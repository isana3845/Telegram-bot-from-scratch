import requests
from dotenv import load_dotenv
import os


load_dotenv()

BOT_TOKEN = os.getenv("KEY")

class Bot:
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.bot = f"https://api.telegram.org/bot{self.bot_token}"
        self.handlers = ...
    
    def get(self, method):
        return requests.get(f"{self.bot}/{method}").json()


    def _requests(self, method, params=None):
        url = f'{self.bot}/{method}'

        try:
            if params:
                response = requests.post(url, params=params)
            else:
                response = requests.get(url)
            
            response.raise_for_status()

            return response.json()
        except Exception as e:
            print(f"Error: {e}")


    def send_message(self, chat_id, text):
        params = {
            "chat_id": chat_id,
            "text": text
        }

        return self._requests("sendMessage", params=params)


    def proccess_message(self, message):
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


# bot = Bot(BOT_TOKEN)

# bot.get_updates()