class InlineKeyboard:
    day_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

    def __init__(self, bot):
        self.bot = bot


    def send_keyboard(self, chat_id):
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": self.day_names[i], "callback_data": f"day_{i}"} for i in range(4)
                ],
                [
                    {"text": self.day_names[4], "callback_data": "day_4"},
                    {"text": self.day_names[5], "callback_data": "day_5"},
                    {"text": "Вся неделя", "callback_data": "day_all"}
                ]
            ]
        }

        