# -*- coding: utf-8 -*-
""" eGOseRmOToRpHAntOM

   TwitterでエゴサーチをしてSlackに投稿するやつ

"""

import sys
import os
import pickle
from datetime import datetime, timedelta, timezone

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

    def send_blocks_message(self, blocks, channel):
        params = {'token': self.__token, 'channel': channel, 'blocks': str(blocks)}

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
            # FixMe: タイムゾーンがJST前提
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
                tweet['profile_image_url'] = user['profile_image_url']
    return tweets


def generate_blocks_from_tweet(tweet):
    tweet_url = 'https://twitter.com/{}/status/{}'.format(tweet['username'], tweet['id'])
    body_text = 'by <{}|*{}* (@{})>\n'.format(tweet_url, tweet['name'], tweet['username'])
    body_text += tweet['text']

    # HACK: created_atのマイクロ秒が常に.000かは未確認
    datetime_created_at_utc = datetime.strptime(tweet['created_at'].replace('Z', '+0000'), '%Y-%m-%dT%H:%M:%S.000%z')
    # FixMe: タイムゾーンが決め打ち
    timezone_jst = timezone(timedelta(hours=9))
    datetime_created_at_jst = datetime_created_at_utc.astimezone(timezone_jst)
    text_created_at = datetime_created_at_jst.strftime('%Y/%m/%d %H:%M:%S')

    blocks = [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': body_text
            },
            'accessory': {
                'type': 'image',
                'image_url': tweet['profile_image_url'],
                'alt_text': tweet['name']
            }
        },
        {
            'type': 'context',
            'elements': [
                {
                    'type': 'plain_text',
                    'text': '{} ({})'.format(text_created_at, tweet['source'])
                }
            ]
        },
        {
            'type': 'divider'
        }
    ]

    return blocks


if __name__ == '__main__':

    twitter = TwitterDriver(settings.TWITTER_KEY)
    slack = SlackDriver(settings.SLACK_TOKEN)
    logger = Logger(settings.LOG_FILE_PATH)

    # QUERY
    twitter_params = {
        'query': settings.TWEET_QUERY,
        'max_results': settings.MAX_RESULTS,
        'tweet.fields': 'created_at,source',
        'expansions': 'author_id',
        'user.fields': 'username,name,profile_image_url',
    }

    # Load Preserved tweet id
    if os.path.exists('./' + settings.PICKLE_FILE_PATH):  # if PICKLE_FILE_PATH is ABSOLUTE path, delete './' +
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
                blocks = generate_blocks_from_tweet(tweet)
                try:
                    # pass
                    slack.send_blocks_message(blocks, settings.CHANNEL_TO_POST)
                except Exception as err:
                    logger.error(err)
                    print(err, file=sys.stderr)
                    sys.exit(1)

        # Preserve newest tweet id
        with open(settings.PICKLE_FILE_PATH, mode='wb') as outfile:
            to_dump = {'newest_id': meta_data['newest_id']}
            pickle.dump(to_dump, outfile)
