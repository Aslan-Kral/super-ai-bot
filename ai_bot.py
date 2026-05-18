import telebot
import requests
import os
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Premium kullanıcı takibi
premium_users = {}      # user_id: expiry_date
pending_payments = {}   # user_id: {"amount": , "date": }

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Hoş geldin!\n\n/premium yazarak premium paketleri görebilirsin.")

@bot.message_handler(commands=['premium'])
def premium(message):
    text = """
🌟 <b>Super AI Premium Paketleri</b>

1️⃣ <b>1 Aylık</b> → 99 TL
   • Sınırsız kullanım
   • Daha uzun ve kaliteli cevaplar

2️⃣ <b>3 Aylık</b> → 249 TL (indirimli)
   • En çok tercih edilen

3️⃣ <b>12 Aylık</b> → 799 TL (çok indirimli)

Ödeme Yöntemi:
Garanti IBAN:
TR02 0006 2000 4700 0006 6276 06

Ödeme yaptıktan sonra:
"Ödeme yaptım" yaz + dekontu at.
Hemen kontrol edip premium'u aktif ediyorum.
"""
    bot.reply_to(message, text, parse_mode="HTML")

@bot.message_handler(func=lambda m: "ödeme yaptım" in m.text.lower())
def odeme_bildir(message):
    user_id = message.from_user.id
    pending_payments[user_id] = {"date": datetime.now()}
    bot.reply_to(message, "✅ Dekontunu aldım. Kontrol ediyorum...\n\nOnaylandıktan sonra premium otomatik aktif olacak.")

def is_premium(user_id):
    if user_id in premium_users and datetime.now() < premium_users[user_id]:
        return True
    return False

@bot.message_handler(func=lambda message: True)
def ai_cevap(message):
    user_id = message.from_user.id
    premium = is_premium(user_id)

    bot.reply_to(message, "Düşünüyorum... ⏳")
    
    try:
        extra = " Çok detaylı, uzun ve yaratıcı Türkçe cevap ver." if premium else " Türkçe cevap ver."
        
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": message.text + extra}],
            "temperature": 0.7,
            "max_tokens": 2500 if premium else 1200
        }
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        cevap = response.json()["choices"][0]["message"]["content"]
        bot.reply_to(message, cevap)
    except:
        bot.reply_to(message, "❌ Hata oldu, lütfen tekrar dene.")

print("✅ Profesyonel Premium Bot Çalışıyor...")
bot.infinity_polling()
