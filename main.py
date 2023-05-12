#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.
# -*- coding: UTF-8 -*-


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
from typing import Dict
from telegram import (
    Update,
    User,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PicklePersistence,
    ConversationHandler,
    filters)

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

CHOOSING, TYPING_REPLY, TYPING_SYS_CONTENT = range(3)
contact_admin = emoji.emojize(':SOS_button:求助')
start_button = emoji.emojize(':rocket:Start')
set_sys_content_button = emoji.emojize(':ID_button:设置身份')
reset_context_button = emoji.emojize(":clockwise_vertical_arrows:遗忘会话")
reply_keyboard = [
    [reset_context_button, start_button],
    [set_sys_content_button, contact_admin],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


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


def ChatCompletionsAI(user: User, prompt) -> str:
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
                f"联系 @JarvisMessagerBot 获取更多帮助!{emoji.emojize(':check_mark_button:')}\n" \
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
    print(messages)

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
    reply = response.get('choices')[0].get('message').get('content')
    if response.get("usage").get("completion_tokens") >= token[level]:
        reply = f"{reply}\n\n答案长度超过了您当前最大{token[level]}个Token的限制\n请联系 @JarvisMessagerBot 获取更多帮助!" \
                f"{emoji.emojize(':check_mark_button:')}"
    return reply


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"""
        Hej  {user.mention_html()}!",
I'm an AI chatbot created to interact with you and make your day a little brighter. If you have any questions or just want to have a friendly chat, I'm here to help! 🤗

Do you know what's great about me? I can help you with anything from giving advice to telling you a joke, and I'm available 24/7! 🕰️

So why not share me with your friends? 😍 
You can send them this link: https://t.me/RoboAceBot
        """,
        reply_markup=markup, disable_web_page_preview=True
    )
    return CHOOSING


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!", reply_markup=markup, parse_mode='Markdown')


async def answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Echo the user message."""
    user_id = update.effective_user.id
    if update.message:
        reply = ChatCompletionsAI(update.effective_user, update.message.text)
        await update.message.reply_text(reply, reply_markup=markup, parse_mode='Markdown')
    return CHOOSING


async def helper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("Start!")
    await update.message.reply_text("""
    请联系👉 @JarvisMessagerBot 👈获取更多帮助!
    """, parse_mode="Markdown", disable_web_page_preview=True)
    return CHOOSING


async def reset_context(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    mysql = Mysql()
    reset_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    mysql.update("update records set reset_at=%s where user_id=%s and reset_at is null", (reset_at, user_id))
    mysql.end()
    await update.message.reply_text("""
    您的会话历史已清空，现在可以重新开始提问了！
    """, parse_mode="Markdown", disable_web_page_preview=True)
    return CHOOSING


async def set_system_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    mysql = Mysql()
    user = mysql.getOne("select * from users where user_id=%s", user_id)
    mysql.end()
    await update.message.reply_text(text=f"""
您当前的系统AI助手身份设置为🤖：

**{user["system_content"]}**

请直接回复新的AI助手身份设置！

您可以参考： [🧠ChatGPT 中文调教指南]https://github.com/PlexPt/awesome-chatgpt-prompts-zh

如需取消重置，请直接回复：`取消` 或 `取消重置` ‍🤝‍
    """,
                                    parse_mode='Markdown', disable_web_page_preview=True)
    return TYPING_SYS_CONTENT


async def set_system_content_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    system_content = update.message.text.strip()
    if system_content in ("取消", "取消重置"):
        await update.message.reply_text(text="已取消。\n您可以继续向我提问了",
                                        reply_markup=markup, parse_mode='Markdown')
    else:
        user_id = update.effective_user.id
        mysql = Mysql()
        mysql.update("update users set system_content=%s where user_id=%s", (system_content, user_id))
        reset_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        mysql.update("update records set reset_at=%s where user_id=%s and reset_at is null", (reset_at, user_id))
        mysql.end()
        await update.message.reply_text(text=f"""
新的AI助手身份已确认。
我将以新身份为背景来为您解答问题。
您现在可以开始提问了！
        """,
                                        reply_markup=markup, parse_mode='Markdown')
    return CHOOSING


async def non_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photos and asks for a location."""
    user = update.message.from_user
    if len(update.message.photo) != 0:
        await update.message.reply_text(text='暂不开放图片发送功能，以免被苹果封！\n请使用文字或Emoji来表达你自己！')
        photo_file = update.message.photo[-1].get_file()
        # can't get photo's name
        photo_file.download(f'./data/photos/{user.name}-{time.strftime("%Y%m%d-%H%M%S")}.jpg')
        logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    else:
        await update.message.reply_text(text='嗯，好像收到了什么奇怪的东西！\n请使用文字或Emoji来表达你自己！')
        if update.message.document:
            file = update.message.document
            file.get_file().download(f'./data/documents/{user.name}-{file.file_name}')
        if update.message.video:
            video = update.message.video
            video.get_file().download(f'./data/videos/{user.name}-{video.file_name}')
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


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    persistence = PicklePersistence(filepath='conversationbot')

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(config["BOT"]["TOKEN"]).persistence(persistence).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex(f'^{contact_admin}$'), helper, ),
                MessageHandler(filters.Regex(f'^({start_button}|/start|Start)$'), start, ),
                MessageHandler(filters.Regex(f"^{reset_context_button}$"), reset_context),
                MessageHandler(filters.Regex(f"^{set_sys_content_button}$"), set_system_content),
                MessageHandler(filters.TEXT, answer_handler),
                MessageHandler(filters.ATTACHMENT, non_text_handler),
            ],
            TYPING_REPLY: [
                MessageHandler(filters.Regex(f'^{contact_admin}$'), helper, ),
                MessageHandler(filters.Regex(f'^({start_button}|/start|Start)$'), start, ),
                MessageHandler(filters.Regex(f"^{reset_context_button}$"), reset_context),
                MessageHandler(filters.Regex(f"^{set_sys_content_button}$"), set_system_content),
                MessageHandler(filters.TEXT, answer_handler),
                MessageHandler(filters.ATTACHMENT, non_text_handler),
            ],
            TYPING_SYS_CONTENT: [
                MessageHandler(filters.TEXT, set_system_content_handler),
            ],
        },
        fallbacks=[MessageHandler(filters.Regex('^Done$'), done)],
        name="my_conversation",
        persistent=True,
    )
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
