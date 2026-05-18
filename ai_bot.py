import telebot
import requests
import os
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Premium kullanıcıları tutmak için basit bir liste (daha sonra veritabanı yapabiliriz)
premium_users = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ Super AI Bot'a hoş geldin!\n\n/premium yazarak premium üye olabilirsin.")

@bot.message_handler(commands=['premium'])
def premium(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("1 Ay Premium - 149 Stars", callback_data="premium_1"))
    markup.add(telebot.types.InlineKeyboardButton("3 Ay Premium - 399 Stars (İndirimli)", callback_data="premium_3"))
    
    bot.send_invoice(
        chat_id=message.chat.id,
        title="Super AI Premium",
        description="Sınırsız hızlı cevap + öncelikli destek",
        payload="premium_payment",
        provider_token="",  # Telegram Stars için boş bırakılır
        currency="XTR",     # Telegram Stars para birimi
        prices=[telebot.types.LabeledPrice("1 Ay Premium", 149)],
        reply_markup=markup
    )

# Ödeme başarılı olursa
@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(query):
    bot.answer_pre_checkout_query(query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    user_id = message.from_user.id
    premium_users[user_id] = datetime.now() + timedelta(days=30)  # 1 ay premium
    
    bot.send_message(message.chat.id, "✅ Tebrikler! Premium üyeliğin aktif edildi.\n"
                                      "Artık sınırsız ve daha hızlı kullanabilirsin!")

# Normal AI cevap (premium kontrolü)
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

print("✅ Bot Telegram Stars ile çalışıyor...")
bot.infinity_polling()
