import asyncio
import requests
from datetime import datetime, timedelta


def get_schedule():
    session = requests.Session()
    session.get("https://univer.dvfu.ru/schedule")

    date = datetime.now()
    start = date - timedelta((date.weekday() + 1) % 7)
    end = start + timedelta(6)

    response = session.get(
        "https://univer.dvfu.ru/schedule/get",
        params={
            "type": "agendaWeek",
            "start": f"{start.strftime('%Y-%m-%d')}T14:00:00.000Z",
            "end": f"{end.strftime('%Y-%m-%d')}T14:00:00.000Z",
            "groups[]": "6886",
            "ppsGuid": "",
            "facilityId": 0
        },
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Referer": "https://univer.dvfu.ru/schedule",
            "X-Requested-With": "XMLHttpRequest"
        }
    )

    events = response.json().get("events", [])
    days = {}
    for event in events:
        day = event["start"][:10]
        days.setdefault(day, []).append(event)
    return days


async def send_day(query, day_index, bot):
    DAY_NAMES = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    chat_id = query["message"]["chat"]["id"]

    # запускаем синхронный get_schedule в отдельном потоке
    loop = asyncio.get_event_loop()
    days = await loop.run_in_executor(None, get_schedule)

    target = next(
        (d for d in days if datetime.strptime(d, "%Y-%m-%d").weekday() == day_index),
        None
    )
    if not target:
        await bot.send_message(chat_id=chat_id, text=f"В {DAY_NAMES[day_index]} пар нет!")
        return

    dt = datetime.strptime(target, "%Y-%m-%d")
    lines = [f"📅 {DAY_NAMES[dt.weekday()]} {dt.strftime('%d.%m')}"]
    lines.append("-" * 60)
    for e in sorted(days[target], key=lambda x: x["start"]):
        lines.append(f"{e['start'][11:16]}-{e['end'][11:16]} {e['pps_load']}")
        lines.append(f"{e['title']} | {e['classroom']}\n")

    await bot.send_message(chat_id=chat_id, text="\n".join(lines))