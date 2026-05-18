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