#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.
# -*- coding: UTF-8 -*-


from MySqlConn import Mysql, config
import logging
import openai
import json
import emoji
import time
import html
import yaml
import traceback

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
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram import (
    Update,
    User,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PicklePersistence,
    ConversationHandler,
    CallbackQueryHandler,
    filters)

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
context_count = {0: 3, 1: 5, 2: 10}
rate_limit = {0: 5, 1: 15, 2: 300}

CHOOSING, TYPING_REPLY, TYPING_SYS_CONTENT = range(3)
contact_admin = "🆘求助"
start_button = "🚀Start"
set_sys_content_button = "🆔自定义角色"
reset_context_button = "🔃重开会话"
statistics_button = "📈用量查询"
switch_role_button = "🙋多角色切换"
reply_keyboard = [
    [contact_admin, start_button],
    [set_sys_content_button, switch_role_button],
    [reset_context_button, statistics_button],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

with open("chat_modes.yml") as f:
    chat_modes = yaml.load(f, Loader=yaml.FullLoader)


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
    time_span = 3  # minutes
    chat_count = mysql.getOne(
        f"select count(*) as count from records where role='user' and created_at >=NOW() - INTERVAL {time_span} MINUTE;")

    if chat_count.get("count") > rate_limit[level]:
        reply = f"请求太快了!{emoji.emojize(':rocket:')}\n" \
                f"您每 {time_span} 分钟最多可向我提问 {rate_limit[level]} 个问题{emoji.emojize(':weary_face:')}\n" \
                f"联系 @AiMessagerBot 获取更多帮助!{emoji.emojize(':check_mark_button:')}\n" \
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

    # Record prompt
    completion_tokens = response["usage"]["completion_tokens"]
    prompt_tokens = response["usage"]["prompt_tokens"]
    # total_tokens = response["usage"]["total_tokens"]
    date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    sql = "insert into records (user_id, role, content, created_at, tokens) " \
          "values (%s, %s, %s, %s, %s)"
    value = [user_id, "user", prompt, date_time, prompt_tokens]
    mysql.insertOne(sql, value)

    # Record response
    response_role = response.get('choices')[0].get('message').get('role')
    response_content = response.get('choices')[0].get('message').get('content')
    date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    value = [user_id, response_role, response_content, date_time, completion_tokens]
    mysql.insertOne(sql, value)
    mysql.end()
    reply = response.get('choices')[0].get('message').get('content')
    if response.get("usage").get("completion_tokens") >= token[level]:
        reply = f"{reply}\n\n答案长度超过了您当前最大{token[level]}个Token的限制\n请联系 @AiMessagerBot 获取更多帮助!" \
                f"{emoji.emojize(':check_mark_button:')}"
    return reply


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"""
        Hej  {user.mention_html()}!
I'm an AI chatbot created to interact with you and make your day a little brighter. If you have any questions or just want to have a friendly chat, I'm here to help! 🤗

Do you know what's great about me? I can help you with anything from giving advice to telling you a joke, and I'm available 24/7! 🕰️

So why not share me with your friends? 😍 
You can send them this link: https://t.me/RoboAceBot

我是一个 AI 聊天机器人。我被创建出来是为了与你互动并让你的生活加美好。如果你有任何问题或只是想友好地聊天，我会在这里帮助你！🤗

我可以帮助你做任何事情，从给你建议到讲笑话，而且我全天候在线！🕰️

快把我分享给你的朋友们吧！😍
你可以将此链接发送给他们：https://t.me/RoboAceBot
        """,
        reply_markup=markup, disable_web_page_preview=True
    )
    return CHOOSING


async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    mysql = Mysql()
    user_id = user.id
    prompt_tokens = mysql.getMany(
        f"select sum(tokens) as tokens from records where user_id={user_id} and role='user'", 1)[0]
    completion_tokens = mysql.getMany(
        f"select sum(tokens) as tokens from records where user_id={user_id} and role='assistant'", 1)[0]

    if not prompt_tokens["tokens"]:
        prompt_tokens["tokens"] = 0
    if not completion_tokens["tokens"]:
        completion_tokens["tokens"] = 0

    await update.message.reply_html(
        rf"""
Hej  {user.mention_html()}!

您当前Token使用情况如下：
查询：{prompt_tokens["tokens"]} Tokens
答案：{completion_tokens["tokens"]} Tokens
总共：{prompt_tokens["tokens"] + completion_tokens["tokens"]} Tokens

祝您生活愉快！🎉
        """,
        reply_markup=markup, disable_web_page_preview=True
    )
    return CHOOSING


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
    请联系👉 @AiMessagerBot 👈获取更多帮助!
    """, parse_mode="Markdown", disable_web_page_preview=True)
    return CHOOSING


async def reset_context(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    mysql = Mysql()
    reset_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    mysql.update("update records set reset_at=%s where user_id=%s and reset_at is null", (reset_at, user_id))
    user = mysql.getOne(f"select * from users where user_id={user_id}")
    mysql.end()
    await update.message.reply_text(f"""
每次提问AI会参考您最近{context_count[user['level']]}次的对话记录为您提供答案！

