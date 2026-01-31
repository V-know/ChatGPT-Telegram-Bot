from telegram import Update
from telegram.ext import ContextTypes
import time

from config import (
    reply_markup,
    CHOOSING)
from db.MySqlConn import Mysql


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    user_id = user.id
    nick_name = user.full_name

    with Mysql() as mysql:
        user_checkin = mysql.getOne("select * from users where user_id=%s", (user_id,))
        if not user_checkin:
            date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            sql = "insert into users (user_id, name, nick_name, level, system_content, created_at) values (%s, %s, %s, %s, %s, %s)"
            value = [user_id, user.username, nick_name, 0, "You are an AI assistant that helps people find information.", date_time]
            mysql.insertOne(sql, value)
        if user_checkin and not user_checkin.get("nick_name"):
            mysql.update("update users set nick_name=%s where user_id=%s", (nick_name, user_id))

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
        reply_markup=reply_markup, disable_web_page_preview=True
    )
    return CHOOSING
