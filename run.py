from dotenv import load_dotenv
import os
from base import Bot, InlineKeyboard
from main import get_schedule

load_dotenv()

BOT_TOKEN = os.getenv("KEY")

bot = Bot(BOT_TOKEN)

keyboard = InlineKeyboard()
keyboard.add_button("OwO", "Bruh")
keyboard.add_button("UwU", "UwU")
keyboard.add_button("nya", "kkk")

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
    bot.send_message(chat_id=chat_id, text=get_schedule())


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