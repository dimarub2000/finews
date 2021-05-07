import telebot
import requests
from telebot import types
from tg_bot.msg_builder import MessageBuilder
from tg_bot.compressor import Compressor

bot = telebot.TeleBot('1581250567:AAHChhfr-OW4e0wj6jm_Bc4OmJNVHVm9Vzo')

user_tag = ''
user_limit = ''
user_query = ''
state = 0


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global state

    if message.text == "/commands":
        markup = types.ReplyKeyboardMarkup()
        itembtn_top_news = types.KeyboardButton('top news')
        itembtn_ticker = types.KeyboardButton('tickers')
        itembtn_subscribe = types.KeyboardButton('subscribe')
        itembtn_search = types.KeyboardButton('search')
        markup.row(itembtn_top_news, itembtn_ticker)
        markup.row(itembtn_subscribe, itembtn_search)
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
    elif message.text == "search":
        state = 2
        bot.send_message(message.from_user.id,
                         "Впиши запрос который тебя интересует")
        bot.register_next_step_handler(message, get_query)

    elif state == 0:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши '/help'.")


def get_tag(message):
    global user_tag

    user_tag = message.text.replace('$', '').upper()
    bot.send_message(message.from_user.id,
                     "Напиши максимальное число последних новостей по этой компании, которые тебя интересуют")
    bot.register_next_step_handler(message, get_limit)


def get_query(message):
    user_query = message.text
    bot.send_message(message.from_user.id,
                     "Напиши максимальное число новостей по этому запросу, которые тебя интересуют")
    bot.register_next_step_handler(message, get_limit, user_query)


def get_limit(message, query=''):
    global user_limit
    send_messages(message.from_user.id, message.text, query)


def send_messages(user, user_limit, query=''):
    global state
    data = []
    if state == 1:
        if user_tag == '-':
            data = requests.get('http://127.0.0.1:5000/top?limit={}'.format(user_limit)).json()
        else:
            data = requests.get('http://127.0.0.1:5000/top?tag={}&limit={}'.format(user_tag, user_limit)).json()
    elif state == 2:
        data = requests.get('http://127.0.0.1:9002/search?limit={}'.format(user_limit), json=query).json()

    compressor = Compressor()
    msg_builder = MessageBuilder(compressor=compressor)
    for item in data:
        msg = msg_builder.build_message(item)
        bot.send_message(user, msg, disable_web_page_preview=True)

    if len(data) == 0 and state == 1:
        bot.send_message(user, "Ничего не найдено по такому запросу, либо не валидный лимит"
                               " (попробуйте любое положительное число), либо нет такого тикера на "
                               " данный момен ( "
                               " чтобы посмотреть доступные на данный момент тикеры, напиши мне "
                               " команду: tickers)")
    if len(data) == 0 and state == 2:
        bot.send_message(user, "-")

    state = 0


bot.polling(none_stop=True, interval=0)
