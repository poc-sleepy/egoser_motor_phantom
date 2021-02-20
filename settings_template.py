"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  Twitter
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
TWITTER_KEY = ''  # Your Twitter Bearer
TWEET_QUERY = 'from:TwitterDev -is:retweet'
MAX_RESULTS = 10  # minimum: 10

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  Slack
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
SLACK_TOKEN = ''  # Your Slack token
CHANNEL_TO_POST = '#random'
TWEET_POST_COLOR = '#1976d2'  # #XXXXXX or None
RETWEET_POST_COLOR = '#4caf50'  # #XXXXXX or None

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  File Path
  When you use this app in crontab,
  1. Set ABSOLUTE path to each path.
  2. Set True to PICKLE_PATH_IS_ABSOLUTE.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
TWEET_FILE_PATH = 'tweets.jsonl'
LOG_FILE_PATH = 'execute.log'
PICKLE_FILE_PATH = 'newest_id.pickle'
PICKLE_PATH_IS_ABSOLUTE = False
# PICKLE_S3_BUCKET = 'egoser-motor-phantom'
