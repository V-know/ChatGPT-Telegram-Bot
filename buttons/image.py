import aiohttp
import time
from telegram import Update
from telegram.ext import ContextTypes
from db.MySqlConn import Mysql

from buttons import get_project_root
from buttons.templates import image
from chat.ai import GenerateImage
from config import (
    reply_markup,
    cancel_markup,
    CHOOSING,
    TYPING_IMAGE_PROMPT)


async def download_image(image_url: str, save_path: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status == 200:
                with open(save_path, 'wb') as f:
                    f.write(await response.read())


async def set_image_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    mysql = Mysql()
    user = mysql.getOne("select * from users where user_id=%s", user_id)
    mysql.end()
    await update.message.reply_text(text=image[user["lang"]],
                                    parse_mode='Markdown', disable_web_page_preview=True, reply_markup=cancel_markup)
    return TYPING_IMAGE_PROMPT


async def set_image_prompt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    nick_name = update.effective_user.full_name
    mysql = Mysql()
    user = mysql.getOne("select * from users where user_id=%s", user_id)
    mysql.end()
    # system_content = update.message.text.strip()
    image_prompt = update.message.text.strip()
    if image_prompt in ("取消", "取消重置", "🚫取消", "cancel", "reset", "🚫Cancel"):
        await update.message.reply_text(
            text="已取消。\n您可以继续向我提问了" if user[
                                                        "lang"] == "cn" else "Canceled. \nYou can continue to ask me questions now.",
            reply_markup=reply_markup, parse_mode='Markdown')
    else:
        placeholder_message = await update.message.reply_text("...")
        image_url = await GenerateImage(image_prompt)
        chat_id = update.effective_chat.id

        await context.bot.edit_message_text("Here is your generated image:", chat_id=placeholder_message.chat_id,
                                            message_id=placeholder_message.message_id)
        await context.bot.send_photo(chat_id=chat_id, photo=image_url, reply_markup=reply_markup, parse_mode='Markdown')

        project_root = get_project_root()
        save_path = f'{project_root}/data/pictures/{nick_name}-{time.strftime("%Y%m%d-%H%M%S")}.jpg'
        await download_image(image_url, save_path)
    return CHOOSING
