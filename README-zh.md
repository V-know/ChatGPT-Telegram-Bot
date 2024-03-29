# ChatGPT Telegram Bot

![python-version](https://img.shields.io/badge/python-3.9+-blue.svg)
[![python-telegram-bot-version](https://img.shields.io/badge/PythonTelegramBot-20.3+-critical.svg)](https://github.com/python-telegram-bot/python-telegram-bot/releases/tag/v20.3)
![db](https://img.shields.io/badge/db-MySQL8-ff69b4.svg)
[![openai-version](https://img.shields.io/badge/openai-0.27.6-orange.svg)](https://openai.com/)
[![license](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)
[![bot](https://img.shields.io/badge/TelegramBot-@RoboAceBot-blueviolet.svg)](https://t.me/RoboAceBot)

[English](README.md) | 中文

一个拥有丝滑AI体验的Telegram Bot

## ⚡Feature

[✓] 同时支持Azure OpenAI和原生OpenAI接口

[✓] 实时（流式）返回AI响应的答案，体验更快捷、更丝滑

[✓] 预设15种Bot身份，可快速切换

[✓] 支持自定义Bot身份，满足个性化需求

[✓] 支持上下文件内容一键清空，随时重开会话

[✓] Telegram Bot 原生按钮支持，直观快捷实现需要功能

[✓] 用户等级划分，不同等级享有不同单次会话Token数量、上下文数量和会话频率

[✓] 支持中/英双语切换

[✓] 容器化

[✓] More ...

<p align="center">
  <img src="https://media.giphy.com/media/gqKOf9LOL6xYK1Bmbv/giphy.gif" />
</p> 

## 👨‍💻TODO

[x] 允许用户在Bot中使用自己的OpenAI Key,以获得更多自由

[x] 完善ErrorHandler

## 🤖快速体验

Telegram Bot: [RoboAceBot](https://t.me/RoboAceBot)

## 🛠️部署

### 安装依赖

```shell
pip install -r requirements.txt
```

### 配置数据库

#### 安装数据库

你可以使用下面的命令快速创建本地MySQL数据库

```shell
dcker-compose up -d -f db/docker-dompose.yaml
```

#### 初始化数据库

```shell
mysql -uusername -p -e "source db/database.sql"
```

### 添加配置

需要的所有配置都在`config.yaml`中，文件格式内容，请参考`config.yaml.example`

| Parameter           | Optional | Description                                                                                                 |
|---------------------|----------|-------------------------------------------------------------------------------------------------------------|
| `BOT`.`TOKEN`       | No       | 从[@botFather](https://t.me/BotFather)创建bot并获取Token                                                          |
| `DEVELOPER_CHAT_ID` | No       | bot出错时，接收信息的TG帐号ID, ID可以从[@get_id_bot](https://t.me/get_id_bot) 获取                                          |
| `MYSQL`             | No       | MySQL连接相关的参数                                                                                                |
| `TIME_SPAN`         | No       | 计算rate limit所用的时间窗口大小，单位：分钟                                                                                 |
| `RATE_LIMIT`        | No       | `key`为用户等级，`value`为TIME_SPAN时间内可以聊天的最大数量                                                                    |
| `CONTEXT_COUNT`     | No       | `key`为用户等级，`value`为每次聊天所包含的上下文数量                                                                            |
| `MAX_TOKEN`         | No       | `key`为用户等级, `value`为每次聊天AI返回节点的最大Token数                                                                     |
| `AI`.`TYPE`         | Yes      | 使用的是AI类型，有`openai`和`azure`两个选项，默认为`openai`                                                                  |                           
| `AI`.`BASE`         | Yes      | 从 Azure 门户检查资源时，可在“密钥和终结点”部分中找到此值。 或者，可以在“Azure OpenAI Studio”>“操场”>“代码视图”中找到该值, 仅当`AI`.`TYPE`为`zaure`里需要设置 |
| `AI`.`ENGINE`       | Yes      | Azure OpenAI的Deployment名, 仅当`AI`.`TYPE`为`zaure`时需要设置                                                        |
| `AI`.`VERSION`      | Yes      | Azure OpenAI的版本号, 仅当`AI`.`TYPE`为`zaure`时需要设置                                                                |
| `AI`.`MODEL`        | Yes      | OpenAI所使用的 Model 名, 仅当`AI`.`TYPE`为`openai`时需要设置                                                             |

如果你使用的是Azure的OpenAI，你可在这个链接里获取所需的所有内容：

[开始通过 Azure OpenAI 服务使用 ChatGPT 和 GPT-4](https://learn.microsoft.com/zh-cn/azure/cognitive-services/openai/chatgpt-quickstart?pivots=programming-language-python&tabs=command-line)

## 🚀启动

```shell
python main.py | tee >> debug.log
```

### Docker build & Run

```shell
docker run --rm --name chatgpt-telegram-bot -v ./config.yaml:/app/config.yaml ghcr.io/v-know/chatgpt-telegram-bot:latest
```

### Docker Compose

```shell
docker-compose up -d
```
## ❤️写在最后

希望本项目在给你丝滑AI体验的同时，能帮助更多人接触并开始创建和使用自己的Telegram Bot