from telegram import Update
from telegram.ext import ContextTypes
import time
from db.MySqlConn import Mysql

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
    await update.message.reply_text(text=f"""
您当前的系统AI助手身份设置为🤖：

**{system_content}**

请直接回复新的AI助手身份设置！

您可以参考： [🧠ChatGPT 中文调教指南]https://github.com/PlexPt/awesome-chatgpt-prompts-zh

如需取消重置，请直接回复：`取消` 或 `取消重置` ‍🤝‍
    """, parse_mode='Markdown', disable_web_page_preview=True, reply_markup=cancel_markup)
    return TYPING_SYS_CONTENT


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


async def set_system_content_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    system_content = update.message.text.strip()
    if system_content in ("取消", "取消重置", "🚫取消"):
        await update.message.reply_text(text="已取消。\n您可以继续向我提问了",
                                        reply_markup=reply_markup, parse_mode='Markdown')
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
        """, reply_markup=reply_markup, parse_mode='Markdown')
    return CHOOSING
