import telebot
import requests
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ Bot aktif!\nHer şeyi sorabilirsin 👋")

@bot.message_handler(commands=['premium'])
def premium(message):
    bot.reply_to(message, "🌟 Premium yakında!\nŞu anda ücretsiz.")

@bot.message_handler(func=lambda message: True)
def ai_cevap(message):
    bot.reply_to(message, "Düşünüyorum... ⏳")
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": message.text}],
            "temperature": 0.7,
            "max_tokens": 1200
        }
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        cevap = response.json()["choices"][0]["message"]["content"]
        bot.reply_to(message, cevap)
    except:
        bot.reply_to(message, "❌ Hata oldu, tekrar dene.")

print("✅ Bot çalışıyor...")
bot.infinity_polling()
