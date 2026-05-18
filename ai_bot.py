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
        expiry = datetime.fromisoformat(result[0])
        if datetime.now() < expiry:
            return True
    return False

def add_premium(user_id, days=30):
    expiry = (datetime.now() + timedelta(days=days)).isoformat()
    c.execute("INSERT OR REPLACE INTO premium_users (user_id, expiry_date) VALUES (?, ?)", (user_id, expiry))
    conn.commit()

# ====================== KOMUTLAR ======================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "👋 Hoş geldin! Ben Super AI Asistanım.\n\n"
        "Her konuda yardımcı olabilirim.\n"
        "/premium yazarak premium paketleri gör.")

@bot.message_handler(commands=['premium'])
def premium(message):
    text = """
🌟 <b>Super AI Premium</b>

Paketler:
• 1 Aylık → 99 TL
• 3 Aylık → 249 TL (indirimli)
• 12 Aylık → 799 TL (en avantajlı)

Avantajlar:
• Daha uzun, detaylı ve yaratıcı cevaplar
• Sınırsız kullanım
• Daha az bekleme süresi

Ödeme:
Garanti IBAN:
TR02 0006 2000 4700 0006 6276 06

Ödeme yaptıktan sonra:
"Ödeme yaptım" yaz + dekont at.
Hemen aktif ediyorum.
"""
    bot.reply_to(message, text, parse_mode="HTML")

@bot.message_handler(func=lambda m: "ödeme yaptım" in m.text.lower())
def odeme(message):
    user_id = message.from_user.id
    add_premium(user_id, 30)
    bot.reply_to(message, "✅ Tebrikler! Premium üyeliğin 30 gün boyunca aktif edildi.\n"
                          "Artık çok daha kaliteli ve uzun cevaplar alacaksın.")

# ====================== ANA AI CEVAP ======================
@bot.message_handler(func=lambda message: True)
def ai_cevap(message):
    user_id = message.from_user.id
    premium = is_premium(user_id)

    bot.reply_to(message, "Düşünüyorum... ⏳")

    try:
        quality = "Çok detaylı, uzun, yaratıcı ve kapsamlı Türkçe cevap ver. Örnekler ver, maddeler kullan." if premium else "Kısa, net ve yardımcı Türkçe cevap ver."

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": f"{message.text}\n\n{quality}"}],
            "temperature": 0.75,
            "max_tokens": 2500 if premium else 1200
        }
        
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                               headers=headers, json=data, timeout=30)
        cevap = response.json()["choices"][0]["message"]["content"]
        bot.reply_to(message, cevap)
        
    except Exception as e:
        bot.reply_to(message, "❌ Şu anda yoğunluk var, lütfen 10 saniye sonra tekrar dene.")

print("✅ Super AI Bot (Profesyonel Versiyon) Çalışıyor...")
bot.infinity_polling()
