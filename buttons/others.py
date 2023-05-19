from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from telegram import (
    Update,
    ReplyKeyboardRemove,
    User)

import time
import json
import openai
import html
import traceback
from typing import Dict

from MySqlConn import config
from config import (
    TYPING_REPLY,
    logger)


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


async def non_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photos and asks for a location."""
    user = update.message.from_user
    if len(update.message.photo) != 0:
        await update.message.reply_text(text='暂不开放图片发送功能！\n请使用文字进行提问！')
        photo_file = await update.message.photo[-1].get_file()
        # can't get photo's name
        await photo_file.download_to_drive(f'./data/photos/{user.name}-{time.strftime("%Y%m%d-%H%M%S")}.jpg')
        logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    else:
        await update.message.reply_text(text='嗯，好像收到了什么奇怪的东西！\n请使用文字进行提问！')
        if update.message.document:
            file = await update.message.document.get_file()
            await file.download_to_drive(f'./data/documents/{user.name}-{time.strftime("%Y%m%d-%H%M%S")}.jpg')
        if update.message.video:
            video = await update.message.video.get_file()
            await video.download_to_drive(f'./data/videos/{user.name}-{time.strftime("%Y%m%d-%H%M%S")}.jpg')
    return TYPING_REPLY


def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f'{key} - {value}' for key, value in user_data.items()]
    return "\n".join(facts).join(['\n', '\n'])


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    if 'choice' in context.user_data:
        del context.user_data['choice']

    await update.message.reply_text(
        f"I learned these facts about you: {facts_to_str(context.user_data)}Until next time!",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=config["DEVELOPER_CHAT_ID"], text=message, parse_mode=ParseMode.HTML
    )
