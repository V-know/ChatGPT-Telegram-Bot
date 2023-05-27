# ChatGPT Telegram Bot

![python-version](https://img.shields.io/badge/python-3.9+-blue.svg)
[![python-telegram-bot-version](https://img.shields.io/badge/PythonTelegramBot-20.3+-critical.svg)](https://github.com/python-telegram-bot/python-telegram-bot/releases/tag/v20.3)
![db](https://img.shields.io/badge/db-MySQL8-ff69b4.svg)
[![openai-version](https://img.shields.io/badge/openai-0.27.6-orange.svg)](https://openai.com/)
[![license](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)
[![bot](https://img.shields.io/badge/TelegramBot-@RoboAceBot-blueviolet.svg)](https://t.me/RoboAceBot)

一个拥有丝滑AI体验的Telegram Bot

## ⚡Feature

[✓] 支持Azure OpenAI接口(原生OpenAI接口 Coming soon)

[✓] 实时（流式）返回AI响应的答案，体验更快捷、更丝滑

[✓] 预设15种Bot身份，可快速切换

[✓] 支持自定义Bot身份，满足个性化需求

[✓] 支持上下文件内容一键清空，随时重开会话

[✓] Telegram Bot 原生按钮支持，直观快捷实现需要功能

[✓] 用户等级划分，不同等级享有不同单次会话Token数量、上下文数量和会话频率

[✓] More ...

## 👨‍💻TODO

[x] 支持原生OpenAI接口（WIP）

[x] 允许用户在Bot中使用自己的OpenAI Key,以获得更多自由

[x] 完善ErrorHandler

[x] 容器化

## 🤖快速体验

Telegram Bot: [RoboAceBot](https://t.me/RoboAceBot)

## 🛠️部署

### 安装依赖

```shell
pip install -r requirements.txt
```

### 添加配置

需要的所有配置都在`config.yaml`中，文件格式内容，请参考`config.yaml.example`

| Parameter         | Description                                                        |
|-------------------|--------------------------------------------------------------------|
| BOT.TOKEN         | 从[@botFather](https://t.me/BotFather)创建bot并获取Token                 |
| DEVELOPER_CHAT_ID | bot出错时，接收信息的TG帐号ID, ID可以从[@get_id_bot](https://t.me/get_id_bot) 获取 |

如果你使用的是Azure的OpenAI，你可在这个链接里获取所需的所有内容：

[开始通过 Azure OpenAI 服务使用 ChatGPT 和 GPT-4](https://learn.microsoft.com/zh-cn/azure/cognitive-services/openai/chatgpt-quickstart?pivots=programming-language-python&tabs=command-line)

## 🚀启动

```shell
python main.py | tee >> debug.log
```