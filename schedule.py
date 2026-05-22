import requests
from datetime import datetime, timedelta
import json
import asyncio
import os


class Schedule:
    def __init__(self, group="6886"):
        self.group = group


    def change_group(self, group):
        self.group = group


    def _parse_cookies(self, cookie_string):
        cookies = {}
        for part in cookie_string.split(";"):
            part = part.strip()
            if "=" in part:
                key, _, value = part.partition("=")
                cookies[key.strip()] = value.strip()
        return cookies


    def fetch_from_site(self, offset):
        cookie_string = os.getenv("DVFU_COOKIES", "")
        csrf_token = os.getenv("DVFU_CSRF", "")

        session = requests.Session()
        session.cookies.update(self._parse_cookies(cookie_string))

        date = datetime.now()
        date_with_offset = date + timedelta(weeks=offset)
        start = date_with_offset - timedelta((date_with_offset.weekday() + 1) % 7)
        end = start + timedelta(6)

        response = session.get(
            "https://univer.dvfu.ru/schedule/get",
            params={
                "type": "agendaWeek",
                "start": f"{start.strftime('%Y-%m-%d')}T14:00:00.000Z",
                "end": f"{end.strftime('%Y-%m-%d')}T14:00:00.000Z",
                "groups[]": self.group,
                "ppsGuid": "",
                "facilityId": 0
            },
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Referer": "https://univer.dvfu.ru/schedule",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRF-Token": csrf_token,
            }
        )

        if response.status_code == 401 or response.status_code == 403:
            raise PermissionError("Куки устарели!")

        return response.json().get("events", [])


    def get_schedule(self, offset=0):
        today_str = datetime.now().strftime("%Y-%m-%d")
        events = []

        cache_file = f"schedule_cache{self.group}.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                if cache_data.get("cache_date") == today_str and cache_data.get("offset") == offset:
                    events = cache_data.get("events", [])
                    print("Расписание загружено из локального кэша.")
            except Exception as e:
                print(f"Ошибка чтения кэша: {e}")

        if not events:
            try:
                events = self.fetch_from_site(offset)
                cache_data = {
                    "cache_date": today_str,
                    "offset": offset,
                    "events": events
                }
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=4)
                print("Расписание успешно обновлено с сайта и сохранено в кэш.")
            except PermissionError as e:
                raise  # пробрасываем выше, чтобы бот мог уведомить
            except Exception as e:
                print(f"Ошибка при запросе к сайту: {e}")
                return {}

        days = {}
        for event in events:
            day = event["start"][:10]
            days.setdefault(day, []).append(event)
        return days


    async def send_day(self, query, day_index, bot):
        DAY_NAMES = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        chat_id = query["message"]["chat"]["id"]

        offset = query.get("offset", 0)

        loop = asyncio.get_event_loop()
        days = await loop.run_in_executor(None, self.get_schedule, offset)

        if not days:
            await bot.send_message(
                chat_id=chat_id,
                text="❌ Не удалось загрузить расписание. Попробуйте позже."
            )
            return

        target = None
        for d in days.keys():
            try:
                if datetime.strptime(d, "%Y-%m-%d").weekday() == day_index:
                    target = d
                    break
            except ValueError as e:
                print(f"Ошибка парсинга даты {d}: {e}")
                continue

        if not target:
            await bot.send_message(
                chat_id=chat_id,
                text=f"В {DAY_NAMES[day_index]} пар нет!"
            )
            return

        dt = datetime.strptime(target, "%Y-%m-%d")
        lines = [f"📅 {DAY_NAMES[dt.weekday()]} {dt.strftime('%d.%m')}"]
        if offset != 0:
            lines.append(f"📆 Неделя {offset:+d}")
        lines.append("-" * 60)

        for e in sorted(days[target], key=lambda x: x["start"]):
            start_time = e['start'][11:16]
            end_time = e['end'][11:16]
            subject = e.get('title', 'Без названия')
            classroom = e.get('classroom', 'Не указано')
            load = e.get('pps_load', '')

            lines.append(f"{start_time}-{end_time} {load}")
            lines.append(f"{subject} | {classroom}\n")

        message_text = "\n".join(lines)
        if len(message_text) > 4096:
            for i in range(0, len(message_text), 4096):
                await bot.send_message(chat_id=chat_id, text=message_text[i:i + 4096])
        else:
            await bot.send_message(chat_id=chat_id, text=message_text)