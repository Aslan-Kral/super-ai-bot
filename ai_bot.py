import telebot
import os
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Basit premium takibi (daha sonra veritabanı yaparız)
premium_users = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ Hoş geldin!\nHer şeyi sorabilirsin.\n\n/premium ile premium üye ol.")

@bot.message_handler(commands=['premium'])
def premium(message):
    text = """
🌟 <b>Super AI Premium</b>

Avantajlar:
• Sınırsız ve hızlı cevap
• Daha kaliteli, uzun yanıtlar
• Öncelikli destek

Fiyat:
• 1 Ay → 9.99€ / 99 TL

Ödeme için:
👉 Garanti IBAN veya Papara linki (senin linkini buraya yaz)

Ödeme yaptıktan sonra "Ödeme yaptım" yaz + dekont at.
Admin seni onaylasın.
"""
    bot.reply_to(message, text, parse_mode="HTML")

@bot.message_handler(func=lambda m: "ödeme yaptım" in m.text.lower())
def odeme_kontrol(message):
    bot.reply_to(message, "✅ Ödemeni aldım. Kontrol ediyorum...\n\nEn kısa sürede premium aktif edilecek. Teşekkürler!")

@bot.message_handler(func=lambda message: True)
def ai_cevap(message):
    bot.reply_to(message, "Düşünüyorum... ⏳")
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": message.text}],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        cevap = response.json()["choices"][0]["message"]["content"]
        bot.reply_to(message, cevap)
    except:
        bot.reply_to(message, "Hata oldu, tekrar dene.")

print("✅ Bot Premium modunda çalışıyor...")
bot.infinity_polling()
