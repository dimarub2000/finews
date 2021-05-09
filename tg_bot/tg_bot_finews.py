import os
import telebot
import requests

from tg_bot.msg_builder import MessageBuilder
from tg_bot.compressor import Compressor
from tg_bot.markup_builder import MarkupBuilder
from tg_bot.news_feed_handler import NewsFeedHandler

TG_BOT_TOKEN = os.environ['TG_BOT_TOKEN']
bot = telebot.TeleBot(TG_BOT_TOKEN)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):

    markup_builder = MarkupBuilder()

    if message.text == "/commands":
        markup = markup_builder.build_markup(['Новости по тикеру компании', 'Последние новости', 'Подписки', 'Поиск'])
        bot.send_message(message.from_user.id, "Выбери одну из команд на панели ниже", reply_markup=markup)
    elif message.text == "/help":
        bot.send_message(message.from_user.id,
                         "Привет! Напиши '/commands' и тебе выведутся все доступные на данный момент функции данного "
                         "бота.")
    elif message.text == "Новости по тикеру компании":
        markup = markup_builder.build_markup(['$TSLA', '$GOOGL', '$WMT', 'все тикеры'])
        bot.send_message(message.from_user.id, "Впиши тикер компании, которая тебя интересует"
                                               " или посмотри по каким тикерам сейчас есть новости",
                         reply_markup=markup)

        bot.register_next_step_handler(message, get_tag)
    elif message.text == "Последние новости":
        data = requests.get('http://127.0.0.1:5000/top?limit={}'.format(30)).json()
        news_feed_handler = NewsFeedHandler(data=data)
        news = news_feed_handler.get_new_page()
        show_news(message, news, news_feed_handler)

    elif message.text == "Подписки":
        markup = markup_builder.build_markup(['Подписаться', 'Отписаться', 'Мои подписки', "Выйти"])
        bot.send_message(message.from_user.id,
                         "С помощью кнопок ты можешь легко управлять своими подписками", reply_markup=markup)
        bot.register_next_step_handler(message, get_subscription)

    elif message.text == "Поиск":
        bot.send_message(message.from_user.id,
                         "Впиши запрос который тебя интересует")
        bot.register_next_step_handler(message, get_query)

    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши '/help'.")


def get_subscription(message):
    if message.text == "Подписаться":
        bot.send_message(message.from_user.id, "Впиши тикер компании, которая тебя интересует"
                                               " или посмотри по каким тикерам сейчас есть новости")
        bot.register_next_step_handler(message, subscribe)
    elif message.text == "Отписаться":
        bot.send_message(message.from_user.id, "Впиши тикер компании, от новостей который ты хотел бы отписаться")
        bot.register_next_step_handler(message, unsubscribe)

    elif message.text == "Мои подписки":
        tickers_list = list(
            map(lambda x: '$' + x,
                requests.get('http://127.0.0.1:5000/all_subscriptions?user_id={}'.format(message.from_user.id)).json()))
        if len(tickers_list) == 0:
            bot.send_message(message.from_user.id, "На данный момент у тебя нет подписок")
        else:
            tickers = get_all_tickers(tickers_list)
            bot.send_message(message.from_user.id, tickers)
        bot.register_next_step_handler(message, get_subscription)
    else:
        main_menu_message(message.from_user.id)


def main_menu_message(user):
    markup_builder = MarkupBuilder()
    markup = markup_builder.build_markup(['Новости по тикеру компании', 'Последние новости', 'Подписки', 'Поиск'])
    bot.send_message(user, "Могу я еще чем-то помочь?", reply_markup=markup)


def subscribe(message):
    user_tag = message.text.replace('$', '').upper()
    requests.post('http://127.0.0.1:5000/subscribe', json={"user_id": message.from_user.id, "tag": user_tag})
    bot.send_message(message.from_user.id, "Вы подписались на новости компании {}".format(user_tag))
    bot.register_next_step_handler(message, get_subscription)


def unsubscribe(message):
    user_tag = message.text.replace('$', '').upper()
    requests.delete('http://127.0.0.1:5000/unsubscribe', json={"user_id": message.from_user.id, "tag": user_tag})
    bot.send_message(message.from_user.id, "Вы отписались от новостей компании {}".format(user_tag))
    bot.register_next_step_handler(message, get_subscription)


def get_all_tickers(tickers_list):
    ans = ''
    for item in tickers_list:
        if ans != '':
            ans += ', '
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
        data = requests.get('http://127.0.0.1:5000/top?tag={}&limit={}'.format(user_tag, 30)).json()
        news_feed_handler = NewsFeedHandler(data, 1)
        news = news_feed_handler.get_new_page()
        show_news(message, news, news_feed_handler)


def get_query(message):
    user_query = message.text
    data = requests.get('http://127.0.0.1:9002/search?limit={}'.format(30), json=user_query).json()
    news_feed_handler = NewsFeedHandler(data=data)
    news = news_feed_handler.get_new_page()
    show_news(message, news, news_feed_handler)


def news_feed(message, news_feed_handler):
    if message.text == "Выйти":
        main_menu_message(message.from_user.id)
    elif message.text == "Дальше":
        news = news_feed_handler.get_new_page()
        show_news(message, news, news_feed_handler)


def show_news(message, news, news_feed_handler):
    if news is None:
        bot.send_message(message.from_user.id, "По твоему запросу у нас закончились новости!")
        main_menu_message(message.from_user.id)
        return
    compressor = Compressor()
    msg_builder = MessageBuilder(compressor=compressor)
    for item in news:
        msg = msg_builder.build_message(item)
        bot.send_message(message.from_user.id, msg, disable_web_page_preview=True)

    markup_builder = MarkupBuilder()
    markup = markup_builder.build_markup(["Дальше", "Выйти"])
    bot.send_message(message.from_user.id, "Продолжим?", reply_markup=markup)
    bot.register_next_step_handler(message, news_feed, news_feed_handler)


if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)
