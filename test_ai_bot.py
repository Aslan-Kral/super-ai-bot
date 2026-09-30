import os
import unittest
from unittest.mock import patch
import ai_bot


class FakeBot:
    def __init__(self, token):
        self.token = token
        self.handlers = {}
        self.replies = []

    def message_handler(self, **filters):
        def register(handler):
            key = tuple(filters.get("commands", filters.get("content_types", [])))
            self.handlers[key] = handler
            return handler
        return register

    def reply_to(self, message, text, **options):
        self.replies.append((message, text, options))


class BotTests(unittest.TestCase):
    def test_missing_token_stops_before_constructing_client(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                ai_bot.create_bot(bot_factory=lambda _: self.fail("client created"))

    def test_env_token_and_handlers(self):
        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "  sample-token  "}):
            bot = ai_bot.create_bot(bot_factory=FakeBot)
        self.assertEqual(bot.token, "sample-token")
        self.assertEqual(set(bot.handlers), {("start", "help"), ("premium",), ("text",)})

    def test_commands_reply_without_claiming_ai_or_paid_activation(self):
        bot = ai_bot.create_bot("sample-token", bot_factory=FakeBot)
        bot.handlers[("start", "help")]("message")
        self.assertIn("henüz bağlı değildir", bot.replies[-1][1])
        bot.handlers[("premium",)]("message")
        self.assertIn("henüz kullanıma açılmadı", bot.replies[-1][1])
        self.assertNotIn("IBAN", bot.replies[-1][1])
        self.assertEqual(bot.replies[-1][2]["parse_mode"], "HTML")
        bot.handlers[("text",)]("message")
        self.assertIn("/help", bot.replies[-1][1])

    def test_main_uses_polling_only_when_explicitly_started(self):
        with patch("ai_bot.create_bot") as factory:
            self.assertEqual(ai_bot.main(), 0)
            factory.return_value.infinity_polling.assert_called_once_with(
                timeout=20, long_polling_timeout=20)

    def test_bad_configuration_does_not_poll_or_expose_secret(self):
        with patch("ai_bot.create_bot", side_effect=ValueError("secret-token")):
            with patch("sys.stderr") as stderr:
                self.assertEqual(ai_bot.main(), 2)
                self.assertNotIn("secret-token", str(stderr.write.call_args_list))


if __name__ == "__main__":
    unittest.main()
