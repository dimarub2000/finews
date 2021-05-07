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
    bot.send_message(144728771, "3% ААААААААААААААААААА")
    if message.text == "/commands":
        markup = types.ReplyKeyboardMarkup()
        itembtn_top_news = types.KeyboardButton('top news')
        itembtn_ticker = types.KeyboardButton('tickers')
        itembtn_subscribe = types.KeyboardButton('subscribe')
        markup.row(itembtn_top_news, itembtn_ticker)
        markup.row(itembtn_subscribe)
        bot.send_message(message.from_user.id, "Выбери одну из команд на панели ниже", reply_markup=markup)
    elif message.text == "/help":
        bot.send_message(message.from_user.id,
                         "Привет! Напиши '/commands' и тебе выведутся все доступные на данный момент функции данного "
                         "бота.")
    elif message.text == "top news":
        state = 1
        bot.send_message(message.from_user.id,
                         "Впиши тикер компании которая тебя интересует (если интересуют новости по всем компаниям "
                         "сразу напиши -).")

        bot.register_next_step_handler(message, get_tag)

    elif message.text == "tickers":
        tickers_list = list(map(lambda x: '$' + x, requests.get('http://127.0.0.1:5000/tags').json()))
        ans = ''
        first = True
        for item in tickers_list:
            if not first:
                ans += ', '
            else:
                first = False
            ans += item
        bot.send_message(message.from_user.id, ans)
    elif message.text == "subscribe":
        pass
    elif state == 0:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши '/help'.")


def get_tag(message):
    global user_tag

    user_tag = message.text.replace('$', '').upper()
    bot.send_message(message.from_user.id,
                     "Напиши максимальное число последних новостей по этой компании, которые тебя интересуют")
    bot.register_next_step_handler(message, get_limit)


def get_limit(message):
    global user_limit, state
    user_limit = message.text
    if user_tag == '-':
        data = list(requests.get('http://127.0.0.1:5000/top?limit={}'.format(user_limit)).json())
    else:
        data = list(requests.get('http://127.0.0.1:5000/top?tag={}&limit={}'.format(user_tag, user_limit)).json())

    for item in data:
        if (len(item['tags'])):
            bot.send_message(message.from_user.id, "Новость по компании: {},"
                                               " время публикации: {}, ссылка на источник: {}".format(item['tags'],
                                                                                                      item['time'],
                                                                                                      item['link']),
                            disable_web_page_preview=True)
        else:
            bot.send_message(message.from_user.id, "время публикации: {}, "
                                                    "ссылка на источник: {}".format(item['time'],
                                                                                    item['link']),
                            disable_web_page_preview=True)
        bot.send_message(message.from_user.id, item['content'], disable_web_page_preview=True)

    if len(data) == 0:
        bot.send_message(message.from_user.id, "Ничего не найдено по такому запросу, либо не валидный лимит"
                                               "(попробуйте любое положительное число), либо нет такого тикера на "
                                               "данный момен ( "
                                               "чтобы посмотреть доступные на данный момент тикеры, напиши мне "
                                               "команду: tickers)")

    state = 0


bot.polling(none_stop=True, interval=0)
