# eGOseRmOToRpHAntOM

search tweet and post to slack

# Requirement

* requests
* Twitter Bearer
* Slack token

# Installation

* Install Requests

```bash
pip install requests
```

* create settings.py

```python
TWITTER_KEY = ''  # Your Twitter Bearer
TWEET_QUERY = 'from:TwitterDev'
MAX_RESULTS = 20 # >= 10

SLACK_TOKEN = ''  # Your Slack token
CHANNEL_TO_POST = '#random'

TWEET_FILE_PATH = 'tweets.jsonl'
LOG_FILE_PATH = 'execute.log'
PICKLE_FILE_PATH = 'newest_id.pickle'
```

# Usage

```bash
python main.py
```

# Note

# Author

* poc-sleepy
* https://github.com/poc-sleepy

# License

"eGOseRmOToRpHAntOM" is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).
