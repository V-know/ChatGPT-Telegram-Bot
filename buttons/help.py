from telegram import Update
from telegram.ext import ContextTypes
from config import CHOOSING


async def helper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("Start!")
    await update.message.reply_text("""
    请联系👉 @AiMessagerBot 👈获取更多帮助!
    """, parse_mode="Markdown", disable_web_page_preview=True)
    return CHOOSING
