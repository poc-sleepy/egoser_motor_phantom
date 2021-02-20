# eGOseRmOToRpHAntOM

search tweets and post them to slack

# Requirement

Python Package

- requests 2.25.1
- python-dotenv 0.15.0

API Token

- Your Twitter Bearer
- Your Slack token

# Installation

- Install External Python Package

```bash
pip install -r requirements.txt
```

- Copy `.env.example` to `.env`
- Edit `.env` (You need set `TWITTER_KEY` and `SLACK_TOKEN`)

# Usage

```bash
$ git clone https://github.com/poc-sleepy/egoser_motor_phantom.git
$ cd egoser_motor_phantom
$ pip install -r requirements.txt
$ cp .env.example .env
$ vi .env
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
