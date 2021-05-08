from telebot import types


class MarkupBuilder(object):
    def __init__(self, n_buttons_in_rows=2):
        self.n_buttons_in_rows = n_buttons_in_rows

    def build_markup(self, buttons_name):
        buttons = []
        for button in buttons_name:
            buttons.append(types.KeyboardButton(button))

        markup = types.ReplyKeyboardMarkup()
        for i in range(0, len(buttons), self.n_buttons_in_rows):
            markup.row(*buttons[i:i + self.n_buttons_in_rows])
        return markup
