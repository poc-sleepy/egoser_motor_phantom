# eGOseRmOToRpHAntOM

search tweet and post to slack

# Requirement

* requests 2.25.11
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
MAX_RESULTS = 20 # Minimum is 10

SLACK_TOKEN = ''  # Your Slack token
CHANNEL_TO_POST = '#random'

TWEET_FILE_PATH = 'tweets.jsonl' # If you will use this in crontab, set ABSOLUTE path.
LOG_FILE_PATH = 'execute.log' # If you will use this in crontab, set ABSOLUTE path.
PICKLE_FILE_PATH = 'newest_id.pickle' # If you will use this in crontab, set ABSOLUTE path.
```

# Usage

```bash
git clone https://github.com/poc-sleepy/egoser_motor_phantom.git
cd egoser_motor_phantom
vi settings.py
python3 main.py
```

# Note

# Author

* poc-sleepy
* https://github.com/poc-sleepy

# License

"eGOseRmOToRpHAntOM" is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).
