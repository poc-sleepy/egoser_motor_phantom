# -*- coding: utf-8 -*-
""" eGOseRmOToRpHAntOM

   TwitterでエゴサーチをしてSlackに投稿するやつ

"""

import sys
import os
from os.path import join, dirname
import pickle
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv


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

    def send_attachments_message(self, attachments, channel):
        params = {'token': self.__token, 'channel': channel, 'attachments': str(attachments)}

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


def generate_attachments_from_tweet(tweet):
    # FixMe: リツイート判定はもっといい方法があるのでは？
    is_retweet = tweet['text'].startswith('RT @')
    color_text = os.environ.get('RETWEET_POST_COLOR') if is_retweet else os.environ.get('TWEET_POST_COLOR')

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

    attachments = [
        {
            'color': color_text,
            'blocks': blocks
        }
    ]

    return attachments


if __name__ == '__main__':

    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    twitter = TwitterDriver(os.environ.get('TWITTER_KEY'))
    slack = SlackDriver(os.environ.get('SLACK_TOKEN'))
    logger = Logger(os.environ.get('LOG_FILE_PATH'))

    # QUERY
    twitter_params = {
        'query': os.environ.get('TWEET_QUERY'),
        'max_results': int(os.environ.get('MAX_RESULTS')),
        'tweet.fields': 'created_at,source',
        'expansions': 'author_id',
        'user.fields': 'username,name,profile_image_url',
    }

    # Load Preserved tweet id
    pickle_path = os.environ.get('PICKLE_FILE_PATH')
    pickle_path_is_absolute = os.environ.get('PICKLE_PATH_IS_ABSOLUTE').lower() == 'true'
    if not pickle_path_is_absolute:
        pickle_path = './' + pickle_path

    if os.path.exists(pickle_path):
        with open(pickle_path, mode='rb') as loadfile:
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

        with open(os.environ.get('TWEET_FILE_PATH'), mode='a', encoding='utf_8') as outfile:
            for tweet in tweets:
                outfile.write(str(tweet) + '\n')
                attachments = generate_attachments_from_tweet(tweet)
                try:
                    slack.send_attachments_message(attachments, os.environ.get('CHANNEL_TO_POST'))
                except Exception as err:
                    logger.error(err)
                    print(err, file=sys.stderr)
                    sys.exit(1)

        # Preserve newest tweet id
        with open(pickle_path, mode='wb') as outfile:
            to_dump = {'newest_id': meta_data['newest_id']}
            pickle.dump(to_dump, outfile)
