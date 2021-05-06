import telebot
import requests
from telebot import types

bot = telebot.TeleBot('1581250567:AAHChhfr-OW4e0wj6jm_Bc4OmJNVHVm9Vzo')

user_tag = ''
user_limit = ''
state = 0

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global state
    if message.text == "/commands":
        markup = types.ReplyKeyboardMarkup()
        itembtn_top_news = types.KeyboardButton('top_news')
        itembtn_ticker = types.KeyboardButton('ticker')
        itembtn_subscribe = types.KeyboardButton('subscribe')
        markup.row(itembtn_top_news, itembtn_ticker)
        markup.row(itembtn_subscribe)
        bot.send_message(message.from_user.id, "Выбери одну из команд на панели ниже", reply_markup=markup)
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Привет! Напиши '/commands' и тебе выведутся все доступные на данный момент функции данного бота.")
    elif message.text == "top_news":
        state = 1
        bot.send_message(message.from_user.id, "Впиши тикер компании которая тебя интересует (если интересуют новости по всем компаниям сразу напиши -). Следующие тикеры доступны на данный момент:")

        bot.register_next_step_handler(message, get_tag)

    elif message.text == "ticker":
        pass
    elif message.text == "subscribe":
        pass
    elif state == 0:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши '/help'.")

def get_tag(message):
    global user_tag

    user_tag = message.text
    bot.send_message(message.from_user.id, "Напиши максимальное число последних новостей по этой компании, которые тебя интересуют")
    bot.register_next_step_handler(message, get_limit)

def get_limit(message):
    global user_limit, state
    user_limit = message.text
    if (user_tag == '-'):
        data = list(requests.get('http://127.0.0.1:5000/top?limit={}'.format(user_limit)).json())
    else:
        data = list(requests.get('http://127.0.0.1:5000/top?tag={}&limit={}'.format(user_tag, user_limit)).json())

    for item in data:
        bot.send_message(message.from_user.id, item['content'])

    if len(data) == 0:
        bot.send_message(message.from_user.id, "Ничего не найдено по такому запросу, либо не валидный лимит"
                " (попробуйте любое положительное число), либо нет такого тикера на данный момен (ниже"
                " представлены все доступные на данный момент тикеры)")

    state = 0


bot.polling(none_stop=True, interval=0)
