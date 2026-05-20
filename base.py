import requests
from dotenv import load_dotenv
import os
import json
from rate_limiter import RateLimiter

load_dotenv()

BOT_TOKEN = os.getenv("KEY")

class Bot:
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.bot = f"https://api.telegram.org/bot{self.bot_token}"
    
    def get(self, method):
        return requests.get(f"{self.bot}/{method}").json()

    def _requests(self, method, params):
        url = f'{self.bot}/{method}'

        try:
            if params:
                response = requests.post(url, params=params)
            else:
                response = requests.get(url)
            
            response.raise_for_status()

            return response.json()
        except Exception as e:
            print(f"error: {e}")


    def send_message(self, chat_id, text):
        params = {
            "chat_id": chat_id,
            "text": text
        }

        return self._requests("sendMessage", params=params)

    async def proccess_message(self, message):
        try:
            response = await self.handlers.handle_message(message)

            if response and isinstance(response, dict) and response.get("error") == "rate_limit":
                chat_id = message.get("chat", {}).get("id")
                wait_time = response.get("wait_time", 1)
                await self.send_message(
                    chat_id=chat_id,
                    text=f"⏰ Слишком много сообщений! Подождите {wait_time:.1f} секунд."
                )
                return {"ok": False, "rate_limited": True}

            return response
        except Exception as e:
            print(f"Error in process_message: {e}")
            return {"ok": False}


    def proccess_message(self, message):
        if "прив" in message["message"]["text"]:
            chat_id = message["message"]["chat"]["id"]

            self.send_message(chat_id, "UwU")
        else:
            print(message)

    
    def get_updates(self):
        offset = 0

        while True:
            try:
                params = {'offset': offset, 'timeout': 30}

                response = requests.get(f"{self.bot}/getUpdates", params=params).json()

                if response["result"]:
                    for update in response["result"]:
                        self.proccess_message(update)
                
                        offset = update["update_id"] + 1
                
            except Exception as e:
                print(f"Ошибка: {e}")


bot = Bot(BOT_TOKEN)

bot.get_updates()