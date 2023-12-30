# ChatGPT Telegram Bot

![python-version](https://img.shields.io/badge/python-3.9+-blue.svg)
[![python-telegram-bot-version](https://img.shields.io/badge/PythonTelegramBot-20.3+-critical.svg)](https://github.com/python-telegram-bot/python-telegram-bot/releases/tag/v20.3)
![db](https://img.shields.io/badge/db-MySQL8-ff69b4.svg)
[![openai-version](https://img.shields.io/badge/openai-0.27.6-orange.svg)](https://openai.com/)
[![license](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)
[![bot](https://img.shields.io/badge/TelegramBot-@RoboAceBot-blueviolet.svg)](https://t.me/RoboAceBot)

English | [中文](README-zh.md)

A Telegram bot with a smooth AI experience.

## ⚡Feature

[✓] Support for both Azure OpenAI and native OpenAI.

[✓] Real-time (streaming) response to AI, with faster and smoother experience.

[✓] 15 preset bot identities that can be quickly switched.

[✓] Support for custom bot identities to meet personalized needs.

[✓] Support to clear the contents of the chat with a single click, and restart the conversation at any time.

[✓]Native Telegram bot button support, making it easy and intuitive to implement required functions.

[✓] User level division, with different levels enjoying different single session token numbers, context numbers, and session frequencies.

[✓] Support English and Chinese on UI

[x] Containerization.

[✓] More...

<p align="center">
  <img src="https://media.giphy.com/media/gqKOf9LOL6xYK1Bmbv/giphy.gif" />
</p> 

## 👨‍💻TODO

[x] Allow users to use their own OpenAI Key in the bot to gain more freedom.

[x] Improve ErrorHandler.

## 🤖Quick Experience

Telegram Bot: [RoboAceBot](https://t.me/RoboAceBot)

## 🛠️Deployment

### Install Dependencies

```shell
pip install -r requirements.txt
```

### Configure Database

#### Install Database

You can quickly create a local MySQL database using:

```shell
docker-compose up -d -f db/docker-compose.yaml
```

#### Initialize Database

```shell
mysql -uusername -p -e "source db/database.sql"
```

### Add Configuration

All the required configurations are in `config.yaml`, please refer to `config.yaml.example` for file format and content.

| Parameter           | Optional | Description                                                                                                                                                                                                                                                 |
|---------------------|----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `BOT`.`TOKEN`       | No       | Create a bot from [@botFather](https://t.me/BotFather) and get the Token.                                                                                                                                                                                   |
| `DEVELOPER_CHAT_ID` | No       | Telegram account ID that receives messages when the bot encounters an error. You can use [@get_id_bot](https://t.me/get_id_bot) to get your ID.                                                                                                             |
| `MYSQL`             | No       | Parameters related to MySQL connection.                                                                                                                                                                                                                     |
| `TIME_SPAN`         | No       | The time window size used to calculate the ratelimit, in minutes.                                                                                                                                                                                           |
| `RATE_LIMIT`        | No       | `key` is the user level, and `value` is the maximum number of chats that can be made within the TIME_SPAN time period.                                                                                                                                      |
| `CONTEXT_COUNT`     | No       | `key` is the user level, and `value` is the number of contexts included in each chat.                                                                                                                                                                       |
| `MAX_TOKEN`         | No       | `key` is the user level, and `value` is the maximum number of tokens returned by the AI per chat.                                                                                                                                                           |
| `AI`.`TYPE`         | Yes      | The type of AI used, with two options: `openai` and `azure`. The default is `openai`.                                                                                                                                                                       |                           
| `AI`.`BASE`         | Yes      | When checking resources from the Azure portal, this value can be found in the "Keys and Endpoints" section. Alternatively, this value can be found in "Azure OpenAI Studio" > "Playground" > "Code View". Only needs to be set when `AI`.`TYPE` is `azure`. |
| `AI`.`ENGINE`       | Yes      | The deployment name of Azure OpenAI, only needs to be set when `AI`.`TYPE` is `azure`.                                                                                                                                                                      |
| `AI`.`VERSION`      | Yes      | The version number of Azure OpenAI, only needs to be set when `AI`.`TYPE`is `azure`.                                                                                                                                                                        |

If you are using Azure's OpenAI, you can obtain all the required content at this link:

[Get started using ChatGPT and GPT-4 with Azure OpenAI Services](https://learn.microsoft.com/zh-cn/azure/cognitive-services/openai/chatgpt-quickstart?pivots=programming-language-python&tabs=command-line)

## 🚀Start

```shell
python main.py | tee >> debug.log
```

### Docker build & Run
```shell
docker run --rm --name chatgpt-telegram-bot -v ./config.yaml:/app/config.yaml vividone/chatgpt-telegram-bot:latest 
```

### Docker Compose
```shell
docker-compose up -d
```

## ❤️In Conclusion

I hope this project can provide you with a smooth AI experience and help more people create and use their own Telegram bots.