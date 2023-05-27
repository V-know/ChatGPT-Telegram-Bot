#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.
# -*- coding: UTF-8 -*-


from MySqlConn import config
from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    PicklePersistence,
    ConversationHandler,
    CallbackQueryHandler,
    filters)

from config import (
    contact_admin,
    start_button,
    set_sys_content_button,
    reset_context_button,
    statistics_button,
    switch_role_button,
    CHOOSING, TYPING_REPLY, TYPING_SYS_CONTENT
)
from buttons.help import helper
from buttons.start import start
from buttons.role import set_system_content, reset_context, set_system_content_handler
from buttons.statistics import statistics
from chat.handler import answer_handler
from buttons.inline import show_chat_modes_handle, show_chat_modes_callback_handle, set_chat_mode_handle
from buttons.others import non_text_handler, done, error_handler


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    persistence = PicklePersistence(filepath='conversationbot')

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(config["BOT"]["TOKEN"]).persistence(persistence).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex(f'^{contact_admin}$'), helper, ),
                MessageHandler(filters.Regex(f'^({start_button}|/start|Start)$'), start, ),
                MessageHandler(filters.Regex(f"^{reset_context_button}$"), reset_context),
                MessageHandler(filters.Regex(f"^{set_sys_content_button}$"), set_system_content),
                MessageHandler(filters.Regex(f"^{statistics_button}$"), statistics),
                MessageHandler(filters.Regex(f"^{switch_role_button}$"), show_chat_modes_handle),
                MessageHandler(filters.TEXT, answer_handler),
                MessageHandler(filters.ATTACHMENT, non_text_handler),
            ],
            TYPING_REPLY: [
                MessageHandler(filters.Regex(f'^{contact_admin}$'), helper, ),
                MessageHandler(filters.Regex(f'^({start_button}|/start|Start)$'), start, ),
                MessageHandler(filters.Regex(f"^{reset_context_button}$"), reset_context),
                MessageHandler(filters.Regex(f"^{set_sys_content_button}$"), set_system_content),
                MessageHandler(filters.Regex(f"^{statistics_button}$"), statistics),
                MessageHandler(filters.Regex(f"^{switch_role_button}$"), show_chat_modes_handle),
                MessageHandler(filters.TEXT, answer_handler),
                MessageHandler(filters.ATTACHMENT, non_text_handler),
            ],
            TYPING_SYS_CONTENT: [
                MessageHandler(filters.TEXT, set_system_content_handler),
            ],
        },
        fallbacks=[MessageHandler(filters.Regex('^Done$'), done)],
        name="my_conversation",
        persistent=True,
    )
    application.add_handler(conv_handler)

    application.add_handler(CallbackQueryHandler(show_chat_modes_callback_handle, pattern="^show_chat_modes"))
    application.add_handler(CallbackQueryHandler(set_chat_mode_handle, pattern="^set_chat_mode"))
    # ...and the error handler
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
