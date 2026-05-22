from typing import Callable, Optional, Dict, Any


class Handler:
    def __init__(self):
        self.handlers = []

    def on(self, msg_type: str = 'any', **filters):
        def decorator(func: Callable):
            self.handlers.append(
                {
                    'type': msg_type,
                    'function': func,
                    'filters': filters,
                    'priority': filters.get('priority', 0)
                }
            )
            self.handlers.sort(key=lambda x: x['priority'], reverse=True)
            return func
        return decorator

    def command(self, command: str, priority: int = 0):
        return self.on('command', command=command, priority=priority)

    def on_text(self, pattern: Optional[str] = None, priority: int = 0):
        return self.on('text', pattern=pattern, priority=priority)

    def on_photo(self):
        return self.on('photo')

    def on_any(self):
        return self.on('any')

    def on_callback(self, data: str, priority: int = 0):
        return self.on('callback', data=data, priority=priority)

    async def handle_callback(self, query: Dict[str, Any]):
        data = query.get("data", "")
        for handler in self.handlers:
            if handler['type'] != 'callback':
                continue
            expected = handler['filters'].get('data', '')
            if data == expected or data.startswith(f"{expected}__"):
                return await handler['function'](query)

    async def handle_message(self, message: Dict[str, Any]):
        text = message.get('text', '')
        is_command = text.startswith('/') if text else False
        command_name = text[1:].split()[0] if is_command else None

        print(f"\ntext='{text}', is_command={is_command}, command='{command_name}'")
        print(f"Доступно обработчиков: {len(self.handlers)}")

        for i, handler in enumerate(self.handlers):
            handler_type = handler['type']
            filters = handler['filters']

            print(f"  [{i}] Проверяем {handler_type} с фильтрами {filters}")

            if handler_type == 'callback':
                continue

            if handler_type == 'command':
                if not is_command:
                    continue
                expected = filters.get('command', '')
                if expected.startswith('/'):
                    expected = expected[1:]
                if command_name != expected:
                    continue

            elif handler_type == 'text':
                if is_command:
                    continue
                pattern = filters.get('pattern')
                if pattern and pattern not in text:
                    continue

            elif handler_type == 'photo':
                if 'photo' not in message:
                    continue

            elif handler_type == 'any':
                pass

            print(f"{handler['function'].__name__}")
            return await handler['function'](message)

        print("Ни один обработчик не подошел")
        return None