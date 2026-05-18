import telebot
import requests
import os
from flask import Flask, request

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Super AI Bot Çalışıyor! 🚀"

@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def webhook():
    update = request.get_json()
    if update:
        bot.process_new_updates([telebot.types.Update.de_json(update)])
    return 'OK', 200

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ Bot aktif!\nHer şeyi sorabilirsin.")

@bot.message_handler(commands=['premium'])
def premium(message):
    bot.reply_to(message, "🌟 Premium yakında aktif olacak!")

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

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TELEGRAM_TOKEN}")
    print("✅ Webhook Bot aktif!")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
