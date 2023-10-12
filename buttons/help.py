from telegram import Update
from telegram.ext import ContextTypes
from config import CHOOSING
from db.MySqlConn import Mysql
from buttons.templates import say_help


async def helper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    mysql = Mysql()
    user = mysql.getOne("select * from users where user_id=%s", user_id)
    mysql.end()
    await update.message.reply_text(say_help[user["lang"]], parse_mode="Markdown", disable_web_page_preview=True)
    return CHOOSING
