from typing import Callable, Optional


class Handler:
    def __init__(self):
        self.handlers = []
        self.middlewares = []
    
    def on(self, msg_type: str = 'any', **filters):
        def decorator(func: Callable):
            self.handlers.append({
                'type': msg_type, #тип сообщения, either its command or a photo
                'function': func, #ссылка на исполняемую фнукицию
                'filters': filters, #сюда по идее записываются паттерны, команды и т.д.
                'priority': filters.get('priority', 0) #priority which is given to handler, by dedault it's 0
            })
            self.handlers.sort(key=lambda x: x['priority'], reverse=True) #here wa're sorting by priority 
            return func
        return decorator
    
    def command(self, command: str):
        return self.on('command', command=command) #handler to handle, bruh, commands
    
    def on_text(self, pattern: Optional[str] = None):
        return self.on('text', pattern=pattern) #im not explaining this one
    
    def on_photo(self):
        return self.on('photo') #mhm
    
    def on_any(self):
        return self.on('any') #duh