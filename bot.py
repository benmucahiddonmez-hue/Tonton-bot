import os
import threading
from flask import Flask
# ... (telegram ve diğer importlarınız)

# Flask uygulaması
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot aktif ve çalışıyor!"


def run_flask():
  # Render'ın atadığı portu alıyoruz (varsayılan 5000)
  port = int(os.environ.get("PORT", 5000))
  # 0.0.0.0 adresi dış erişime açmak için zorunludur
  app.run(host="0.0.0.0", port=port)


def main():
  TOKEN = os.getenv("TELEGRAM_TOKEN")
  if not TOKEN:
    print("Hata: TELEGRAM_TOKEN bulunamadı!")
    return

  # Telegram Bot yapılandırması
  application = Application.builder().token(TOKEN).build()

  # Komutlarınız buraya eklenecek
  # application.add_handler(...)

  # 1. Önce Flask'ı arka planda (ayrı bir thread'de) başlatıyoruz ki Render portu açık bulsun
  flask_thread = threading.Thread(target=run_flask)
  flask_thread.daemon = True
  flask_thread.start()
  print("Flask web sunucusu arka planda başlatıldı.")

  # 2. Sonra Telegram botunu polling ile başlatıyoruz
  print("Telegram bot polling ile başlatılıyor...")
  application.run_polling()


if __name__ == "__main__":
  main()
