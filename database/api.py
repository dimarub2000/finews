import json
import logging

from flask import request
from database import app, db
from marshmallow import Schema, fields, post_load

logger = logging.getLogger(__name__)


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    content = db.Column(db.String(1000))
    time = db.Column(db.String(20))
    link = db.Column(db.String(64))
    tags = db.Column(db.String(12), nullable=True)
    source = db.Column(db.String(24))


class NewsSchema(Schema):
    id = fields.Int()
    content = fields.Str()
    time = fields.Str()
    link = fields.Str()
    tags = fields.Str()
    source = fields.Str()

    @post_load
    def make_user(self, data, **kwargs):
        return News(**data)


news_schema = NewsSchema()
many_news_schema = NewsSchema(many=True)


@app.route('/news', methods=['POST'])
def add_news():
    data = request.get_json()
    logger.critical("data {}".format(data))
    for news in data:
        db.session.add(News(content=news['text'],
                            time=news['time'],
                            link=news['link'],
                            tags=news.get('tags'),
                            source=news.get('source')))
    db.session.commit()
    return 'OK'


@app.route('/news', methods=['GET'])
def get_news():
    news = News.query.all()
    return json.dumps(many_news_schema.dump(news, many=True))


if __name__ == '__main__':
    logger.critical("Creating all")
    db.create_all()
    app.run()
