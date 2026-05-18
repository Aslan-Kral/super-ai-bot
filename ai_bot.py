import telebot
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True)
def cevap(message):
    bot.reply_to(message, "✅ Bot çalışıyor!\nSelam, nasılsın?")

print("✅ EN BASİT BOT ÇALIŞIYOR...")
bot.infinity_polling()
