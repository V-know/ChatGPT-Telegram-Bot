from telegram import Update
from telegram.ext import ContextTypes
from config import CHOOSING


async def helper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("""
如遇功能异常，请输入： /start 或重启 Bot 进行重置

或
    
联系👉 @AiMessagerBot 👈获取更多帮助!
    """, parse_mode="Markdown", disable_web_page_preview=True)
    return CHOOSING
