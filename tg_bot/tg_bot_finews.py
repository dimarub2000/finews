import os
import telebot
import requests

from tg_bot.msg_builder import MessageBuilder
from tg_bot.compressor import Compressor
from tg_bot.markup_builder import MarkupBuilder

TG_BOT_TOKEN = os.environ['TG_BOT_TOKEN']
bot = telebot.TeleBot(TG_BOT_TOKEN)

state = 0


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global state

    markup_builder = MarkupBuilder()

    if message.text == "/commands":
        markup = markup_builder.build_markup(['Новости по тикеру компании', 'Последние новости', 'Подписки', 'Поиск'])
        bot.send_message(message.from_user.id, "Выбери одну из команд на панели ниже", reply_markup=markup)
    elif message.text == "/help":
        bot.send_message(message.from_user.id,
                         "Привет! Напиши '/commands' и тебе выведутся все доступные на данный момент функции данного "
                         "бота.")
    elif message.text == "Новости по тикеру компании":
        state = 1
        markup = markup_builder.build_markup(['$TSLA', '$GOOGL', '$WMT', 'все тикеры'])
        bot.send_message(message.from_user.id, "Впиши тикер компании, которая тебя интересует"
                                               " или посмотри по каким тикерам сейчас есть новости",
                         reply_markup=markup)

        bot.register_next_step_handler(message, get_tag)
    elif message.text == "Последние новости":
        state = 3
        bot.send_message(message.from_user.id,
                         "Напиши максимальное число последних новостей, которые ты хотел бы увидеть")
        bot.register_next_step_handler(message, get_limit)
    elif message.text == "Подписки":
        state = 4
        markup = markup_builder.build_markup(['Подписаться', 'Отписаться', 'Мои подписки', "Выйти"])
        bot.send_message(message.from_user.id,
                         "С помощью кнопок ты можешь легко управлять своими подписками", reply_markup=markup)
        bot.register_next_step_handler(message, get_subscription)

    elif message.text == "Поиск":
        state = 2
        bot.send_message(message.from_user.id,
                         "Впиши запрос который тебя интересует")
        bot.register_next_step_handler(message, get_query)

    elif state == 0:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши '/help'.")


def get_subscription(message):
    if message.text == "Подписаться":
        bot.send_message(message.from_user.id, "Впиши тикер компании, которая тебя интересует"
                                               " или посмотри по каким тикерам сейчас есть новости")
        bot.register_next_step_handler(message, subscribe)
    elif message.text == "Отписатсья":
        bot.send_message(message.from_user.id, "Впиши тикер компании, от новостей который ты хотел бы отписаться")
        bot.register_next_step_handler(message, subscribe)

    elif message.text == "Мои подписки":
        tickers_list = list(map(lambda x: '$' + x,
                                requests.get('http://127.0.0.1:5000/all_subscriptions?user_id={}'.format(message.from_user.id)).json()))
        tickers = get_all_tickers(tickers_list)
        bot.send_message(message.from_user.id, tickers)
        bot.register_next_step_handler(message, get_subscription)
    else:
        main_menu_message(message.from_user.id)


def main_menu_message(user):
    global state
    markup_builder = MarkupBuilder()
    markup = markup_builder.build_markup(['Новости по тикеру компании', 'Последние новости', 'Подписки', 'Поиск'])
    bot.send_message(user, "Могу я еще чем-то помочь?", reply_markup=markup)
    state = 0


def subscribe(message):
    user_tag = message.text.replace('$', '').upper()
    requests.post('http://127.0.0.1:5000/subscribe', json={"user_id": message.from_user.id, "tag": user_tag})
    bot.send_message(message.from_user.id, "Вы подписались на новости компании {}".format(user_tag))
    main_menu_message(message.from_user.id)


def unsubscribe(message):
    user_tag = message.text.replace('$', '').upper()
    requests.delete('http://127.0.0.1:5000/unsubscribe', json={"user_id": message.from_user.id, "tag": user_tag})
    bot.send_message(message.from_user.id, "Вы Отписались от новостей компании {}".format(user_tag))
    main_menu_message(message.from_user.id)


def get_all_tickers(tickers_list):
    ans = ''
    first = True
    for item in tickers_list:
        if not first:
            ans += ', '
        else:
            first = False
        ans += item
    return ans


def get_tag(message):
    if message.text == "все тикеры":
        tickers_list = list(map(lambda x: '$' + x, requests.get('http://127.0.0.1:5000/tags').json()))
        tickers = get_all_tickers(tickers_list)
        bot.send_message(message.from_user.id, tickers)
        bot.register_next_step_handler(message, get_tag)

    else:
        user_tag = message.text.replace('$', '').upper()
        bot.send_message(message.from_user.id,
                         "Напиши максимальное число последних новостей по этой компании, которые тебя интересуют")
        bot.register_next_step_handler(message, get_limit, '', user_tag)


def get_query(message):
    user_query = message.text
    bot.send_message(message.from_user.id,
                     "Напиши максимальное число новостей по этому запросу, которые тебя интересуют")
    bot.register_next_step_handler(message, get_limit, user_query)


def get_limit(message, query='', user_tag=''):
    send_messages(message.from_user.id, message.text, query, user_tag)


def send_messages(user, user_limit, query='', user_tag=''):
    global state
    data = []
    if state == 1:
        data = requests.get('http://127.0.0.1:5000/top?tag={}&limit={}'.format(user_tag, user_limit)).json()
    elif state == 2:
        data = requests.get('http://127.0.0.1:9002/search?limit={}'.format(user_limit), json=query).json()
    elif state == 3:
        data = requests.get('http://127.0.0.1:5000/top?limit={}'.format(user_limit)).json()

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

    main_menu_message(user)


if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)
