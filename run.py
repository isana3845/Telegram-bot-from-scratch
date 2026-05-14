from dotenv import load_dotenv
import os
from base import AsyncBot
import asyncio
from main import get_schedule

load_dotenv()

BOT_TOKEN = os.getenv("KEY")

bot = AsyncBot(BOT_TOKEN)


@bot.handlers.command("/start")
async def meow(message):
    chat_id = message["chat"]["id"]
    await bot.send_message(chat_id, "Я дура\nкоманды:\n   /meow\n/schedule\n на :3 отвечает UwU, а на любое сообщение будет отвечать OWO")
    #bot.send_photo(chat_id, "123.png")


@bot.handlers.command("/meow", priority=100)
async def meow(message):
    chat_id = message["chat"]["id"]
    await bot.send_message(chat_id, "meow meow meow")


@bot.handlers.command("/schedule", priority=0)
async def schedule(message):
    chat_id = message["chat"]["id"]

    schedule = await asyncio.to_thread(get_schedule)

    await bot.send_message(chat_id, schedule)


@bot.handlers.on_text(":3", priority=1000)
async def uwu(message):
    chat_id = message["chat"]["id"]
    await bot.send_message(chat_id, "UwU")


@bot.handlers.on_photo()
async def give(message):
    chat_id = message["chat"]["id"]
    await bot.send_message(chat_id, "Краду твою кариночку")
    await bot.get_file(message)


@bot.handlers.on_any()
async def bbbb(message):
    chat_id = message["chat"]["id"]
    await bot.send_message(chat_id, "OWO")

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