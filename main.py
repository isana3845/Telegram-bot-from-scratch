from dotenv import load_dotenv
import os
from base import Bot
from schedule import get_schedule

load_dotenv()

BOT_TOKEN = os.getenv("KEY")
bot = Bot(BOT_TOKEN)


@bot.handlers.command("/start", priority=1000)
def meow(message):
    chat_id = message["chat"]["id"]
    bot.send_message(chat_id, "Я дура")
    bot.send_photo(chat_id, "123.png")


@bot.handlers.command("/meow", priority=100)
def meow(message):
    chat_id = message["chat"]["id"]
    bot.send_message(chat_id, "meow meow meow")


@bot.handlers.command("/schedule", priority=0)
def schedule(message):
    chat_id = message["chat"]["id"]
    bot.send_message(chat_id, get_schedule())


@bot.handlers.on_text(":3", priority=1000)
def uwu(message):
    chat_id = message["chat"]["id"]
    bot.send_message(chat_id, "UwU")


@bot.handlers.on_any()
def bitch(message):
    chat_id = message["chat"]["id"]
    bot.send_message(chat_id, "OWO")
    

bot.get_updates()