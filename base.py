import requests
import aiohttp
import asyncio
import json
from typing import Callable, Optional, Dict, Any

from handlers.handlers import Handler
import os


class Bot:
    def init(self, bot_token):
        self.bot_token = bot_token
        self.bot = f"https://api.telegram.org/bot{self.bot_token}"
        self.handlers = Handler()
        self.session = None
    
    
    async def start_session(self):
        self.session = aiohttp.ClientSession()

    async def close_session(self):
        if self.session:
            await self.session.close()

    async def get_file(self, message: Dict[str, Any], save_path = ""):
        try:
            photo = message.get("photo", "")

            if photo: 
                #информация о фото
                async with self.session.get(f"{self.bot}/getFile?file_id={photo[-1]['file_id']}") as aio:
                    file_path = await aio.json()
                
                if file_path:
                    file_name = file_path['result']['file_path'].split("/")[-1]
                    async with self.session.get(f"https://api.telegram.org/file/bot{self.bot_token}/{file_path['result']['file_path']}") as aii:
                        response = await aii.read()
                    # response = requests.get(f"https://api.telegram.org/file/bot{self.bot_token}/{file_path['result']['file_path']}")
                    with open(f"{save_path}/{file_name}".strip("/"), "wb") as f:
                        f.write(response)
                    return response
        except Exception as e:
            return f"Error: {e}"
    async def delete_message(self, chat_id, message_id):
            params = {
            "chat_id": chat_id,
            "message_id": message_id
        }

            return await self._requests("deleteMessage", params)
    async def _requests(self, method, json_data):
        if not self.session:
            raise Exception
        
        url = f'{self.bot}/{method}'

        try:
            if json_data:
                async with self.session.post(url, json=json_data) as asi:
                    asi.raise_for_status()
                    return await asi.json()
            else:
                async with self.session.get(url) as asi:
                    asi.raise_for_status()
                    return await asi.json()
            
        except Exception as e:
            print(f"error: {e}")

    async def send_poll(self, chat_id, question, *args):
            params = {
            "chat_id": chat_id,
            "question": question,
            "options": list(args)
            }
            
            return await self._requests("sendPoll", params)
    
    async def send_message(self, **params): #в aiohttp уже json
        return await self._requests("sendMessage", json_data=params)
    
    # async def send_message(self, chat_id, text):
    #     data = {
    #         "chat_id": chat_id,
    #         "text": text
    #     }

    #     return await self._aiohttp("sendMessage", json_data=data)

    async def send_photo(self, chat_id, photo_path):
        if not self.session:
            raise Exception
        
        url = f"{self.bot}/sendPhoto"
        try:
            with open(photo_path, 'rb') as photo:
                form_data = aiohttp.FormData() #специальный формат для отправки файлов
                form_data.add_field('photo', photo)
                form_data.add_field('chat_id', str(chat_id))

                async with self.session.post(url, data=form_data) as aio:
                    return await aio.json()
                
        except Exception as e:
            print(f"error: {e}")
        

    async def proccess_message(self, message):
        try:
            response = await self.handlers.handle_message(message)
            return response
        except Exception as e:
            return {"ok": False}
        
            
    async def get_updates(self):
        if not self.session:
            raise Exception
        
        offset = 0
        while True:
            try:
                params = {'offset': offset, 'timeout': 10}
                async with self.session.get(f"{self.bot}/getUpdates", params=params) as aio:
                    response = await aio.json()
                if response["result"]:
                    for update in response["result"]:
                        print(update)

                        if 'callback_query' in update:
                            await self.handlers.handle_callback(update['callback_query'])
                        elif 'message' in update:
                            await self.proccess_message(update['message'])

                        offset = update["update_id"] + 1
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(5)