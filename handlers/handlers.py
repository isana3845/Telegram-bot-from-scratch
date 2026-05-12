from typing import Callable, Optional
import re


class Handler:
    def __init__(self):
        self.handlers = {
            'text': [],
            'command': [],
            'callback': [],
            'photo': [],
            'video': [],
            'document': [],
            'any': []
        }
        self.middlewares = []
    

    def command(self, command):
        def decorator(func):
            self.handlers['command'].append({
                'command': command,
                'function': func,
                'pattern': None
            })
            return func
        return decorator
    

    def on_text(self, pattern):
        def decorator(func):
            self.handlers['text'].append({
                'command': None,
                'function': func,
                'pattern': re.compile(pattern) if pattern else None
            })
            return func
        return decorator


    def on_any(self):
        def decorator(func):
            self.handlers['any'].append({'function': func})
    