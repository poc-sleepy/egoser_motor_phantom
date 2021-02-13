# -*- coding: utf-8 -*-
""" eGOseRmOToRpHAntOM

   TwitterでエゴサーチをしてSlackに投稿するやつ

"""

import sys
import os
import pickle
from datetime import datetime

import requests

import settings


class TwitterDriver:

    def __init__(self, bearer):
        self.__headers = {
            'Authorization': 'Bearer {}'.format(bearer),
            'Content-Type': 'application/json',
        }

    def search_recent(self, params):
        r = requests.get('https://api.twitter.com/2/tweets/search/recent',
                         params=params,
                         headers=self.__headers)
        if r.status_code == requests.codes.ok:
            logger.info('200 OK\t{}'.format(r.url))
            return r.json()

        else:
            r.raise_for_status()


class SlackDriver:

    def __init__(self, token):
        self.__token = token  # slack_api_token
        self.__headers = {'Content-Type': 'application/json'}

    def send_message(self, message, channel):
        params = {'token': self.__token, 'channel': channel, 'text': message}

        r = requests.post('https://slack.com/api/chat.postMessage',
                          headers=self.__headers,
                          params=params)
        if r.status_code == requests.codes.ok:
            logger.info('200 OK\t{}'.format(r.url))
            json = r.json()
            if json['ok']:
                if 'warning' in json:
                    logger.warn('Slack: {}'.format(json['stuff']))
            else:
                logger.error('Slack: {}'.format(json['error']))
        else:
            r.raise_for_status()


class Logger:

    def __init__(self, filepath):
        self.__filepath = filepath

    def __write_log(self, msg, log_level):
        with open(self.__filepath, mode='a', encoding='utf_8') as outfile:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' +09:00'
            outfile.write('{}\t[{}]: {}\n'.format(timestamp, log_level, msg))

    def error(self, msg):
        self.__write_log(msg, 'ERROR')

    def warn(self, msg):
        self.__write_log(msg, 'WARN')

    def info(self, msg):
        self.__write_log(msg, 'INFO')


def merge_tweet_author(tweets, users):
    for tweet in tweets:
        for user in users:
            if tweet['author_id'] == user['id']:
                tweet['username'] = user['username']
                tweet['name'] = user['name']
    return tweets


if __name__ == '__main__':

    twitter = TwitterDriver(settings.TWITTER_KEY)
    slack = SlackDriver(settings.SLACK_TOKEN)
    logger = Logger(settings.LOG_FILE_PATH)

    # QUERY
    twitter_params = {
        'query': settings.TWEET_QUERY,
        'max_results': settings.MAX_RESULTS,
        'tweet.fields': 'created_at',
        'expansions': 'author_id',
        'user.fields': 'username,name',
    }

    # Load Preserved tweet id
    if os.path.exists('./' + settings.PICKLE_FILE_PATH): # if PICKLE_FILE_PATH is ABSOLUTE path, delete './' +
        with open(settings.PICKLE_FILE_PATH, mode='rb') as loadfile:
            twitter_params['since_id'] = pickle.load(loadfile)['newest_id']

    try:
        json = twitter.search_recent(twitter_params)

    except Exception as err:
        logger.error(err)
        print(err, file=sys.stderr)
        sys.exit(1)

    meta_data = json['meta']
    logger.info('{} tweets found.'.format(meta_data['result_count']))
    print('{} tweets found.'.format(meta_data['result_count']), file=sys.stdout)

    if meta_data['result_count']:

        tweets = merge_tweet_author(json['data'], json['includes']['users'])
        tweets.reverse()  # created_date ASC

        with open(settings.TWEET_FILE_PATH, mode='a', encoding='utf_8') as outfile:
            for tweet in tweets:
                outfile.write(str(tweet) + '\n')
                slack_msg = 'https://twitter.com/twitter/status/{}'.format(tweet['id'])
                try:
                    slack.send_message(slack_msg, settings.CHANNEL_TO_POST)
                except Exception as err:
                    logger.error(err)
                    print(err, file=sys.stderr)
                    sys.exit(1)

        # Preserve newest tweet id
        with open(settings.PICKLE_FILE_PATH, mode='wb') as outfile:
            to_dump = {'newest_id': meta_data['newest_id']}
            pickle.dump(to_dump, outfile)
