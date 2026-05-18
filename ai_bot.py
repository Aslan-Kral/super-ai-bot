@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "👋 *Merhaba! Hoş geldin.*\n\n"
        "Ben **Super AI Asistan**.\n"
        "Her konuda yardımcı olabilirim.\n\n"
        "Premium özellikler için `/premium` yazman yeterli.", 
        parse_mode="Markdown")

@bot.message_handler(commands=['premium'])
def premium(message):
    text = """
🌟 <b>Super AI Premium</b>

📦 <b>Paket Seçenekleri</b>
• 1 Aylık → 99 TL
• 3 Aylık → 249 TL (indirimli)
• 12 Aylık → 799 TL (en avantajlı)

✨ <b>Avantajlar</b>
• Daha uzun, detaylı ve yaratıcı cevaplar
• Sınırsız kullanım
• Daha yüksek yanıt kalitesi
• Öncelikli destek

💰 <b>Ödeme Bilgileri</b>
Garanti IBAN:
`TR02 0006 2000 4700 0006 6276 06`

Ödeme yaptıktan sonra **"Ödeme yaptım"** yaz ve dekontu at.
Dekontunu kontrol edip hemen premium’u aktif ediyorum.
"""
    bot.reply_to(message, text, parse_mode="HTML")
