import aiohttp
import asyncio
import json
from typing import Callable, Optional, Dict, Any
from handlers.handlers import AHandler
import os
import certifi
import ssl
from datetime import datetime
from rite_limiter import RateLimiter
import socket

class InlineKeyboard:
    def __init__(self):
        self.rows = [[]]
    

    def add_button(self, text, callback_data = "", url = ""):
        button = {'text': text, "callback_data": callback_data, "url": url}
        self.rows[-1].append(button)

    
    def new_row(self):
        self.rows.append([])


    def __call__(self):
        return {"inline_keyboard": self.rows}


class AsyncBot:
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.bot = f"https://api.telegram.org/bot{self.bot_token}"
        self.handlers = AHandler()
        self.session = None
        self.proxy = "http://127.0.0.1:10808"

    #Метод для логирования данных в JSON файл.
    def _log_action(self, action_type, chat_id, data):
        log_file = "bot_logs.json"
        logs = []
        
        if os.path.exists(log_file):
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except json.JSONDecodeError:
                pass
        
        logs.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": action_type,
            "chat_id": chat_id,
            "data": data
        })
        
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=4)

    async def start_session(self):
        ssl_context = ssl.create_default_context(cafile = certifi.where())

        connector = aiohttp.TCPConnector(
            family = socket.AF_INET,
            ssl = ssl_context,
        )
        timeout = aiohttp.ClientTimeout(total = 300)

        self.session = aiohttp.ClientSession(
            connector = connector,
            timeout = timeout,
            proxy = self.proxy
        )
        print("Сессия запущена с прокси")

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
                    with open(f"{save_path}/{file_name}".strip("/"), "wb") as f:
                        f.write(response)
                    return response
        except Exception as e:
            return f"Error: {e}"

    async def _requests(self, method, json_data):
        if not self.session:
            raise Exception("Сессия не запустилась 0")
        
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
            
            self._log_action("bot_send_poll", chat_id, {"question": question})
            return await self._requests("sendPoll", params)
    
    async def send_message(self, **params): #в aiohttp уже json
        self._log_action("bot_send_message", params.get("chat_id"), {"text": params.get("text")})
        return await self._requests("sendMessage", json_data=params)

    async def send_photo(self, chat_id, photo_path):
        if not self.session:
            raise Exception
        
        url = f"{self.bot}/sendPhoto"
        try:
            with open(photo_path, 'rb') as photo:
                form_data = aiohttp.FormData() #специальный формат для отправки файлов
                form_data.add_field('photo', photo)
                form_data.add_field('chat_id', str(chat_id))

                self._log_action("bot_send_photo", chat_id, {"photo_path": photo_path})
                async with self.session.post(url, data=form_data) as aio:
                    return await aio.json()
                
        except Exception as e:
            print(f"error: {e}")
        

    async def proccess_message(self, message):
        try:
            # Логирование входящего сообщения пользователя
            msg_data = message.get("message", {})
            chat_id = msg_data.get("chat", {}).get("id")
            
            if chat_id:
                text = msg_data.get("text", "<media_or_other>")
                self._log_action("user_message", chat_id, {"text": text})
                
            response = await self.handlers.handle_message(message)

            #лимит
            if response and isinstance(response, dict) and response.get("error") == "rate_limit":
                chat_id = message.get("chat", {}).get("id")
                wait_time = response.get("wait_time", 1)
                await self.send_message(
                    chat_id=chat_id,
                    text=f"Слишком много сообщений. Подождите {wait_time:.1f} секунд."
                )
                return {"ok": False, "rate_limited": True}
            
            return response
        except Exception as e:
            return {"ok": False}
        
            
    async def get_updates(self):
        if not self.session:
            raise Exception("Сессия не запустилась 1")
        
        offset = 0

        while True:
            try:
                params = {'offset': offset, 'timeout': 30}

                async with self.session.get(f"{self.bot}/getUpdates", params=params) as aio:
                    response = await aio.json()
                    

                if response.get("ok") and "result" in response:
                    for update in response["result"]:
                        print(update)
                        if 'message' in update:
                            await self.proccess_message(update['message'])
                        
                        #лимит для кнопок тоже
                        elif 'callback_query' in update:
                            result = await self.handlers.handle_callback(update['callback_query'])

                            if isinstance(result, dict) and result.get("error") == "rate_limit":
                                chat_id = update['callback_query'].get('message', {}).get('chat', {}).get('id')
                                if chat_id:
                                    await self.send_message(
                                        chat_id=chat_id,
                                        text=f"Подождите {result.get('wait_time', 1):.1f} секунд"
                                        )
                
                        offset = update["update_id"] + 1

                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"Ошибка: {e}")
                await asyncio.sleep(5) #чтобы не спамить запросами