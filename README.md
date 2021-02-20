# eGOseRmOToRpHAntOM

search tweet and post to slack

# Requirement

- requests 2.25.11
- Twitter Bearer
- Slack token

# Installation

- Install Requests

```bash
pip install requests
```

- Copy settings_template.py to settings.py
- Edit settings.py (You need set TWITTER_KEY and SLACK_TOKEN in settings_template.py)

# Usage

```bash
$ git clone https://github.com/poc-sleepy/egoser_motor_phantom.git
$ cd egoser_motor_phantom
$ cp settings_template.py settings.py
$ vi settings.py
(edit...)
$ python3 main.py
```

# Deploy to AWS Lambda

- Requirements

  - Install Docker
    - Disable `Use gRPC FUSE for file sharing` for permission issue if you're using Docker for Mac
  - Configure AWS credentials

- Install Serverless Framework

```
$ npm install -g serverless
```

- Install node_modules

```
$ npm install
```

- Deploy

```
$ sls deploy
```

# Note

# Author

- poc-sleepy
- https://github.com/poc-sleepy

# License

"eGOseRmOToRpHAntOM" is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).
