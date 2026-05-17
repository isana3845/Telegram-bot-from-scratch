from dotenv import load_dotenv
import os
from base import Bot
from schedule import get_schedule, get_schedule_raw
from keyboard import InlineKeyboard
from datetime import datetime

load_dotenv()

BOT_TOKEN = os.getenv("KEY")
print(BOT_TOKEN)
bot = Bot(BOT_TOKEN)

DAY_NAMES = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

keyboard = InlineKeyboard()
for i in range(4):
    keyboard.add_button(DAY_NAMES[i], f"day_{i}")
keyboard.new_row()
keyboard.add_button(DAY_NAMES[4], "day_4")
keyboard.add_button(DAY_NAMES[5], "day_5")
keyboard.add_button("📅 Вся неделя", "day_all")


def send_day(query, day_index):
    chat_id = query["message"]["chat"]["id"]
    days = get_schedule_raw()
    target = next(
        (d for d in days if datetime.strptime(d, "%Y-%m-%d").weekday() == day_index),
        None
    )
    if not target:
        bot.send_message(chat_id=chat_id, text=f"В {DAY_NAMES[day_index]} пар нет!")
        return
    
    dt = datetime.strptime(target, "%Y-%m-%d")
    lines = [f"📅 {DAY_NAMES[dt.weekday()]} {dt.strftime('%d.%m')}"]
    for e in sorted(days[target], key=lambda x: x["start"]):
        lines.append(f"{e['start'][11:16]}-{e['end'][11:16]} {e['pps_load']}")
        lines.append(f"{e['title']} | {e['classroom']}")
        
    bot.send_message(chat_id=chat_id, text="\n".join(lines))


@bot.handlers.on_callback("day_0")
def day_0(query): send_day(query, 0)

@bot.handlers.on_callback("day_1")
def day_1(query): send_day(query, 1)

@bot.handlers.on_callback("day_2")
def day_2(query): send_day(query, 2)

@bot.handlers.on_callback("day_3")
def day_3(query): send_day(query, 3)

@bot.handlers.on_callback("day_4")
def day_4(query): send_day(query, 4)

@bot.handlers.on_callback("day_5")
def day_5(query): send_day(query, 5)


@bot.handlers.on_callback("day_all")
def day_all(query):
    chat_id = query["message"]["chat"]["id"]
    days = get_schedule_raw()
    if not days:
        bot.send_message(chat_id=chat_id, text="На этой неделе пар нет!")
        return
    for day in sorted(days):
        dt = datetime.strptime(day, "%Y-%m-%d")
        lines = [f"📅 {DAY_NAMES[dt.weekday()]} {dt.strftime('%d.%m')}"]
        for e in sorted(days[day], key=lambda x: x["start"]):
            lines.append(f"{e['start'][11:16]}-{e['end'][11:16]} {e['pps_load']}")
            lines.append(f"{e['title']} | {e['classroom']}")
        bot.send_message(chat_id=chat_id, text="\n".join(lines))


@bot.handlers.command("/start")
def meow(message):
    chat_id = message["chat"]["id"]
    bot.send_message(chat_id=chat_id, text="Я дура\nкоманды:\n/meow\n/schedule\n на :3 отвечает UwU, а на любое сообщение будет отвечать OWO")
    bot.send_photo(chat_id, "123.png")


@bot.handlers.command("/meow", priority=100)
def meow(message):
    chat_id = message["chat"]["id"]
    bot.send_message(chat_id=chat_id, text="meow meow meow", reply_markup=keyboard())


@bot.handlers.command("/schedule", priority=0)
def schedule(message):
    chat_id = message["chat"]["id"]
    bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())


@bot.handlers.on_text(":3", priority=1000)
def uwu(message):
    chat_id = message["chat"]["id"]
    bot.send_message(chat_id=chat_id, text="UwU")


@bot.handlers.on_text("bruh", priority=1000)
def owo(message):
    chat_id = message["chat"]["id"]
    bot.send_poll(chat_id, "Вы тупой?", "Да", "Конечно")


@bot.handlers.on_photo()
def give(message):
    chat_id = message["chat"]["id"]
    bot.send_message(chat_id=chat_id, text="Краду твою кариночку")
    bot.get_file(message)


@bot.handlers.on_any()
def bbbb(message):
    chat_id = message["chat"]["id"]
    bot.send_message(chat_id=chat_id, text="OWO")

bot.get_updates()