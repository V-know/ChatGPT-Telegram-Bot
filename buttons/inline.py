from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton)
import yaml
import time

from db.MySqlConn import Mysql
from config import reply_markup


async def show_chat_modes_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, inline_reply_markup = get_chat_mode_menu(0)
    # placeholder_message = await update.message.reply_text("...", reply_markup=ReplyKeyboardRemove())
    #
    # await context.bot.deleteMessage(chat_id=placeholder_message.chat_id,
    #                                 message_id=placeholder_message.message_id)
    await update.message.reply_text(text, reply_markup=inline_reply_markup, parse_mode=ParseMode.HTML)


with open("chat_modes.yml") as f:
    chat_modes = yaml.load(f, Loader=yaml.FullLoader)


def get_chat_mode_menu(page_index: int):
    n_chat_modes_per_page = 5
    text = f"Select <b>chat mode</b> ({len(chat_modes)} modes available):"

    # buttons
    chat_mode_keys = list(chat_modes.keys())
    page_chat_mode_keys = chat_mode_keys[page_index * n_chat_modes_per_page:(page_index + 1) * n_chat_modes_per_page]

    keyboard = []
    for chat_mode_key in page_chat_mode_keys:
        name = chat_modes[chat_mode_key]["name"]
        keyboard.append([InlineKeyboardButton(name, callback_data=f"set_chat_mode|{chat_mode_key}")])

    # pagination
    if len(chat_mode_keys) > n_chat_modes_per_page:
        is_first_page = (page_index == 0)
        is_last_page = ((page_index + 1) * n_chat_modes_per_page >= len(chat_mode_keys))

        if is_first_page:
            keyboard.append([
                InlineKeyboardButton("»", callback_data=f"show_chat_modes|{page_index + 1}")
            ])
        elif is_last_page:
            keyboard.append([
                InlineKeyboardButton("«", callback_data=f"show_chat_modes|{page_index - 1}"),
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("«", callback_data=f"show_chat_modes|{page_index - 1}"),
                InlineKeyboardButton("»", callback_data=f"show_chat_modes|{page_index + 1}")
            ])
    keyboard.append([InlineKeyboardButton("🚫取消切换", callback_data="cancel")])

    inline_reply_markup = InlineKeyboardMarkup(keyboard)

    return text, inline_reply_markup


async def show_chat_modes_callback_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    page_index = int(query.data.split("|")[1])
    if page_index < 0:
        return

    text, reply_markup = get_chat_mode_menu(page_index)
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except BadRequest as e:
        if str(e).startswith("Message is not modified"):
            pass


async def set_chat_mode_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id

    query = update.callback_query
    await query.answer()

    system_content = query.data.split("|")[1]

    mysql = Mysql()
    mysql.update("update users set system_content=%s, parse_mode=%s where user_id=%s",
                 (chat_modes[system_content]['prompt_start'], chat_modes[system_content]["parse_mode"], user_id))
    reset_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    mysql.update("update records set reset_at=%s where user_id=%s and reset_at is null", (reset_at, user_id))
    mysql.end()

    await context.bot.send_message(
        update.callback_query.message.chat.id,
        f"{chat_modes[system_content]['welcome_message']}",
        parse_mode=ParseMode.HTML, reply_markup=reply_markup
    )


async def cancel_chat_mode_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        update.callback_query.message.chat.id,
        text="已取消。\n您可以继续向我提问了",
        parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
    )