现在您的会话历史已清空，可以重新开始提问了！
    """, parse_mode="Markdown", disable_web_page_preview=True)
    return CHOOSING


async def set_system_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    mysql = Mysql()
    user = mysql.getOne("select * from users where user_id=%s", user_id)
    mysql.end()
    system_content = user.get(
        "system_content") if user else 'You are an AI assistant that helps people find information.'
    await update.message.reply_text(text=f"""
您当前的系统AI助手身份设置为🤖：

**{system_content}**

请直接回复新的AI助手身份设置！

您可以参考： [🧠ChatGPT 中文调教指南]https://github.com/PlexPt/awesome-chatgpt-prompts-zh

如需取消重置，请直接回复：`取消` 或 `取消重置` ‍🤝‍
    """, parse_mode='Markdown', disable_web_page_preview=True)
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
        """, reply_markup=markup, parse_mode='Markdown')
    return CHOOSING


async def show_chat_modes_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, reply_markup = get_chat_mode_menu(0)
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)


def get_chat_mode_menu(page_index: int):
    n_chat_modes_per_page = 5
    text = f"Select <b>chat mode</b> ({len(chat_modes)} modes available):"

    # buttons
    chat_mode_keys = list(chat_modes.keys())
    page_chat_mode_keys = chat_mode_keys[page_index * n_chat_modes_per_page:(page_index + 1) * n_chat_modes_per_page]

    keyboard = []
    for chat_mode_key in page_chat_mode_keys:
        name = chat_modes[chat_mode_key]["name"]
        keyboard.append([InlineKeyboardButton(name, callback_data=f"set_chat_mode|{chat_mode_key}")])

    # pagination
    if len(chat_mode_keys) > n_chat_modes_per_page:
        is_first_page = (page_index == 0)
        is_last_page = ((page_index + 1) * n_chat_modes_per_page >= len(chat_mode_keys))

        if is_first_page:
            keyboard.append([
                InlineKeyboardButton("»", callback_data=f"show_chat_modes|{page_index + 1}")
            ])
        elif is_last_page:
            keyboard.append([
                InlineKeyboardButton("«", callback_data=f"show_chat_modes|{page_index - 1}"),
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("«", callback_data=f"show_chat_modes|{page_index - 1}"),
                InlineKeyboardButton("»", callback_data=f"show_chat_modes|{page_index + 1}")
            ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    return text, reply_markup


async def show_chat_modes_callback_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    page_index = int(query.data.split("|")[1])
    if page_index < 0:
        return

    text, reply_markup = get_chat_mode_menu(page_index)
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except BadRequest as e:
        if str(e).startswith("Message is not modified"):
            pass


async def set_chat_mode_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id

    query = update.callback_query
    await query.answer()

    system_content = query.data.split("|")[1]

    # db.set_user_attribute(user_id, "current_chat_mode", chat_mode)
    # db.start_new_dialog(user_id)

    mysql = Mysql()
    mysql.update("update users set system_content=%s where user_id=%s", (chat_modes[system_content]['prompt_start'], user_id))
    reset_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    mysql.update("update records set reset_at=%s where user_id=%s and reset_at is null", (reset_at, user_id))
    mysql.end()

    await context.bot.send_message(
        update.callback_query.message.chat.id,
        f"{chat_modes[system_content]['welcome_message']}",
        parse_mode=ParseMode.HTML
    )


async def non_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photos and asks for a location."""
    user = update.message.from_user
    if len(update.message.photo) != 0:
        await update.message.reply_text(text='暂不开放图片发送功能！\n请使用文字进行提问！')
        photo_file = update.message.photo[-1].get_file()
        # can't get photo's name
        photo_file.download(f'./data/photos/{user.name}-{time.strftime("%Y%m%d-%H%M%S")}.jpg')
        logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    else:
        await update.message.reply_text(text='嗯，好像收到了什么奇怪的东西！\n请使用文字进行提问！')
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
                MessageHandler(filters.Regex(f"^{statistics_button}$"), statistics),
                MessageHandler(filters.Regex(f"^{switch_role_button}$"), show_chat_modes_handle),
                MessageHandler(filters.TEXT, answer_handler),
                MessageHandler(filters.ATTACHMENT, non_text_handler),
            ],
            TYPING_REPLY: [
                MessageHandler(filters.Regex(f'^{contact_admin}$'), helper, ),
                MessageHandler(filters.Regex(f'^({start_button}|/start|Start)$'), start, ),
                MessageHandler(filters.Regex(f"^{reset_context_button}$"), reset_context),
                MessageHandler(filters.Regex(f"^{set_sys_content_button}$"), set_system_content),
                MessageHandler(filters.Regex(f"^{statistics_button}$"), statistics),
                MessageHandler(filters.Regex(f"^{switch_role_button}$"), show_chat_modes_handle),
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

    application.add_handler(CallbackQueryHandler(show_chat_modes_callback_handle, pattern="^show_chat_modes"))
    application.add_handler(CallbackQueryHandler(set_chat_mode_handle, pattern="^set_chat_mode"))
    # ...and the error handler
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
