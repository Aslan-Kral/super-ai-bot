import telebot
import requests
import os
import sqlite3
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ====================== VERİTABANI ======================
conn = sqlite3.connect('bot_database.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS premium_users 
             (user_id INTEGER PRIMARY KEY, expiry_date TEXT)''')
conn.commit()

def is_premium(user_id):
    c.execute("SELECT expiry_date FROM premium_users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    if result:
        try:
            expiry = datetime.fromisoformat(result[0])
            return datetime.now() < expiry
        except:
            return False
    return False

def add_premium(user_id, days=30):
    expiry = (datetime.now() + timedelta(days=days)).isoformat()
    c.execute("INSERT OR REPLACE INTO premium_users (user_id, expiry_date) VALUES (?, ?)", (user_id, expiry))
    conn.commit()
    return expiry

# ====================== KOMUTLAR ======================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 **Hoş geldin!**\n\n"
                          "Ben Super AI Asistan. Her konuda yardımcı olabilirim.\n"
                          "Premium özellikler için `/premium` yaz.")

@bot.message_handler(commands=['premium'])
def premium(message):
    text = """
🌟 <b>Super AI Premium</b>

📦 Paketler:
• 1 Aylık → 99 TL
• 3 Aylık → 249 TL (en popüler)
• 12 Aylık → 799 TL (en avantajlı)

✨ Avantajlar:
• Daha uzun, detaylı ve yaratıcı cevaplar
• Sınırsız kullanım
• Öncelikli yanıt kalitesi

💰 Ödeme:
Garanti IBAN:
`TR02 0006 2000 4700 0006 6276 06`

Ödeme yaptıktan sonra **"Ödeme yaptım"** yaz ve dekontu at.
Hemen aktif ediyorum.
"""
    bot.reply_to(message, text, parse_mode="HTML")

@bot.message_handler(func=lambda m: "ödeme yaptım" in m.text.lower())
def odeme(message):
    user_id = message.from_user.id
    expiry = add_premium(user_id, 30)
    bot.reply_to(message, f"✅ **Tebrikler!** Premium üyeliğin aktif edildi.\n"
                          f"Bitiş tarihi: {expiry[:10]}\n\n"
                          "Artık çok daha kaliteli cevaplar alacaksın.")

# ====================== ANA AI ======================
@bot.message_handler(func=lambda message: True)
def ai_cevap(message):
    text_lower = message.text.lower().strip()
    
    # Komut koruma
    if text_lower in ["/start", "start", "/premium", "premium", "paket"]:
        if text_lower in ["/start", "start"]:
            return start(message)
        else:
            return premium(message)

    user_id = message.from_user.id
    premium_status = is_premium(user_id)

    bot.reply_to(message, "Düşünüyorum... ⏳")

    try:
        quality_instruction = (
            "Çok detaylı, uzun, yaratıcı, maddeli, örnekli ve profesyonel Türkçe cevap ver."
            if premium_status else
            "Kısa, net, yardımcı ve Türkçe cevap ver."
        )

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": f"{message.text}\n\n{quality_instruction}"}],
            "temperature": 0.75,
            "max_tokens": 2800 if premium_status else 1200
        }
        
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                               headers=headers, json=data, timeout=35)
        cevap = response.json()["choices"][0]["message"]["content"]
        bot.reply_to(message, cevap)
        
    except:
        bot.reply_to(message, "❌ Şu anda biraz yoğunum, lütfen 10 saniye sonra tekrar dene.")

print("✅ Super AI Bot - Profesyonel Versiyon Çalışıyor...")
bot.infinity_polling()
