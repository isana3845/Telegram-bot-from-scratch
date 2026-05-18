import requests
from datetime import datetime, timedelta


def get_schedule_raw():
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

    day_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    lines = []
    for day in sorted(days):
        dt = datetime.strptime(day, "%Y-%m-%d")
        lines.append(f"📅 {day_names[dt.weekday()]} {dt.strftime('%d.%m')}")
        lines.append("-" * 60)

        for e in sorted(days[day], key=lambda x: x["start"]):
            lines.append(f"  {e['start'][11:16]}-{e['end'][11:16]} {e['pps_load']}")
            lines.append(f"  {e['title']} | {e['classroom']}\n")
        lines.append("\n\n")

    return days


print(get_schedule_raw())