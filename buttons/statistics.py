from telegram import Update
from telegram.ext import ContextTypes
from db.MySqlConn import Mysql
from config import (
    markup,
    CHOOSING)


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
