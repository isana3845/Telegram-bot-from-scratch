import requests
from datetime import datetime, timedelta
import json
import os

CACHE_FILE = "schedule_cache.json"

def fetch_from_site():
    """Внутренняя функция для отправки запроса на сайт ДВФУ."""
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
    return response.json().get("events", [])

def get_schedule():
    today_str = datetime.now().strftime("%Y-%m-%d")
    events = []
    
    # Пытаемся загрузить данные из кэша
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
                # Если кэш создан сегодня, используем его
                if cache_data.get("cache_date") == today_str:
                    events = cache_data.get("events", [])
                    print("Расписание загружено из локального кэша.")
        except Exception as e:
            print(f"Ошибка чтения кэша: {e}")

    # Если кэш пустой или устарел, качаем заново и обновляем файл
    if not events:
        try:
            events = fetch_from_site()
            cache_data = {
                "cache_date": today_str,
                "events": events
            }
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=4)
            print("Расписание успешно обновлено с сайта и сохранено в кэш.")
        except Exception as e:
            print(f"Ошибка при запросе к сайту: {e}")
            return "Не удалось получить расписание (ошибка сети)."

    # Дальнейшая обработка и форматирование текста (осталась без изменений)
    days = {}
    for event in events:
        day = event["start"][:10]
        days.setdefault(day, []).append(event)

    day_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    lines = []
    for day in sorted(days):
        dt = datetime.strptime(day, "%Y-%m-%d")
        lines.append(f"📅 {day_names[dt.weekday()]} {dt.strftime('%d.%m')}")
        lines.append("-" * 70)

        for e in sorted(days[day], key=lambda x: x["start"]):
            lines.append(f"  {e['start'][11:16]}-{e['end'][11:16]} {e['pps_load']}")
            lines.append(f"  {e['title']} | {e['classroom']}\n")
        lines.append("\n\n")

    return "\n".join(lines)
