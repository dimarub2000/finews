import json
import requests

from flask import request
from sqlalchemy import desc
from database import app, db


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    time = db.Column(db.String(100))
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
    tag = db.Column(db.String(12), nullable=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)


db.create_all()


@app.route('/news', methods=['POST'])
def add_news():
    data = request.get_json()
    requests.post('http://127.0.0.1:9002/index', json=data)
    for news in data:
        cur_news = News(
            text=news['text'],
            time=news['time'],
            link=news['link'],
            source=news.get('source')
        )
        db.session.add(cur_news)
        for tag in news.get('tags', []):
            db.session.add(Tags(tag=tag, news=cur_news))

    db.session.commit()
    return 'OK\n'


@app.route('/news', methods=['GET'])
def get_news():
    news = News.query.all()
    return json.dumps(News.news_to_list(news))


@app.route('/top', methods=['GET'])
def get_top():
    tag = request.args.get('tag')
    limit = request.args.get('limit', default=0, type=int)
    print(limit)
    if tag is None:
        news = News.query.order_by(desc(News.id)).limit(limit).all()
    else:
        news = News.query.filter(News.tags.any(tag=tag)).order_by(desc(News.id)).limit(limit).all()

    return json.dumps(News.news_to_list(news))


@app.route('/tags', methods=['GET'])
def get_tags():
    tags = db.session.query(Tags.tag).order_by(Tags.tag).distinct().all()
    return json.dumps(list(map(lambda x: x.tag, tags)))


if __name__ == "__main__":
    app.run()
