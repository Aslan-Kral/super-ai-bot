import telebot
import requests
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ Hoş geldin!\nHer şeyi sorabilirsin.\n\n/premium ile premium ol.")

@bot.message_handler(commands=['premium'])
def premium(message):
    text = """
🌟 <b>Super AI Premium</b>

Avantajlar:
• Sınırsız ve hızlı cevap
• Daha kaliteli, uzun yanıtlar
• Öncelikli destek

Fiyat:
• 1 Ay → 99 TL

Ödeme:
Garanti IBAN:
TR02 0006 2000 4700 0006 6276 06

Ödeme yaptıktan sonra "Ödeme yaptım" yaz ve dekontu at.
Hemen premium aktif edeyim.
"""
    bot.reply_to(message, text, parse_mode="HTML")

@bot.message_handler(func=lambda m: "ödeme yaptım" in m.text.lower())
def odeme(message):
    bot.reply_to(message, "✅ Teşekkürler! Dekontu at, ödemeni kontrol edip premium'u hemen aktif edeyim.")

@bot.message_handler(func=lambda message: True)
def ai_cevap(message):
    # Premium komutunu özel olarak ele al
    if message.text.lower() == "/premium":
        return premium(message)
    
    bot.reply_to(message, "Düşünüyorum... ⏳")
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": message.text + " (Türkçe cevap ver)"}],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        cevap = response.json()["choices"][0]["message"]["content"]
        bot.reply_to(message, cevap)
    except:
        bot.reply_to(message, "❌ Hata oldu, lütfen tekrar dene.")

print("✅ Bot çalışıyor...")
bot.infinity_polling()
