import os
import telebot
import requests
import logging

from tg_bot.msg_builder import MessageBuilder
from tg_bot.compressor import Compressor
from tg_bot.markup_builder import MarkupBuilder
from tg_bot.news_feed_handler import NewsFeedHandler
from config.config_parser import FinewsConfigParser

TG_BOT_TOKEN = os.environ['TG_BOT_TOKEN']
bot = telebot.TeleBot(TG_BOT_TOKEN)

cfg_parser = FinewsConfigParser()
DATABASE_URI = cfg_parser.get_service_url('database')
SEARCH_URI = cfg_parser.get_service_url('search')
SERVICE_NAME = 'tg_bot'

logging.basicConfig()
logger = logging.getLogger(SERVICE_NAME)
logger.setLevel(cfg_parser.get_log_level(SERVICE_NAME, 'INFO'))


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
        markup = markup_builder.build_markup(['$TSLA', '$GOOGL', '$WMT', 'Все тикеры', 'Выйти'])
        bot.send_message(message.from_user.id, "Впиши тикер компании, которая тебя интересует"
                                               " или посмотри по каким тикерам сейчас есть новости",
                         reply_markup=markup)

        bot.register_next_step_handler(message, get_tag)
    elif message.text == "Последние новости":
        limit = cfg_parser.get_service_setting(SERVICE_NAME, 'max_feed_size', 30)
        page_size = cfg_parser.get_service_setting(SERVICE_NAME, 'page_size', 3)
        data = requests.get(DATABASE_URI + '/top?limit={}'.format(limit)).json()
        news_feed_handler = NewsFeedHandler(data=data, page_size=page_size)
        news = news_feed_handler.get_new_page()
        show_news(message, news, news_feed_handler)

    elif message.text == "Подписки":
        markup = markup_builder.build_markup(['Подписаться', 'Отписаться', 'Мои подписки', "Выйти"])
        bot.send_message(message.from_user.id,
                         "С помощью кнопок ты можешь легко управлять своими подписками", reply_markup=markup)
        bot.register_next_step_handler(message, get_subscription)

    elif message.text == "Поиск":
        markup = markup_builder.build_markup(["Выйти"])
        bot.send_message(message.from_user.id,
                         "Впиши запрос который тебя интересует", reply_markup=markup)
        bot.register_next_step_handler(message, get_query)

    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши '/help'.")


def get_subscription(message):
    if message.text == "Подписаться":
        markup_builder = MarkupBuilder()
        markup = markup_builder.build_markup(["Назад"])
        bot.send_message(message.from_user.id, "Впиши тикер компании, которая тебя интересует"
                                               " или посмотри по каким тикерам сейчас есть новости",
                         reply_markup=markup)
        bot.register_next_step_handler(message, subscribe)
    elif message.text == "Отписаться":
        markup_builder = MarkupBuilder()
        markup = markup_builder.build_markup(["Назад"])
        bot.send_message(message.from_user.id, "Впиши тикер компании, от новостей который ты хотел бы отписаться",
                         reply_markup=markup)
        bot.register_next_step_handler(message, unsubscribe)

    elif message.text == "Мои подписки":
        tickers_list = list(
            map(lambda x: '$' + x,
                requests.get(DATABASE_URI + '/all_subscriptions?user_id={}'.format(message.from_user.id)).json()))
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


def prev_message(message):
    markup_builder = MarkupBuilder()
    markup = markup_builder.build_markup(['Подписаться', 'Отписаться', 'Мои подписки', "Выйти"])
    bot.send_message(message.from_user.id, "Ты вернулся в меню подписок", reply_markup=markup)
    bot.register_next_step_handler(message, get_subscription)


def subscribe(message):
    markup_builder = MarkupBuilder()
    markup = markup_builder.build_markup(['Подписаться', 'Отписаться', 'Мои подписки', "Выйти"])
    if message.text == "Назад":
        bot.send_message(message.from_user.id, "Ты вернулся в меню подписок", reply_markup=markup)
        bot.register_next_step_handler(message, get_subscription)
        return
    user_tag = message.text.replace('$', '').upper()
    requests.post(DATABASE_URI + '/subscribe', json={"user_id": message.from_user.id, "tag": user_tag})
    bot.send_message(message.from_user.id, "Вы подписались на новости компании {}".format(user_tag), reply_markup=markup)
    bot.register_next_step_handler(message, get_subscription)


def unsubscribe(message):
    markup_builder = MarkupBuilder()
    markup = markup_builder.build_markup(['Подписаться', 'Отписаться', 'Мои подписки', "Выйти"])
    if message.text == "Назад":
        bot.send_message(message.from_user.id, "Ты вернулся в меню подписок", reply_markup=markup)
        bot.register_next_step_handler(message, get_subscription)
        return
    user_tag = message.text.replace('$', '').upper()
    response = requests.delete(DATABASE_URI + '/unsubscribe', json={"user_id": message.from_user.id, "tag": user_tag})
    if response.status_code == 400:
        bot.send_message(message.from_user.id, "Кажется, ты не был подписан на новости этой компании!", reply_markup=markup)
    else:
        bot.send_message(message.from_user.id, "Вы отписались от новостей компании {}".format(user_tag), reply_markup=markup)
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
        tickers_list = list(map(lambda x: '$' + x, requests.get(DATABASE_URI + '/tags').json()))
        tickers = get_all_tickers(tickers_list)
        bot.send_message(message.from_user.id, tickers)
        bot.register_next_step_handler(message, get_tag)

    elif message.text == "Выйти":
        main_menu_message(message.from_user.id)
    else:
        user_tag = message.text.replace('$', '').upper()
        limit = cfg_parser.get_service_setting(SERVICE_NAME, 'max_feed_size', 30)
        page_size = cfg_parser.get_service_setting(SERVICE_NAME, 'page_size', 3)
        response = requests.get(DATABASE_URI + '/top?tag={}&limit={}'.format(user_tag, limit))
        if response.status_code == 404:
            bot.send_message(message.from_user.id, "К сожалению по даному тикеру у нас нет новостей,"
                    " но ты можешь подписаться, нажав на кнопку Подписки, и мы будем присылать свежие"
                    " новости по этому и любому другому тикеру")
            main_menu_message(message.from_user.id)
            return
        news_feed_handler = NewsFeedHandler(response.json(), page_size)
        news = news_feed_handler.get_new_page()
        show_news(message, news, news_feed_handler)


def get_query(message):
    if message.text == "Выйти":
        main_menu_message(message.from_user.id)
        return
    user_query = message.text
    limit = cfg_parser.get_service_setting(SERVICE_NAME, 'max_feed_size', 30)
    page_size = cfg_parser.get_service_setting(SERVICE_NAME, 'page_size', 3)
    response = requests.get(SEARCH_URI + '/search?limit={}'.format(limit), json=user_query)
    if response.status_code == 404:
        bot.send_message(message.from_user.id, "К сожалению, по твоему запросу у нас нет новостей.")
        main_menu_message(message.from_user.id)
        return
    news_feed_handler = NewsFeedHandler(data=response.json(), page_size=page_size)
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
        bot.send_message(message.from_user.id, "По твоему запросу у нас закончились новости,"
        " но ты можешь подписаться на свежие новости по этой и любой другой компании, нажав на кнопку Подписки")
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
