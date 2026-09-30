# super-ai-bot

Telegram komut botu. Bu sürümde yapay zekâ yanıt servisi, ödeme doğrulama ve ücretli üyelik bulunmaz. Eski fiyat/IBAN mesajı, olmayan bir üyeliğe ödeme istenmesini önlemek için devre dışıdır.

## Yerel başlatma

Python 3.10+ ile `pip install -r requirements.txt` çalıştırın.
BotFather'dan aldığınız bot tokenını yerel `TELEGRAM_BOT_TOKEN` ortam değişkenine güvenli biçimde tanımlayın; tokenı koda, sohbete veya Git'e eklemeyin.
Ardından `python ai_bot.py` çalıştırın. Aynı token için tek polling süreci kullanın.

Komutlar: `/start`, `/help`, `/premium`. Diğer metinlere mevcut yetenek sınırı açıklanır.
Modülü import etmek ağı başlatmaz. Eksik/geçersiz yapılandırmada çıkış kodu 2 döner.

## Kontrol

`python -m unittest -v`

Testler sahte Telegram istemcisiyle çevrimdışı çalışır. Canlı Telegram bağlantısını veya AI kalitesini doğrulamaz.

## Kalan işler

- Gerçek AI yanıt servisi, kullanım sınırları ve hata yönetimi.
- Satıştan önce açık hizmet kapsamı, onaylanmış fiyatlar, ödeme sağlayıcısı ve doğrulanmış üyelik akışı.
- Test hesabında Telegram kabul testi ve yetkili ortamda tek süreç olarak çalıştırma.
