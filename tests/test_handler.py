import asyncio
import json
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from telegram.constants import ChatAction


class TestAnswerHandler(unittest.TestCase):
    def test_converts_commonmark_to_telegram_entities(self):
        from chat.handler import _convert_markdown_for_telegram

        text, entities = _convert_markdown_for_telegram("1. **全球经济不确定性**：价格上涨。")

        self.assertEqual(text, "1. 全球经济不确定性：价格上涨。\n")
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0]["type"], "bold")
        self.assertEqual(
            text[entities[0]["offset"]:entities[0]["offset"] + entities[0]["length"]],
            "全球经济不确定性",
        )
        json.dumps(entities)

    def test_typing_heartbeat_repeats_until_cancelled(self):
        from chat import handler

        bot = SimpleNamespace(send_chat_action=AsyncMock())
        sleep = AsyncMock(side_effect=[None, asyncio.CancelledError()])

        with patch.object(handler.asyncio, "sleep", sleep):
            with self.assertRaises(asyncio.CancelledError):
                asyncio.run(handler._typing_heartbeat(bot, 42))

        bot.send_chat_action.assert_awaited_once_with(
            chat_id=42,
            action=ChatAction.TYPING,
        )

    def test_sends_typing_action_before_processing(self):
        from chat import handler

        update = MagicMock()
        update.effective_user.id = 42
        update.effective_user.full_name = "Test User"
        update.effective_user.username = "test-user"
        update.effective_chat.id = 42
        update.message.text = "Hello"
        events = []

        async def reply_text(*args, **kwargs):
            events.append("placeholder")
            return SimpleNamespace(chat_id=42, message_id=1)

        async def send_chat_action(*args, **kwargs):
            events.append("typing")

        update.message.reply_text = reply_text

        context = SimpleNamespace(
            bot=SimpleNamespace(
                send_chat_action=AsyncMock(side_effect=send_chat_action),
                edit_message_text=AsyncMock(),
                send_message=AsyncMock(),
            )
        )
        mysql = MagicMock()
        mysql.__enter__.return_value.getOne.side_effect = [
            None,
            {
                "parse_mode": "HTML",
                "level": 0,
                "system_content": "You are helpful.",
                "lang": "en",
            },
            {"count": 0},
        ]
        mysql.__enter__.return_value.getMany.return_value = []

        async def replies():
            yield ("**Hi**", "stop")

        with patch.object(handler, "Mysql", return_value=mysql), \
                patch.object(handler, "ChatCompletionsAI", return_value=replies()), \
                patch.object(handler, "rate_limit", [10]), \
                patch.object(handler, "context_count", [10]), \
                patch.object(handler, "reply_markup", None):
            asyncio.run(handler.answer_handler(update, context))

        self.assertGreaterEqual(context.bot.send_chat_action.await_count, 3)
        context.bot.send_chat_action.assert_any_await(
            chat_id=42,
            action=ChatAction.TYPING,
        )
        placeholder_index = events.index("placeholder")
        self.assertEqual(events[placeholder_index - 1:placeholder_index + 2], [
            "typing",
            "placeholder",
            "typing",
        ])
        edit_call = context.bot.edit_message_text.await_args
        self.assertEqual(edit_call.args[0], "Hi")
        self.assertEqual(edit_call.kwargs["entities"][0]["type"], "bold")
        self.assertNotIn("parse_mode", edit_call.kwargs)


if __name__ == "__main__":
    unittest.main()