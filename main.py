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

import logging
import openai
import yaml
import json

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

with open("config.yaml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

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


def ai(user: User, prompt):
    openai.api_key = config["AI"]["TOKEN"]
    max_tokens = 4000 if user.id == 467300857 else 256
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


def chatCompletionAI(user: User, prompt):
    max_tokens = 4000 if user.id == 467300857 else 256
    openai.api_key = config["AI"]["TOKEN"]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0301",
        messages=[
            # {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
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

    return response.get("choices")[0].get("message").get("content")


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    if update.message:
        await update.message.reply_text(chatCompletionAI(update.effective_user, update.message.text), parse_mode='Markdown')


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(config["BOT"]["TOKEN"]).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()

