import requests
from datetime import datetime, timedelta
import json
import asyncio
import os



class Schedule:
    def init(self, group = "6886"):
          self.group = group
          
    def change_group(self, group):
          self.group = group
     
    def fetch_from_site(self, offset):
        """Внутренняя функция для отправки запроса на сайт ДВФУ."""
        session = requests.Session()
        session.get("https://univer.dvfu.ru/schedule")


        date = datetime.now()
        date_with_offset = date + timedelta(weeks=offset)  # Добавляем смещение недель
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
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json",
                "Referer": "https://univer.dvfu.ru/schedule",
                "X-Requested-With": "XMLHttpRequest"
            }
        )
        return response.json().get("events", [])

    def get_schedule(self, offset=0):
        today_str = datetime.now().strftime("%Y-%m-%d")
        events = []
        
        if os.path.exists(f"schedule_cache{self.group}.json"):
            try:
                with open(f"schedule_cache{self.group}.json", "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                # Проверяем кэш с учетом offset
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
                    "offset": offset,  # Сохраняем offset в кэш
                    "events": events
                }
                with open(f"schedule_cache{self.group}.json", "w", encoding="utf-8") as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=4)
                print("Расписание успешно обновлено с сайта и сохранено в кэш.")
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
        message_id = query.get("message", {}).get("message_id")

        callback_data = query.get("data", "")
        
        group = "6886"  # Значение по умолчанию
        if callback_data in ["6885", "6886"]:
            group = callback_data
        

        offset = query.get("offset", 0)  # Если offset передан в query
        if callback_data == "n_w":
            offset = query.get("offset", 0) + 1  # Увеличиваем offset на следующую неделю
            group = query.get("group", "6886")  # Сохраняем группу

        # Запускаем синхронный get_schedule в отдельном потоке
        loop = asyncio.get_event_loop()
        days = await loop.run_in_executor(None, self.get_schedule, offset)
        if not days:
            await bot.send_message(
                chat_id=chat_id, 
                text="❌ Не удалось загрузить расписание. Попробуйте позже."
            )
            return

        # Ищем нужный день
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
                text=f"📭 В {DAY_NAMES[day_index]} пар нет!"
            )
            return

        # Форматируем расписание
        dt = datetime.strptime(target, "%Y-%m-%d")
        lines = [f"📅 {DAY_NAMES[dt.weekday()]} {dt.strftime('%d.%m')}"]
        if offset != 0:  # Показываем offset если не текущая неделя
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
                await bot.send_message(
                    chat_id=chat_id, 
                    text=message_text[i:i+4096]
                )
        else:
            await bot.send_message(chat_id=chat_id, text=message_text)