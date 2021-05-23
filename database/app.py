import json
import logging

from flask import Flask
from flask import request, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

from config.config_parser import FinewsConfigParser


app = Flask(__name__)
app.config.from_pyfile('database_config.py')
db = SQLAlchemy(app)
SERVICE_NAME = 'database'

cfg_parser = FinewsConfigParser()

logging.basicConfig()
logger = logging.getLogger(SERVICE_NAME)
logger.setLevel(cfg_parser.get_log_level(SERVICE_NAME, 'INFO'))
logger.setFormatter(logging.Formatter("%(asctime)s;%(levelname)s;%(message)s",
                              "%Y-%m-%d %H:%M:%S"))


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    time = db.Column(db.Integer)
    link = db.Column(db.String(100))
    text = db.Column(db.String(10000))
    tags = db.relationship('Tags', backref='news')
    source = db.Column(db.String(100))

    def to_dict(self):
        res = dict()
        res['id'] = self.id
        res['time'] = self.time
        res['link'] = self.link
        res['text'] = self.text
        res['tags'] = [elem.tag for elem in self.tags]
        res['source'] = self.source
        return res

    @staticmethod
    def news_to_list(news):
        return list(map(lambda x: x.to_dict(), news))


class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(16), nullable=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)


class Subs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(16), nullable=True)
    user_id = db.Column(db.String(100))


@app.route('/news', methods=['POST'])
def add_news():
    logger.info("got new data")
    data = request.get_json()
    for news in data:
        cur_news = News(
            text=news['text'],
            time=news['time'],
            link=news['link'],
            source=news['source']
        )
        db.session.add(cur_news)
        for tag in news.get('tags', []):
            db.session.add(Tags(tag=tag, news=cur_news))

    db.session.commit()
    return Response(status=200)


@app.route('/news', methods=['GET'])
def get_news():
    news = News.query.all()
    return Response(json.dumps(News.news_to_list(news)), status=200)


@app.route('/top', methods=['GET'])
def get_top():
    tag = request.args.get('tag')
    limit = request.args.get('limit', default=0, type=int)
    if tag is None:
        news = News.query.order_by(desc(News.time)).limit(limit).all()
    else:
        news = News.query.filter(News.tags.any(tag=tag)).order_by(desc(News.time)).limit(limit).all()

    response_list = News.news_to_list(news)

    if len(response_list) == 0:
        logger.debug('Not found news item for tag: {}'.format(tag))
        return Response(status=404)

    return Response(json.dumps(News.news_to_list(news)), status=200)


@app.route('/tags', methods=['GET'])
def get_tags():
    tags = db.session.query(Tags.tag).order_by(Tags.tag).distinct().all()
    return json.dumps(list(map(lambda x: x.tag, tags)))


@app.route('/subscribe', methods=['POST'])
def subscribe():
    logger.info("got new subscription")
    data = request.get_json()
    logger.debug("User: %d, Tag: %s" % (data['user_id'], data['tag']))
    subscription = Subs.query.filter_by(user_id=data['user_id'], tag=data['tag']).first()
    if subscription is not None:
        logger.debug('User %d already subscribed on %s' % (data['user_id'], data['tag']))
        return Response(status=400)

    db.session.add(Subs(
        user_id=data['user_id'],
        tag=data['tag']
    ))
    db.session.commit()
    return Response(status=200)


@app.route('/unsubscribe', methods=['DELETE'])
def unsubscribe():
    data = request.get_json()
    logger.info("got new unsubscription")
    logger.debug("User: %d, Tag: %s" % (data['user_id'], data['tag']))
    subscription = Subs.query.filter_by(user_id=data['user_id'], tag=data['tag']).first()
    if subscription is None:
        logger.debug('User %d is not subscribed on %s' % (data['user_id'], data['tag']))
        return Response(status=400)

    db.session.delete(subscription)
    db.session.commit()
    return Response(status=200)


@app.route('/unsubscribe_all', methods=['DELETE'])
def unsubscribe_all():
    data = request.get_json()
    logger.info("got new unsubscription from all")
    logger.debug("User: %d" % data['user_id'])

    db.session.query(Subs).filter_by(user_id=data['user_id']).delete(synchronize_session=False)
    db.session.commit()
    return Response(status=200)


@app.route('/all_subscriptions', methods=['GET'])
def all_subscriptions():
    user_id = request.args.get('user_id')
    tags = db.session.query(Subs.tag).filter_by(user_id=user_id).all()
    return Response(json.dumps(list(map(lambda x: x.tag, tags))), status=200)


@app.route('/get_subscribers', methods=['GET'])
def get_subscribers():
    tags = request.get_json()
    user_ids = db.session.query(Subs.user_id).filter(Subs.tag.in_(tags)).distinct().all()
    return Response(json.dumps(list(map(lambda x: x.user_id, user_ids))), 200)


@app.route('/last_time', methods=['GET'])
def last_time():
    source = request.args.get('source')
    time = db.session.query(News.time).filter_by(source=source).order_by(desc(News.time)).limit(1).first_or_404()
    return Response(json.dumps(time.time), status=200)


@app.route('/ping', methods=['GET'])
def ping():
    logger.info("PING")
    return Response(status=200)


if __name__ == "__main__":
    db.create_all()
    app.run(port=5000)
