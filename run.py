from dotenv import load_dotenv
import os
from AsynсBot import AsyncBot, InlineKeyboard
import asyncio
from datetime import datetime
from schedule import get_schedule, get_schedule_raw

load_dotenv()

BOT_TOKEN = os.getenv("KEY")

bot = AsyncBot(BOT_TOKEN)

DAY_NAMES = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

keyboard = InlineKeyboard()
for i in range(4):
    keyboard.add_button(DAY_NAMES[i], f"day_{i}")
    if i == 2:
        keyboard.new_row()
keyboard.add_button("OwO", "Bruh")
keyboard.add_button("UwU", "UwU")
keyboard.add_button("nya", "kkk")

async def send_day(query, day_index):
    chat_id = query["message"]["chat"]["id"]
    days = await get_schedule_raw()
    target = next(
        (d for d in days if datetime.strptime(d, "%Y-%m-%d").weekday() == day_index),
        None
    )
    if not target:
        await bot.send_message(chat_id=chat_id, text=f"В {DAY_NAMES[day_index]} пар нет!")
        return
    
    dt = datetime.strptime(target, "%Y-%m-%d")
    lines = [f"📅 {DAY_NAMES[dt.weekday()]} {dt.strftime('%d.%m')}"]
    for e in sorted(days[target], key=lambda x: x["start"]):
        lines.append(f"{e['start'][11:16]}-{e['end'][11:16]} {e['pps_load']}")
        lines.append(f"{e['title']} | {e['classroom']}")
        
    await bot.send_message(chat_id=chat_id, text="\n".join(lines))


@bot.handlers.on_callback("day_0")
async def day_0(query):
    await send_day(query, 0)

@bot.handlers.on_callback("day_1")
async def day_1(query):
    await send_day(query, 1)

@bot.handlers.on_callback("day_2")
async def day_2(query):
    await send_day(query, 2)

@bot.handlers.on_callback("day_3")
async def day_3(query):
    await send_day(query, 3)

@bot.handlers.on_callback("day_4")
async def day_4(query):
    await send_day(query, 4)

@bot.handlers.on_callback("day_5")
async def day_5(query):
    await send_day(query, 5)


@bot.handlers.on_callback("day_all")
async def day_all(query):
    chat_id = query["message"]["chat"]["id"]
    days = await get_schedule_raw()
    if not days:
        await bot.send_message(chat_id=chat_id, text="На этой неделе пар нет!")
        return
    for day in sorted(days):
        dt = datetime.strptime(day, "%Y-%m-%d")
        lines = [f"📅 {DAY_NAMES[dt.weekday()]} {dt.strftime('%d.%m')}"]
        for e in sorted(days[day], key=lambda x: x["start"]):
            lines.append(f"{e['start'][11:16]}-{e['end'][11:16]} {e['pps_load']}")
            lines.append(f"{e['title']} | {e['classroom']}")
        await bot.send_message(chat_id=chat_id, text="\n".join(lines))



@bot.handlers.command("/start")
async def meow(message):
    chat_id = message["chat"]["id"]
    await bot.send_message(chat_id, "Я дура\nкоманды:\n   /meow\n/schedule\n на :3 отвечает UwU, а на любое сообщение будет отвечать OWO")
    #bot.send_photo(chat_id, "123.png")


@bot.handlers.command("/meow", priority=100)
async def meo(message):
    chat_id = message["chat"]["id"]
    await bot.send_message(chat_id, "meow meow meow", reply_markup=keyboard())


@bot.handlers.command("/schedule", priority=0)
async def schedule(message):
    chat_id = message["chat"]["id"]
    text = await get_schedule()
    await bot.send_message(chat_id=chat_id, text=text)


@bot.handlers.on_text(":3", priority=1000)
async def uwu(message):
    chat_id = message["chat"]["id"]
    await bot.send_message(chat_id=chat_id, text="UwU")

@bot.handlers.on_text("bruh", priority=1000)
async def owo(message):
    chat_id = message["chat"]["id"]
    await bot.send_poll(chat_id, "Вы тупой?", "Да", "Конечно")


@bot.handlers.on_photo()
async def give(message):
    chat_id = message["chat"]["id"]
    await bot.send_message(chat_id=chat_id, text="Краду твою кариночку")
    await bot.get_file(message)


@bot.handlers.on_any()
async def bbbb(message):
    chat_id = message["chat"]["id"]
    await bot.send_message(chat_id=chat_id, text="OWO")

# await bot.get_updates()
async def main():
    await bot.start_session()
    try:
        await bot.get_updates()
    except Exception as e:
        print(f"error: {e}")
    finally:
        await bot.close_session()

asyncio.run(main())