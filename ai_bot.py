import telebot
import requests
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ Bot aktif!\n\n/premium yazarak premium paketleri gör.")

@bot.message_handler(commands=['premium'])
def premium(message):
    text = """
🌟 <b>Super AI Premium</b>

1 Aylık → 99 TL
3 Aylık → 249 TL
12 Aylık → 799 TL

Ödeme yaptıktan sonra "Ödeme yaptım" yaz + dekont at.
"""
    bot.reply_to(message, text, parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def ai(message):
    if message.text.lower() in ["premium", "/premium", "paket"]:
        return premium(message)
    
    bot.reply_to(message, "Düşünüyorum... ⏳")
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": message.text + " Türkçe cevap ver"}],
            "max_tokens": 1500
        }
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        cevap = r.json()["choices"][0]["message"]["content"]
        bot.reply_to(message, cevap)
    except:
        bot.reply_to(message, "Hata oldu, tekrar dene.")

print("✅ Bot basitleştirildi ve çalışıyor...")
bot.infinity_polling()
