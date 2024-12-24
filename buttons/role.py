from telegram import Update
from telegram.ext import ContextTypes
import time
from db.MySqlConn import Mysql

from buttons.templates import role, context_info, identity_confirmed, cancel_notification
from config import (
    reply_markup,
    cancel_markup,
    context_count,
    CHOOSING,
    TYPING_SYS_CONTENT)


async def set_system_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    mysql = Mysql()
    user = mysql.getOne("select * from users where user_id=%s", user_id)
    mysql.end()
    system_content = user.get(
        "system_content") if user else 'You are an AI assistant that helps people find information.'
    await update.message.reply_text(text=role[user["lang"]].safe_substitute(system_content=system_content),
                                    parse_mode='Markdown', disable_web_page_preview=True, reply_markup=cancel_markup)
    return TYPING_SYS_CONTENT


async def reset_context(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    mysql = Mysql()
    reset_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    mysql.update("update records set reset_at=%s where user_id=%s and reset_at is null", (reset_at, user_id))
    user = mysql.getOne(f"select * from users where user_id={user_id}")
    mysql.end()
    await update.message.reply_text(
        context_info[user["lang"]].safe_substitute(context_count=context_count[user["level"]]), parse_mode="Markdown",
        disable_web_page_preview=True)
    return CHOOSING


async def set_system_content_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    nick_name = update.effective_user.full_name
    mysql = Mysql()
    user = mysql.getOne("select * from users where user_id=%s", user_id)
    mysql.end()
    system_content = update.message.text.strip()
    if system_content in ("取消", "取消重置", "🚫取消", "cancel", "reset"):
        await update.message.reply_text(
            text=cancel_notification[user["lang"]], reply_markup=reply_markup, parse_mode='Markdown')
    else:
        user_id = update.effective_user.id
        mysql = Mysql()
        mysql.update("update users set system_content=%s, nick_name=%s where user_id=%s",
                     (system_content, nick_name, user_id))
        reset_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        mysql.update("update records set reset_at=%s where user_id=%s and reset_at is null", (reset_at, user_id))
        mysql.end()
        await update.message.reply_text(text=identity_confirmed[user["lang"]], reply_markup=reply_markup,
                                        parse_mode='Markdown')
    return CHOOSING
