import tweepy as tw
import json
import os


def init_api():
    consumer_key = os.environ.get('CONSUMER_KEY')
    consumer_secret = os.environ.get('CONSUMER_SECRET')
    access_token = os.environ.get('ACCESS_TOKEN')
    access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET')
    auth = tw.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tw.API(auth, wait_on_rate_limit=True)
    return api


class TweetParser(object):
    def __init__(self, api, num_tweets: int = 1000, sources: list = None):
        if sources is None:
            self.sources = []
        else:
            self.sources = sources.copy()
        self.num_tweets = num_tweets
        self.api = api

    def get_tweets_by_ticker(self, ticker: str, data_since: str, data_until: str):
        list_of_tweets = []
        for tweet in tw.Cursor(self.api.search, q=ticker + ' -filter:retweets', since=data_since, until=data_until,
                               lang='en').items(self.num_tweets):
            dict_ = {
                'Source': 'twitter',
                'Keywords': ticker,
                'User Name': tweet.user.name,
                'Screen Name': tweet.user.screen_name,
                'Tweet Created at': tweet.created_at,
                'Tweet Text': tweet.text,
                'Location': tweet.user.location,
                'Likes': tweet.favorite_count,
                'Retweets': tweet.retweet_count
            }
            list_of_tweets.append(dict_)
        return json.dumps(list_of_tweets)

    def append_new_source(self, screen_name: str):
        self.sources.append(screen_name)

    def get_tweets_from_source(self):
        list_of_tweets = []
        for source in self.sources:
            for tweet in tw.Cursor(self.api.user_timeline, screen_name=source).items(5):
                dict_ = {
                    'Source': 'twitter',
                    'User Name': tweet.user.name,
                    'Screen Name': tweet.user.screen_name,
                    'Tweet Created at': tweet.created_at,
                    'Tweet Text': tweet.text,
                    'Location': tweet.user.location,
                    'Likes': tweet.favorite_count,
                    'Retweets': tweet.retweet_count
                }
                list_of_tweets.append(dict_)
        return json.dumps(list_of_tweets)
