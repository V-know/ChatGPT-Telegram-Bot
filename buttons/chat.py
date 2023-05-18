from telegram import Update, User
from telegram.ext import ContextTypes
from config import (
    markup,
    token,
    rate_limit,
    context_count,
    CHOOSING,
    logger)
import openai
import emoji
import json
import time
from MySqlConn import Mysql, config


def ChatCompletionsAI(user: User, prompt) -> (str, str):
    mysql = Mysql()
    user_id = user.id
    user_checkin = mysql.getOne(f"select * from users where user_id={user_id}")
    if not user_checkin:
        date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        sql = "insert into users (user_id, name, level, system_content, created_at) values (%s, %s, %s, %s, %s)"
        value = [user_id, user.username, 0, "You are an AI assistant that helps people find information.", date_time]
        mysql.insertOne(sql, value)
    logged_in_user = mysql.getOne(f"select * from users where user_id={user_id}")
    parse_mode = logged_in_user.get("parse_mode")
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
    return parse_mode, reply


async def answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Echo the user message."""
    user_id = update.effective_user.id
    if update.message:
        parse_mode, reply = ChatCompletionsAI(update.effective_user, update.message.text)
        await update.message.reply_text(reply, reply_markup=markup, parse_mode=parse_mode)
    return CHOOSING
