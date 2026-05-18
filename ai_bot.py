import telebot
import requests
import os
import sqlite3
from datetime import datetime, timedelta

# ====================== AYARLAR ======================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ====================== VERİTABANI ======================
conn = sqlite3.connect('bot_database.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS premium_users 
             (user_id INTEGER PRIMARY KEY, expiry_date TEXT, payment_date TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS payments 
             (user_id INTEGER, amount TEXT, date TEXT, status TEXT, dekont TEXT)''')
conn.commit()

def is_premium(user_id):
    c.execute("SELECT expiry_date FROM premium_users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    if result:
        try:
            return datetime.fromisoformat(result[0]) > datetime.now()
        except:
            return False
    return False

def add_premium(user_id, days=30):
    expiry = (datetime.now() + timedelta(days=days)).isoformat()
    c.execute("INSERT OR REPLACE INTO premium_users (user_id, expiry_date, payment_date) VALUES (?, ?, ?)",
              (user_id, expiry, datetime.now().isoformat()))
    conn.commit()
    return expiry[:10]

# ====================== KOMUTLAR ======================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "👋 *Hoş geldin!*\n\n"
        "Ben Super AI Asistan.\n"
        "Her konuda yardımcı olabilirim.\n\n"
        "Premium özellikler için → `/premium` yaz.", 
        parse_mode="Markdown")

@bot.message_handler(commands=['premium'])
def premium(message):
    text = """
🌟 <b>Super AI Premium</b>

📦 Paketler:
• 1 Aylık → 99 TL
• 3 Aylık → 249 TL (indirimli)
• 12 Aylık → 799 TL (en avantajlı)

✨ Avantajlar:
• Daha uzun, detaylı ve yaratıcı cevaplar
• Sınırsız kullanım
• Öncelikli kalite

💰 Ödeme:
Garanti IBAN:
`TR02 0006 2000 4700 0006 6276 06`

Ödeme yaptıktan sonra:
**"Ödeme yaptım"** yaz ve dekontu at.
Dekontunu kontrol edip hemen aktif ediyorum.
"""
    bot.reply_to(message, text, parse_mode="HTML")

@bot.message_handler(func=lambda m: "ödeme yaptım" in m.text.lower())
def odeme_bildir(message):
    user_id = message.from_user.id
    bot.reply_to(message, "✅ Dekontunu aldım. Kontrol ediyorum...\n\n"
                          "Onaylandıktan sonra premium otomatik aktif olacak.\n"
                          "Dekontu atman yeterli.")

# ====================== ANA AI ======================
@bot.message_handler(func=lambda message: True)
def ai_cevap(message):
    text = message.text.lower().strip()
    
    # Komut koruma
    if text in ["/start", "start"]:
        return start(message)
    if text in ["/premium", "premium", "paket"]:
        return premium(message)

    user_id = message.from_user.id
    premium = is_premium(user_id)

    bot.reply_to(message, "Düşünüyorum... ⏳")

    try:
        instruction = (
            "Çok detaylı, uzun, yaratıcı, maddeli, örnekli ve profesyonel Türkçe cevap ver." 
            if premium else 
            "Kısa, net ve yardımcı Türkçe cevap ver."
        )

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": f"{message.text}\n\n{instruction}"}],
            "temperature": 0.75,
            "max_tokens": 2800 if premium else 1200
        }
        
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                               headers=headers, json=data, timeout=30)
        cevap = response.json()["choices"][0]["message"]["content"]
        bot.reply_to(message, cevap)
    except:
        bot.reply_to(message, "❌ Şu anda yoğunluk var, lütfen 10 saniye sonra tekrar dene.")

print("✅ Super AI Bot - Phase 1 (Profesyonel) Çalışıyor...")
bot.infinity_polling()
