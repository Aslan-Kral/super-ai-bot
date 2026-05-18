import telebot
import requests
import os
import sqlite3
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Veritabanı
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
            return datetime.fromisoformat(result[0]) > datetime.now()
        except:
            return False
    return False

def add_premium(user_id, days=30):
    expiry = (datetime.now() + timedelta(days=days)).isoformat()
    c.execute("INSERT OR REPLACE INTO premium_users (user_id, expiry_date) VALUES (?, ?)", (user_id, expiry))
    conn.commit()

# ====================== KOMUTLAR ======================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Hoş geldin!\n\n/premium yazarak paketleri görebilirsin.")

@bot.message_handler(commands=['premium'])
def premium_cmd(message):
    text = """
🌟 <b>Super AI Premium</b>

Paketler:
• 1 Aylık → 99 TL
• 3 Aylık → 249 TL 
• 12 Aylık → 799 TL 

Avantajlar:
• Daha uzun ve detaylı cevaplar
• Yaratıcı yanıtlar
• Sınırsız kullanım

Ödeme:
Garanti IBAN:
TR02 0006 2000 4700 0006 6276 06

"Ödeme yaptım" yaz + dekont at → Hemen aktif ederim.
"""
    bot.reply_to(message, text, parse_mode="HTML")

# Normal mesajlarda da "premium" kelimesini yakala
@bot.message_handler(func=lambda m: True)
def ai_cevap(message):
    text = message.text.lower().strip()
    
    # Premium kelimesi geçtiğinde premium menüsünü göster
    if text == "premium" or text == "/premium" or "paket" in text:
        return premium_cmd(message)
    
    if text == "/start" or text == "start":
        return start(message)

    # Normal AI cevabı
    user_id = message.from_user.id
    premium = is_premium(user_id)

    bot.reply_to(message, "Düşünüyorum... ⏳")

    try:
        instruction = "Çok detaylı, uzun, yaratıcı, maddeli ve örnekli Türkçe cevap ver." if premium else "Kısa, net ve yardımcı Türkçe cevap ver."
        
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": f"{message.text}\n\n{instruction}"}],
            "temperature": 0.7,
            "max_tokens": 2500 if premium else 1100
        }
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        cevap = response.json()["choices"][0]["message"]["content"]
        bot.reply_to(message, cevap)
    except:
        bot.reply_to(message, "❌ Hata oldu, lütfen tekrar dene.")

print("✅ Slash'sız premium da çalışıyor...")
bot.infinity_polling()
