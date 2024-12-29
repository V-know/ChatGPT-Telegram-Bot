from datetime import datetime, timedelta
import aiohttp
import time
from telegram import Update
from telegram.ext import ContextTypes
from db.MySqlConn import Mysql

from buttons import get_project_root
from buttons.templates import image, image_limit, cancel_notification
from chat.ai import GenerateImage
from config import (
    reply_markup,
    cancel_markup,
    CHOOSING,
    image_rate_limit,
    notification_channel,
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
    logged_in_user = mysql.getOne("select * from users where user_id=%s", user_id)

    # Check rate limit
    today = datetime.now().date()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())
    call_count = mysql.getOne(
        "select count(*) as count from image_requests where user_id=%s and created_at between %s and %s",
        (user_id, start_of_day, end_of_day)
    )

    image_prompt = update.message.text.strip()
    if image_prompt in ("取消", "取消重置", "🚫取消", "cancel", "reset", "🚫Cancel"):
        await update.message.reply_text(
            text=cancel_notification[logged_in_user["lang"]], reply_markup=reply_markup, parse_mode='Markdown')
        return CHOOSING
    else:
        level = logged_in_user.get("level")
        if call_count.get("count") >= image_rate_limit[level]:
            await update.message.reply_text(
                text=image_limit[logged_in_user["lang"]], reply_markup=reply_markup, parse_mode='Markdown')
            return CHOOSING

        placeholder_message = await update.message.reply_text("...")
        image_url = await GenerateImage(image_prompt)
        chat_id = update.effective_chat.id

        await context.bot.edit_message_text("Here is your generated image:", chat_id=placeholder_message.chat_id,
                                            message_id=placeholder_message.message_id)
        await context.bot.send_photo(chat_id=chat_id, photo=image_url, reply_markup=reply_markup, parse_mode='Markdown',
                                     disable_web_page_preview=True)

        project_root = get_project_root()
        image_name = f'{nick_name}-{time.strftime("%Y%m%d-%H%M%S")}.jpg'
        save_path = f'{project_root}/data/pictures/{image_name}'

        date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        mysql.insertOne(
            "insert into image_requests (user_id, prompt, image_name, created_at) values (%s, %s,  %s,  %s)",
            (user_id, image_prompt, image_name, date_time))

        mysql.end()
        if notification_channel:
            msg = f"#U{user_id} {nick_name}: {image_prompt}"
            await context.bot.send_photo(chat_id=notification_channel, photo=image_url, caption=msg, )
        await download_image(image_url, save_path)
    return CHOOSING
