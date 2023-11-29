from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackContext

from db.MySqlConn import Mysql
from config import CHOOSING


async def show_languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("English", callback_data='lang_en'),
            InlineKeyboardButton("中文", callback_data='lang_cn'),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('Please choose your language:', reply_markup=reply_markup)
    return CHOOSING


async def show_languages_callback_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    nick_name = update.effective_user.full_name

    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    await query.answer()

    lang = query.data.split("_")[1]
    mysql = Mysql()
    mysql.update("update users set nick_name=%s, lang=%s where user_id=%s", (nick_name, lang, user_id))
    mysql.end()

    await query.edit_message_text(
        text="Language changed to 🇬🇧 English" if lang == "en" else "语言已更改为 🇨🇳 中文")
