import telebot
from telebot import types

bot = telebot.TeleBot('1581250567:AAHChhfr-OW4e0wj6jm_Bc4OmJNVHVm9Vzo')

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/commands":
        markup = types.ReplyKeyboardMarkup()
        itembtn_top_news = types.KeyboardButton('top_news')
        itembtn_ticker = types.KeyboardButton('ticker')
        itembtn_subscribe = types.KeyboardButton('subscribe')
        markup.row(itembtn_top_news, itembtn_ticker)
        markup.row(itembtn_subscribe)
        bot.send_message(message.from_user.id, "Choose one letter:", reply_markup=markup)
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Привет! Напиши '/commands' и тебе выведутся все доступные на данный момент функции данного бота.")
    elif message.text == "top_news":
        pass
    elif message.text == "ticker":
        pass
    elif message.text == "subscribe":
        pass
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши '/help'.")


bot.polling(none_stop=True, interval=0)
