"""Telegram command bot. AI replies and paid subscriptions are not implemented."""
import os
import sys


def create_bot(token=None, *, bot_factory=None):
    token = (token if token is not None else os.environ.get("TELEGRAM_BOT_TOKEN", "")).strip()
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN ortam değişkenini ayarlayın.")
    if bot_factory is None:
        from telebot import TeleBot
        bot_factory = TeleBot
    bot = bot_factory(token)

    @bot.message_handler(commands=["start", "help"])
    def start(message):
        bot.reply_to(
            message,
            "👋 <b>Merhaba! Super AI Asistan'a hoş geldin.</b>\n\n"
            "Bu sürüm komut botudur. Yapay zekâ yanıtları henüz bağlı değildir.\n"
            "Üyelik durumunu görmek için /premium yazabilirsin.",
            parse_mode="HTML",
        )

    @bot.message_handler(commands=["premium"])
    def premium(message):
        bot.reply_to(
            message,
            "🌟 <b>Super AI Premium</b>\n\n"
            "Ücretli üyelik henüz kullanıma açılmadı. "
            "Ödeme doğrulama ve üyelik etkinleştirme sistemi hazır değildir.\n"
            "Lütfen bu bot üzerinden ödeme veya dekont göndermeyin.",
            parse_mode="HTML",
        )

    @bot.message_handler(content_types=["text"])
    def unsupported(message):
        bot.reply_to(
            message,
            "Yapay zekâ yanıt servisi henüz bağlı değil. "
            "Kullanılabilir komutlar: /start, /help ve /premium.",
        )

    return bot


def main():
    try:
        bot = create_bot()
    except ValueError:
        print("Bot başlatılamadı: TELEGRAM_BOT_TOKEN eksik veya geçersiz.", file=sys.stderr)
        return 2
    except ImportError:
        print("Bağımlılıklar eksik: pip install -r requirements.txt", file=sys.stderr)
        return 2
    bot.infinity_polling(timeout=20, long_polling_timeout=20)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
