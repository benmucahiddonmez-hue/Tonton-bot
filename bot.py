import os
from flask import Flask
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 1. Flask Uygulaması (Render'ın port isteğini karşılamak ve botu canlı tutmak için)
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot aktif ve çalışıyor!"


# 2. Telegram Komut Fonksiyonları
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  """/start komutu çalıştığında tetiklenir."""
  await update.message.reply_text(
      "Merhaba! Bot güncellendi ve başarıyla çalışıyor."
  )


async def veri_cek(update: Update, context: ContextTypes.DEFAULT_TYPE):
  """Requests kütüphanesini kullanarak dış kaynaklı veri çeken örnek komut."""
  try:
    # Örnek bir API isteği (kendi API adresinizle değiştirebilirsiniz)
    response = requests.get("https://api.github.com")
    data = response.json()
    await update.message.reply_text(f"API Bağlantısı başarılı! Durum: Online")
  except Exception as e:
    await update.message.reply_text(f"Veri çekilirken bir hata oluştu: {e}")


def main():
  # Çevre değişkenlerinden (Environment Variables) Telegram Token'ını alıyoruz
  TOKEN = os.getenv("8834429728:AAEUxQQGpda4GLlTBgJJVi2G9XkXUCEi-og")

  if not TOKEN:
    print("Hata: TELEGRAM_TOKEN bulunamadı!")
    return

  # python-telegram-bot v20+ yapısı
  application = Application.builder().token(TOKEN).build()

  # Komut yönlendiricileri (Handlers)
  application.add_handler(CommandHandler("start", start))
  application.add_handler(CommandHandler("veri", veri_cek))

  # Botu başlatma (Polling yöntemi)
  print("Bot başlatılıyor...")
  application.run_polling()


if __name__ == "__main__":
  # Render gibi platformlar için PORT değişkenini dinamik alıyoruz
  port = int(os.environ.get("PORT", 5000))

  # Not: Render üzerinde Flask ve Bot polling'i aynı anda çalıştırmak için
  # webhook kullanmak veya botu ayrı bir thread'de çalıştırmak gerekebilir.
  # Eğer sadece basit bir health-check web sunucusu tutacaksanız Flask'ı
  # arka planda (threading) başlatmanız gerekebilir.
