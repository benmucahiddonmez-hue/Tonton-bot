import os
import threading
from flask import Flask
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 1. Flask Uygulaması (Render'ın port isteğini karşılamak ve web servisini canlı tutmak için)
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot aktif ve çalışıyor!"


def run_flask():
  # Render'ın atadığı dinamik portu alıyoruz (varsayılan 5000)
  port = int(os.environ.get("PORT", 5000))
  # 0.0.0.0 adresi dış dünya/Render erisimi için zorunludur
  app.run(host="0.0.0.0", port=port)


# 2. Telegram Bot Komut Fonksiyonları
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  """/start komutu çalıştığında tetiklenir."""
  await update.message.reply_text(
      "Merhaba! Bot güncellendi, Flask ve Telegram botu başarıyla"
      " çalıştırılıyor."
  )


async def veri_cek(update: Update, context: ContextTypes.DEFAULT_TYPE):
  """Requests kütüphanesini kullanarak örnek veri çeken komut."""
  try:
    response = requests.get("https://api.github.com")
    if response.status_code == 200:
      await update.message.reply_text(
          "Requests testi başarılı! Dış API'ye erişilebiliyor."
      )
    else:
      await update.message.reply_text(
          f"API yanıt döndü ancak durum kodu: {response.status_code}"
      )
  except Exception as e:
    await update.message.reply_text(f"Veri çekilirken bir hata oluştu: {e}")


def main():
  # Render Environment Variables kısmından TOKEN'ı güvenli şekilde çekiyoruz
  TOKEN = os.getenv("TELEGRAM_TOKEN")

