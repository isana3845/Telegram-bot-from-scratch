import requests
import asyncio
import json
from typing import Callable, Optional, Dict, Any
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
    

    def get_file(self, message: Dict[str, Any], save_path = ""):
        try:
            photo = message.get("photo", "")
            if photo:
                file_path = requests.get(f"{self.bot}/getFile?file_id={photo[-1]['file_id']}").json()
                if file_path:
                    file_name = file_path['result']['file_path'].split("/")[-1]
                    response = requests.get(f"https://api.telegram.org/file/bot{self.bot_token}/{file_path['result']['file_path']}")
                    with open(f"{save_path}/{file_name}".strip("/"), "wb") as f:
                        f.write(response.content)
                    return response
        except Exception as e:
            return f"Error: {e}"


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


    def send_poll(self, chat_id, question, *args):
          params = {
          "chat_id": chat_id,
          "question": question,
          "options": json.dumps(args)
          }
          
          return self._requests("sendPoll", params)


    def send_message(self, **params):
        if "reply_markup" in params:
              params["reply_markup"] = json.dumps(params["reply_markup"])
        return self._requests("sendMessage", params=params)


    def send_photo(self, chat_id, photo_path):
        url = f"{self.bot}/sendPhoto"
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': chat_id}
            response = requests.post(url, files=files, data=data)
        return response
        

    def proccess_message(self, message):
        try:
              response = self.handlers.handle_message(message["message"])
              return response
        except Exception as e:
              return {"ok": False}
        

    def answer_callback(self, callback_query_id):
        return self._requests("answerCallbackQuery", {"callback_query_id": callback_query_id})
        
            
    def get_updates(self):
        offset = 0

        while True:
              params = {'offset': offset, 'timeout': 10}

              response = requests.get(f"{self.bot}/getUpdates", params=params).json()

              for update in response.get("result", []):
                if "message" in update:
                    self.handlers.handle_message(update["message"])
                elif "callback_query" in update:
                    query = update["callback_query"]
                    self.answer_callback(query["id"])
                    self.handlers.handle_callback(query)

                offset = update["update_id"] + 1