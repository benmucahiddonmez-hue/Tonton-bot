import os
import threading
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


async def fiyat(update: Update, context: ContextTypes.DEFAULT_TYPE):
  """Kullanıcının yazdığı coine göre dinamik fiyat çeker (Örn: /fiyat btc)."""
  if not context.args:
    await update.message.reply_text(
        "Lütfen bir coin adı belirtin. Örnek: `/fiyat btc`, `/fiyat ton` veya"
        " `/fiyat ston`",
        parse_mode="Markdown",
    )
    return

  query = context.args[0].lower()

  # Coin kısaltmalarını CoinGecko ID'lerine eşleştiriyoruz
  coin_map = {
      "btc": "bitcoin",
      "eth": "ethereum",
      "ton": "the-open-network",
      "ston": "ston",
  }

  coin_id = coin_map.get(query, query)

  try:
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    response = requests.get(url)
    if response.status_code == 200:
      data = response.json()
      if coin_id in data and "usd" in data[coin_id]:
        price = data[coin_id]["usd"]
        await update.message.reply_text(
            f"💎 {query.upper()} Fiyatı: ${price}"
        )
      else:
        await update.message.reply_text(
            f"'{query}' için CoinGecko üzerinde fiyat bulunamadı."
        )
    else:
      await update.message.reply_text("Fiyat bilgisi şu an alınamadı.")
  except Exception as e:
    await update.message.reply_text(f"Fiyat çekilirken hata oluştu: {e}")


def run_flask():
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port, use_reloader=False)


def main():
  TOKEN = os.getenv("TELEGRAM_TOKEN")
  if not TOKEN:
    print("Hata: TELEGRAM_TOKEN bulunamadı!")
    return

  # 1. Flask'ı arka planda başlatıyoruz
  flask_thread = threading.Thread(target=run_flask)
  flask_thread.daemon = True
  flask_thread.start()

  # 2. Telegram botunu ana thread'de çalıştırıyoruz
  application = Application.builder().token(TOKEN).build()
  application.add_handler(CommandHandler("start", start))
  application.add_handler(CommandHandler("veri", veri_cek))
  application.add_handler(CommandHandler("fiyat", fiyat))

  print("Telegram bot polling ile ana thread'de başlatılıyor...")
  application.run_polling()


if __name__ == "__main__":
  main()
