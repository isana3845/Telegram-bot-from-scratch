import os
from dotenv import load_dotenv
import asyncio
from base import Bot
from schedule import Schedule
from keyboard import InlineKeyboard
from datetime import datetime

#6885
#6886

g = {
"6886": "РУЦП",
"6885": "ПИ"
}

schedule = Schedule()

BOT_TOKEN = os.getenv("KEY")
print(BOT_TOKEN)
bot = Bot(BOT_TOKEN)

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
keyboard.add_button("📅 Следующая неделя", "n_w")
keyboard.new_row()
keyboard.add_button("РуЦП", "6886")
keyboard.add_button("ПИ", "6885")



@bot.handlers.on_callback("day_0")
async def day_0(query):
    chat_id = query["message"]["chat"]["id"]
    message_id = query["message"]["message_id"]
    await bot.delete_message(chat_id, message_id)
    await schedule.send_day(query, 0, bot)
    await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())

@bot.handlers.on_callback("day_1")
async def day_1(query):
    chat_id = query["message"]["chat"]["id"]
    message_id = query["message"]["message_id"]
    await bot.delete_message(chat_id, message_id)
    await schedule.send_day(query, 1, bot)
    
    await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())

@bot.handlers.on_callback("day_2")
async def day_2(query):
    chat_id = query["message"]["chat"]["id"]
    message_id = query["message"]["message_id"]
    await bot.delete_message(chat_id, message_id)
    await schedule.send_day(query, 2, bot)
    
    await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())

@bot.handlers.on_callback("day_3")
async def day_3(query):
    chat_id = query["message"]["chat"]["id"]
    message_id = query["message"]["message_id"]
    await bot.delete_message(chat_id, message_id)
    await schedule.send_day(query, 3, bot)

    await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())

@bot.handlers.on_callback("day_4")
async def day_4(query):
    chat_id = query["message"]["chat"]["id"]
    message_id = query["message"]["message_id"]
    await bot.delete_message(chat_id, message_id)
    await schedule.send_day(query, 4, bot)

    await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())

@bot.handlers.on_callback("day_5")
async def day_5(query):
    chat_id = query["message"]["chat"]["id"]
    message_id = query["message"]["message_id"]
    await bot.delete_message(chat_id, message_id)
    await schedule.send_day(query, 5, bot)

    await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())

@bot.handlers.on_callback("6885")
async def change(query):
    schedule.change_group("6885")
    
    chat_id = query["message"]["chat"]["id"]
    message_id = query["message"]["message_id"]
    await bot.delete_message(chat_id, message_id)
    
    await bot.send_message(chat_id=chat_id, text="Выбрана новая группа: ПИ")
    await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())

@bot.handlers.on_callback("6886")
async def change(query):
    schedule.change_group("6886")
    
    chat_id = query["message"]["chat"]["id"]
    message_id = query["message"]["message_id"]
    await bot.delete_message(chat_id, message_id)
    
    await bot.send_message(chat_id=chat_id, text="Выбрана новая группа: РуЦП")
    await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())

@bot.handlers.on_callback("day_all")
async def day_all(query):
    chat_id = query["message"]["chat"]["id"]
    message_id = query["message"]["message_id"]
    await bot.delete_message(chat_id, message_id)
    
    days = schedule.get_schedule()
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
    await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())

@bot.handlers.on_callback("n_w")
async def day_all(query):
    chat_id = query["message"]["chat"]["id"]
    message_id = query["message"]["message_id"]
    await bot.delete_message(chat_id, message_id)
    
    days = schedule.get_schedule(offset=1)
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
    await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())



@bot.handlers.command("/start")
async def meow(message):
    chat_id = message["chat"]["id"]
    await bot.send_message(chat_id=chat_id, text="Здравствуйте! Вас приветствует персональный помощник!\nВы можете получить расписание по команде /schedule/nУзнать текущую группу: /group")


@bot.handlers.command("/schedule", priority=0)
async def sch(message):
    chat_id = message["chat"]["id"]
    await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())

@bot.handlers.command("/group")
async def gr(message):
      chat_id = message["chat"]["id"]
      await bot.send_message(chat_id=chat_id, text=f"Ваша текущая группа {g[schedule.group]}!\nГотовы узнать свое расписание?", reply_markup=keyboard())

@bot.handlers.on_photo()
async def give(message):
    chat_id = message["chat"]["id"]
    await bot.send_message(chat_id=chat_id, text="Краду твою картиночку")
    await bot.get_file(message)


@bot.handlers.on_any()
async def bbbb(message):
    chat_id = message["chat"]["id"]
    await bot.send_message(chat_id=chat_id, text="ничего интересного")


async def main():
    await bot.start_session()
    try:
        await bot.get_updates()
    except Exception as e:
        raise e
        print(f"error: {e}")
    finally:
        await bot.close_session()

asyncio.run(main())