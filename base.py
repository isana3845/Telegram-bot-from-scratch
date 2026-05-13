import requests
from dotenv import load_dotenv
from handlers.handlers import Handler
import os


class Bot:
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.bot = f"https://api.telegram.org/bot{self.bot_token}"
        self.handlers = Handler()
    
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

    def send_photo(self, chat_id, photo_path):
        url = f"{self.bot}/sendPhoto"
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': chat_id}
            response = requests.post(url, files=files, data=data)
        return response
        

    def proccess_message(self, message):
        response = self.handlers.handle_message(message)
        print(response)
        return response
        
            
    def get_updates(self):
        offset = 0

        while True:
            try:
                params = {'offset': offset, 'timeout': 30}

                response = requests.get(f"{self.bot}/getUpdates", params=params).json()

                if response["result"]:
                    for update in response["result"]:
                        print(update)
                        self.proccess_message(update['message'])
                
                        offset = update["update_id"] + 1
                
            except Exception as e:
                print(f"Ошибка: {e}")