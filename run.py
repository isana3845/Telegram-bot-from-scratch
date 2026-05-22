import os
import json
from dotenv import load_dotenv
import asyncio
from base import Bot
from schedule import Schedule
from keyboard import InlineKeyboard
from datetime import datetime


load_dotenv()


def load_groups():
    if os.path.exists("groups.json"):
        with open("groups.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

GROUPS = load_groups()

schedule = Schedule()

BOT_TOKEN = os.getenv("KEY")
bot = Bot(BOT_TOKEN)

DAY_NAMES = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

# Пользователи, ожидающие ввода группы: {chat_id}
waiting_for_group = set()

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
keyboard.add_button("🔄 Сменить группу", "change_group")


async def send_week(chat_id, offset=0):
    days = schedule.get_schedule(offset=offset)
    if not days:
        await bot.send_message(chat_id=chat_id, text="На этой неделе пар нет!")
        return
    for day in sorted(days):
        dt = datetime.strptime(day, "%Y-%m-%d")
        lines = [f"📅 {DAY_NAMES[dt.weekday()]} {dt.strftime('%d.%m')}"]
        lines.append("-" * 60)
        for e in sorted(days[day], key=lambda x: x["start"]):
            lines.append(f"{e['start'][11:16]}-{e['end'][11:16]} {e.get('pps_load', '')}")
            lines.append(f"{e['title']} | {e.get('classroom', 'Не указано')}\n")
        await bot.send_message(chat_id=chat_id, text="\n".join(lines))
    await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())


async def ask_group(chat_id):
    waiting_for_group.add(chat_id)
    await bot.send_message(
        chat_id=chat_id,
        text="Введи название своей группы, например:\nБ9125-09.03.04руц"
    )


async def handle_group_input(chat_id, text):
    text = text.strip()

    if not GROUPS:
        waiting_for_group.discard(chat_id)
        return

    # Точное совпадение
    if text in GROUPS:
        schedule.change_group(str(GROUPS[text]))
        waiting_for_group.discard(chat_id)
        await bot.send_message(chat_id=chat_id, text=f"✅ Группа установлена: {text}")
        await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())
        return

    # Частичное совпадение
    matches = [name for name in GROUPS if text.lower() in name.lower()]

    if not matches:
        await bot.send_message(chat_id=chat_id, text=f"❌ Группа «{text}» не найдена. Попробуй ещё раз.")
        return  # остаёмся в режиме ожидания

    if len(matches) == 1:
        name = matches[0]
        schedule.change_group(str(GROUPS[name]))
        waiting_for_group.discard(chat_id)
        await bot.send_message(chat_id=chat_id, text=f"✅ Группа установлена: {name}")
        await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())
        return

    if len(matches) > 10:
        await bot.send_message(chat_id=chat_id, text=f"Найдено {len(matches)} групп — уточни запрос.")
        return

    # Несколько совпадений — кнопки выбора
    kb = InlineKeyboard()
    for i, name in enumerate(matches):
        kb.add_button(name, f"setgroup__{GROUPS[name]}__{name}")
        if i % 2 == 1:
            kb.new_row()
    waiting_for_group.discard(chat_id)
    await bot.send_message(chat_id=chat_id, text="Найдено несколько групп:", reply_markup=kb())


@bot.handlers.on_callback("day_0")
async def day_0(query):
    chat_id = query["message"]["chat"]["id"]
    await bot.delete_message(chat_id, query["message"]["message_id"])
    await schedule.send_day(query, 0, bot)
    await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())

@bot.handlers.on_callback("day_1")
async def day_1(query):
    chat_id = query["message"]["chat"]["id"]
    await bot.delete_message(chat_id, query["message"]["message_id"])
    await schedule.send_day(query, 1, bot)
    await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())

@bot.handlers.on_callback("day_2")
async def day_2(query):
    chat_id = query["message"]["chat"]["id"]
    await bot.delete_message(chat_id, query["message"]["message_id"])
    await schedule.send_day(query, 2, bot)
    await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())

@bot.handlers.on_callback("day_3")
async def day_3(query):
    chat_id = query["message"]["chat"]["id"]
    await bot.delete_message(chat_id, query["message"]["message_id"])
    await schedule.send_day(query, 3, bot)
    await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())

@bot.handlers.on_callback("day_4")
async def day_4(query):
    chat_id = query["message"]["chat"]["id"]
    await bot.delete_message(chat_id, query["message"]["message_id"])
    await schedule.send_day(query, 4, bot)
    await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())

@bot.handlers.on_callback("day_5")
async def day_5(query):
    chat_id = query["message"]["chat"]["id"]
    await bot.delete_message(chat_id, query["message"]["message_id"])
    await schedule.send_day(query, 5, bot)
    await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())

@bot.handlers.on_callback("day_all")
async def day_all(query):
    chat_id = query["message"]["chat"]["id"]
    await bot.delete_message(chat_id, query["message"]["message_id"])
    await send_week(chat_id, offset=0)

@bot.handlers.on_callback("n_w")
async def next_week(query):
    chat_id = query["message"]["chat"]["id"]
    await bot.delete_message(chat_id, query["message"]["message_id"])
    await send_week(chat_id, offset=1)

@bot.handlers.on_callback("change_group")
async def change_group_cb(query):
    chat_id = query["message"]["chat"]["id"]
    await bot.delete_message(chat_id, query["message"]["message_id"])
    await ask_group(chat_id)

@bot.handlers.on_callback("setgroup")
async def setgroup_cb(query):
    chat_id = query["message"]["chat"]["id"]
    data = query.get("data", "")
    parts = data.split("__")

    if len(parts) < 3:
        return
    
    group_id = parts[1]
    group_name = parts[2]
    schedule.change_group(group_id)
    await bot.delete_message(chat_id, query["message"]["message_id"])
    await bot.send_message(chat_id=chat_id, text=f"✅ Группа установлена: {group_name}")
    await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())


@bot.handlers.command("/start")
async def start(message):
    chat_id = message["chat"]["id"]
    await bot.send_message(
        chat_id=chat_id,
        text=(
            "Здравствуйте! Вас приветствует персональный помощник!\n"
            "Получить расписание: /schedule\n"
            "Сменить группу: /setgroup"
        )
    )

@bot.handlers.command("/schedule", priority=0)
async def sch(message):
    chat_id = message["chat"]["id"]
    await bot.send_message(chat_id=chat_id, text="Выбери день:", reply_markup=keyboard())

@bot.handlers.command("/setgroup")
async def setgroup_cmd(message):
    chat_id = message["chat"]["id"]
    await ask_group(chat_id)

@bot.handlers.command("/group")
async def gr(message):
    chat_id = message["chat"]["id"]
    group_name = next(
        (name for name, gid in GROUPS.items() if str(gid) == schedule.group),
        schedule.group
    )
    await bot.send_message(
        chat_id=chat_id,
        text=f"Текущая группа: {group_name}",
        reply_markup=keyboard()
    )


@bot.handlers.on_text()
async def text_handler(message):
    chat_id = message["chat"]["id"]
    if chat_id in waiting_for_group:
        await handle_group_input(chat_id, message.get("text", ""))
        return
    await bot.send_message(chat_id=chat_id, text="ничего интересного")

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
    if not GROUPS:
        print("groups.json не найден!")
    await bot.start_session()
    try:
        await bot.get_updates()
    except Exception as e:
        print(f"error: {e}")
        raise
    finally:
        await bot.close_session()

asyncio.run(main())