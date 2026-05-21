from typing import Callable, Optional, Dict, Any
import asyncio


class AHandler:
    def __init__(self):
        self.handlers = []
        self.rate_limiter = None

    def set_rate_limiter(self, rate_limiter):
        self.rate_limiter = rate_limiter
    
    def on(self, msg_type: str = 'any', **filters):
        def decorator(func: Callable):
            self.handlers.append(
                {
                'type': msg_type,
                'function': func,
                'filters': filters,
                'priority': filters.get('priority', 0)
            })
            self.handlers.sort(key=lambda x: x['priority'], reverse=True)

            return func
        return decorator
    
    def command(self, command: str, priority: str = 0):
        return self.on('command', command=command, priority=priority)
    
    def on_text(self, pattern: Optional[str] = None, priority: str = 0):
        return self.on('text', pattern=pattern, priority=priority)
    
    def on_photo(self):
        return self.on('photo')
    
    def on_any(self):
        return self.on('any')
    
    def on_callback(self, data: str, priority: str = 0):
        return self.on('callback', data=data, priority=priority)
    
    async def handle_callback(self, query: Dict[str, Any]):
        data = query.get("data", "")
        user_id = query.get("from", {}).get("id", 0)

        if self.rate_limiter and not self.rate_limiter.can_send(user_id):
            wait_time = self.rate_limiter.get_wait_time(user_id)
            return {"error": "rate_limit", "wait_time": wait_time, "type": "callback"}

        for handler in self.handlers:
            if handler['type'] == 'callback' and handler['filters'].get('data') == data:
                return await handler['function'](query)           
    
    
    async def handle_message(self, message: Dict[str, Any]):
        user_id = message.get('from', {}).get('id', 0)

        if self.rate_limiter and not self.rate_limiter.can_send(user_id):
            wait_time = self.rate_limiter.get_wait_time(user_id)
            return {"error": "rate_limit", "wait_time": wait_time}
    
        text = message.get('text', '')
        is_command = text.startswith('/') if text else False
        command_name = text[1:].split()[0] if is_command else None
        
        print(f"\ntext='{text}', is_command={is_command}, command='{command_name}'")
        print(f"Доступно обработчиков: {len(self.handlers)}")
        
        for i, handler in enumerate(self.handlers):
            handler_type = handler['type']
            filters = handler['filters']
            
            print(f"  [{i}] Проверяем {handler_type} с фильтрами {filters}")
            
            # Проверка типа обработчика
            if handler_type == 'callback':
                continue
            
            if handler_type == 'command':
                if not is_command:
                    print(f"Не команда")
                    continue
                    
                expected = filters.get('command', '')
                if expected.startswith('/'):
                    expected = expected[1:]
                
                if command_name != expected:
                    print(f"Команда {command_name} != {expected}")
                    continue
                    
                print(f"Команда подходит!")
                
            elif handler_type == 'text':
                if is_command:
                    print(f"Это команда, а не текст")
                    continue
                    
                pattern = filters.get('pattern')
                if pattern and pattern not in text:
                    print(f"Паттерн '{pattern}' не найден в '{text}'")
                    continue
                    
                print(f"Текст подходит!")
                
            elif handler_type == 'photo':
                if 'photo' not in message:
                    print(f"Нет фото")
                    continue
                print(f"Есть фото!")
                
            elif handler_type == 'any':
                print(f"Подходит любой тип")
            
            # Если дошли сюда - обработчик подходит
            print(f"{handler['function'].__name__}")
            return await handler['function'](message)
        
        print("Ни один обработчик не подошел")
        return None