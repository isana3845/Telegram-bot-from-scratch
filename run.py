from dotenv import load_dotenv
import os
import asyncio
from base import Bot
from schedule import get_schedule, send_day
from keyboard import InlineKeyboard
from datetime import datetime
from rate_limiter import RateLimiter

load_dotenv()

BOT_TOKEN = os.getenv("KEY")
print(BOT_TOKEN)
bot = Bot(BOT_TOKEN)

rate_limiter = RateLimiter(max_messages=3, time_window=5.0)
bot.handlers.set_rate_limiter(rate_limiter)

DAY_NAMES = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

keyboard = InlineKeyboard()
for i in range(4):
    keyboard.add_button(DAY_NAMES[i], f"day_{i}")
    if i == 2:
        keyboard.new_row()
keyboard.add_button(DAY_NAMES[4], "day_4")
keyboard.add_button(DAY_NAMES[5], "day_5")
keyboard.new_row()
keyboard.add_button("📅 Вся неделя", "day_all")


@bot.handlers.on_callback("day_0")
async def day_0(query):
    await send_day(query, 0, bot)

@bot.handlers.on_callback("day_1")
async def day_1(query):
    await send_day(query, 1, bot)

@bot.handlers.on_callback("day_2")
async def day_2(query):
    await send_day(query, 2, bot)

@bot.handlers.on_callback("day_3")
async def day_3(query):
    await send_day(query, 3, bot)

@bot.handlers.on_callback("day_4")
async def day_4(query):
    await send_day(query, 4, bot)

@bot.handlers.on_callback("day_5")
async def day_5(query):
    await send_day(query, 5, bot)


@bot.handlers.on_callback("day_all")
async def day_all(query):
    chat_id = query["message"]["chat"]["id"]
    days = get_schedule()
    if not days:
        await bot.send_message(chat_id=chat_id, text="На этой неделе пар нет!")
        return
    for day in sorted(days):
        dt = datetime.strptime(day, "%Y-%m-%d")
        lines = [f"📅 {DAY_NAMES[dt.weekday()]} {dt.strftime('%d.%m')}"]
        lines.append("-" * 60)
        for e in sorted(days[day], key=lambda x: x["start"]):
            lines.append(f"{e['start'][11:16]}-{e['end'][11:16]} {e['pps_load']}")
            lines.append(f"{e['title']} | {e['classroom']}\n")
        await bot.send_message(chat_id=chat_id, text="\n".join(lines))


@bot.handlers.command("/start")
async def meow(message):
    chat_id = message["chat"]["id"]
    await bot.send_message(chat_id=chat_id, text="Я дура\nкоманды:\n/meow\n/schedule\n на :3 отвечает UwU, а на любое сообщение будет отвечать OWO")


@bot.handlers.command("/meow", priority=100)
async def meow(message):
    chat_id = message["chat"]["id"]
    await bot.send_message(chat_id=chat_id, text="meow meow meow")


@bot.handlers.command("/schedule", priority=0)
async def schedule(message):
    chat_id = message["chat"]["id"]
    await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())


@bot.handlers.on_text(":3", priority=1000)
async def uwu(message):
    chat_id = message["chat"]["id"]
    await bot.send_message(chat_id=chat_id, text="UwU")


@bot.handlers.on_text("bruh", priority=1000)
async def owo(message):
    chat_id = message["chat"]["id"]
    await bot.send_poll(chat_id, "Вы крутой?", "Да", "Конечно")


@bot.handlers.on_photo()
async def give(message):
    chat_id = message["chat"]["id"]
    await bot.send_message(chat_id=chat_id, text="Краду твою картиночку")
    await bot.get_file(message)


@bot.handlers.on_any()
async def bbbb(message):
    chat_id = message["chat"]["id"]
    await bot.send_message(chat_id=chat_id, text="OWO")


async def main():
    await bot.start_session()
    try:
        await bot.get_updates()
    except Exception as e:
        print(f"error: {e}")
    finally:
        await bot.close_session()

asyncio.run(main())