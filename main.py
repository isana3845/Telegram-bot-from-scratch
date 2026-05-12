from base import Bot
from schedule import get_schedule
from dotenv import load_dotenv
import os


load_dotenv()

bot = Bot(os.getenv("KEY"))


@bot.command("start")
def start(chat_id):
    bot.send_message(chat_id, "Message") 


@bot.command("schedule")
def schedule(chat_id):
    bot.send_message(chat_id, get_schedule())


bot.get_updates()