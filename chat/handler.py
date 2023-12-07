from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest
import asyncio
import re

from chat.ai import ChatCompletionsAI
import time
import emoji

from db.MySqlConn import Mysql
from buttons.templates import token_limit
from config import (
    token,
    reply_markup,
    CHOOSING,
    rate_limit,
    time_span,
    notification_channel,
    context_count)


async def answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    prompt = update.message.text
    user_id = user.id
    nick_name = user.full_name
    mysql = Mysql()

    user_checkin = mysql.getOne(f"select * from users where user_id={user_id}")
    if not user_checkin:
        date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        sql = "insert into users (user_id, name, nick_name level, system_content, created_at) values (%s, %s, %s, %s, %s, %s)"
        value = [user_id, user.username, nick_name, 0, "You are an AI assistant that helps people find information.",
                 date_time]
        mysql.insertOne(sql, value)

    if user_checkin and not user_checkin.get("nick_name"):
        mysql.update("update users set nick_name=%s where user_id=%s", (nick_name, user_id))

    logged_in_user = mysql.getOne(f"select * from users where user_id={user_id}")
    parse_mode = logged_in_user.get("parse_mode")
    # VIP level
    level = logged_in_user.get("level")

    # Rate limit controller
    chat_count = mysql.getOne(
        f"select count(*) as count from records where role='user' and created_at >=NOW() - INTERVAL {time_span} MINUTE;")

    if chat_count.get("count") > rate_limit[level]:
        reply = f"请求太快了!{emoji.emojize(':rocket:')}\n" \
                f"您每 {time_span} 分钟最多可向我提问 {rate_limit[level]} 个问题{emoji.emojize(':weary_face:')}\n" \
                f"联系 @AiMessagerBot 获取更多帮助!{emoji.emojize(':check_mark_button:')}\n" \
                f"或稍后再试！"
        await update.message.reply_text(reply, reply_markup=reply_markup)
        return CHOOSING

    placeholder_message = await update.message.reply_text("...")
    # Init messages
    records = mysql.getMany(f"select * from records where user_id={user_id} and reset_at is null order by id desc",
                            context_count[level])
    if update.message:
        messages = []
        prompt_tokens = 0
        if records:
            for record in records:
                messages.append({"role": record["role"], "content": record["content"]})
                prompt_tokens += count_tokens(record["content"])
            messages.reverse()
        messages.insert(0, {"role": "system", "content": logged_in_user["system_content"]})
        prompt_tokens += count_tokens(logged_in_user["system_content"])
        messages.append({"role": "user", "content": prompt})
        prompt_tokens += count_tokens(prompt)

        replies = ChatCompletionsAI(logged_in_user, messages)
        prev_answer = ""
        index = 0
        answer = ""
        async for reply in replies:
            index += 1
            answer, status = reply
            if abs(count_tokens(answer) - count_tokens(prev_answer)) < 30 and status is None:
                continue
            prev_answer = answer
            try:
                if status == "length":
                    answer = token_limit[user_checkin["lang"]].safe_substitute(answer=answer, max_token=token[level])
                elif status == "content_filter":
                    answer = f"{answer}\n\nAs an AI assistant, please ask me appropriate questions!！\nPlease contact @AiMessagerBot for more help!" \
                             f"{emoji.emojize(':check_mark_button:')}"
                await context.bot.edit_message_text(answer, chat_id=placeholder_message.chat_id,
                                                    message_id=placeholder_message.message_id,
                                                    parse_mode=parse_mode, disable_web_page_preview=True)
            except BadRequest as e:
                if str(e).startswith("Message is not modified"):
                    continue
                else:
                    await context.bot.edit_message_text(answer, chat_id=placeholder_message.chat_id,
                                                        message_id=placeholder_message.message_id)
            await asyncio.sleep(0.01)  # wait a bit to avoid flooding

        date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        sql = "insert into records (user_id, role, content, created_at, tokens) " \
              "values (%s, %s, %s, %s, %s)"
        value = [user_id, "user", prompt, date_time, prompt_tokens]
        mysql.insertOne(sql, value)

        value = [user_id, 'assistant', answer, date_time, count_tokens(answer)]
        mysql.insertOne(sql, value)
        mysql.end()
        if notification_channel:
            msg = f"#U{user_id}: {prompt} \n#Jarvis : {answer}"
            await context.bot.send_message(chat_id=notification_channel, text=msg)
            # parse_mode=parse_mode)  # reply_markup=markup)
    return CHOOSING


def count_tokens(text):
    # 使用正则表达式匹配中文汉字、英文单词和标点符号
    pattern = r"[\u4e00-\u9fa5]|[a-zA-Z]+|[^\s\w]"
    tokens = re.findall(pattern, text)

    # 计算token数量
    token_count = len(tokens)

    return token_count
