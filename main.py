#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.
# -*- coding: UTF-8 -*-

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from MySqlConn import Mysql, config
import logging
import openai
import json
import redis
import emoji
import time

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ForceReply, Update, User
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# with open("config.yaml") as f:
#     config = yaml.load(f, Loader=yaml.FullLoader)
cache = redis.Redis(host='localhost', port=6379)
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

fh = logging.FileHandler('main.log')

formatter = logging.Formatter('%(message)s')
fh.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(fh)

token = {0: 256, 1: 1024, 2: 1024}
context_count = {0: 5, 1: 10, 2: 10}
rate_limit = {0: 5, 1: 15, 2: 300}


def ai(user: User, prompt):
    openai.api_key = config["AI"]["TOKEN"]
    max_tokens = 1000 if user.id == 467300857 else 256
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    response["user"] = {"name": user.username,
                        "id": user.id
                        }
    response["prompt"] = prompt
    logger.info(json.dumps(response))

    return response.get('choices')[0].get('text')


def CompletionsAI(user: User, prompt):
    max_tokens = 1000 if user.id == 467300857 else 256
    openai.api_key = config["AI"]["TOKEN"]
    openai.api_type = "azure"
    openai.api_base = "https://openaitrial0417.openai.azure.com/"
    openai.api_version = "2023-03-15-preview"

    response = openai.Completion.create(
        engine="gpt-35-turbo",
        prompt=prompt,
        temperature=0.8,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)
    response["user"] = {"name": user.username,
                        "id": user.id
                        }
    response["prompt"] = prompt
    logger.info(response)

    return response.get("choices")[0].get("text")


def ChatCompletionsAI(user: User, prompt):
    mysql = Mysql()
    user_id = user.id
    user_checkin = mysql.getOne(f"select * from users where user_id={user_id}")
    if not user_checkin:
        date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        sql = "insert into users (user_id, name, level, system_content, created_at) values (%s, %s, %s, %s, %s)"
        value = [user_id, user.username, 0, "You are an AI assistant that helps people find information.", date_time]
        mysql.insertOne(sql, value)
    logged_in_user = mysql.getOne(f"select * from users where user_id={user_id}")
    # VIP level
    level = logged_in_user.get("level")

    # Rate limit controller
    key = 'user:{}:requests'.format(user_id)
    count = cache.incr(key)
    cache.expire(key, 180)
    if count > rate_limit[level]:
        reply = f"请求太快了!{emoji.emojize(':rocket:')}\n" \
                f"您每3分钟最多可向我提供 {rate_limit[level]} 个问题{emoji.emojize(':weary_face:')}\n" \
                f"联系 @JarvisMessagerBot 获取更多!{emoji.emojize(':check_mark_button:')}\n" \
                f"或稍后再试！"
        return reply

    # Init messages
    records = mysql.getMany(f"select * from records where user_id={user_id} and reset_at is null order by id desc",
                            context_count[level])

    messages = []
    if records:
        for record in records:
            messages.append({"role": record["role"], "content": record["content"]})
        messages.reverse()
    messages.insert(0, {"role": "system", "content": logged_in_user["system_content"]})
    messages.append({"role": "user", "content": prompt}),

    # Record prompt
    date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    sql = "insert into records (user_id, role, content, created_at) values (%s, %s, %s, %s)"
    value = [user_id, "user", prompt, date_time]
    mysql.insertOne(sql, value)

    # Setup AI
    openai.api_key = config["AI"]["TOKEN"]
    openai.api_type = "azure"
    openai.api_base = "https://openaitrial0417.openai.azure.com/"
    openai.api_version = "2023-03-15-preview"

    response = openai.ChatCompletion.create(
        engine="gpt-35-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=token[level],
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)

    response["user"] = {"name": user.username,
                        "id": user.id
                        }
    response["prompt"] = prompt
    logger.info(json.dumps(response))

    # Record response
    response_role = response.get('choices')[0].get('message').get('role')
    response_content = response.get('choices')[0].get('message').get('content')
    date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    value = [user_id, response_role, response_content, date_time]
    mysql.insertOne(sql, value)
    mysql.end()
    return response.get('choices')[0].get('message').get('content')


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hej  {user.mention_html()}!",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    user_id = update.effective_user.id
    if update.message:
        reply = ChatCompletionsAI(update.effective_user, update.message.text)
        await update.message.reply_text(reply, parse_mode='Markdown')


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(config["BOT"]["TOKEN"]).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e. message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
