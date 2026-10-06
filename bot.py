import asyncio
import os
from flask import Flask
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Flask Uygulaması
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot aktif ve çalışıyor!"


# Telegram Komutları
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
      "Merhaba! Bot başarıyla aktif ve komutları dinliyor."
  )


async def veri_cek(update: Update, context: ContextTypes.DEFAULT_TYPE):
  try:
    response = requests.get("https://api.github.com")
    if response.status_code == 200:
      await update.message.reply_text(
          "Requests testi başarılı! Dış API'ye erişildi."
      )
    else:
      await update.message.reply_text(
          f"API yanıt verdi, durum kodu: {response.status_code}"
      )
  except Exception as e:
    await update.message.reply_text(f"Veri çekilirken hata oluştu: {e}")


def run_telegram_bot():
  TOKEN = os.getenv("TELEGRAM_TOKEN")
  if not TOKEN:
    print("Hata: TELEGRAM_TOKEN bulunamadı!")
    return

  # Yeni bir event loop oluşturarak botu güvenli bir şekilde başlatıyoruz
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)

  application = Application.builder().token(TOKEN).build()
  application.add_handler(CommandHandler("start", start))
  application.add_handler(CommandHandler("veri", veri_cek))

  print("Telegram bot polling ile başlatılıyor...")
  application.run_polling()


if __name__ == "__main__":
  import threading

  # 1. Telegram botunu arka planda thread ile çalıştırıyoruz
  bot_thread = threading.Thread(target=run_telegram_bot)
  bot_thread.daemon = True
  bot_thread.start()

  # 2. Flask sunucusunu ana akışta çalıştırıyoruz
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
