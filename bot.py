import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Logging ayarları
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# GeckoTerminal API Bilgileri (TON ağı ve verdiğiniz havuz adresi)
NETWORK = "ton"
POOL_ADDRESS = "EQBTAGlXQX68Wc5m3q3PlvO7TKGn6_eo4M0fIF5DVNng76lh"
API_URL = f"https://api.geckoterminal.com/api/v2/networks/{NETWORK}/pools/{POOL_ADDRESS}"


def get_pool_data():
  try:
    response = requests.get(API_URL)
    if response.status_code == 200:
      data = response.json()
      attributes = data["data"]["attributes"]

      # Lazım olan verileri seçelim
      pool_name = attributes.get("name")
      price_usd = attributes.get("base_token_price_usd")
      fdv_usd = attributes.get("fdv_usd")
      volume_h24 = attributes.get("volume_usd", {}).get("h24")

      return {
          "name": pool_name,
          "price": price_usd,
          "fdv": fdv_usd,
          "volume_24h": volume_h24,
      }
    else:
      return None
  except Exception as e:
    print(f"API Hatası: {e}")
    return None


async def fiyat_komutu(update: Update, context: ContextTypes.DEFAULT_TYPE):
  data = get_pool_data()

  if data:
    mesaj = (
        f"📊 *Havuz Bilgisi: {data['name']}*\n\n"
        f"💵 *Fiyat (USD):* ${float(data['price']):.6f}\n"
        f"💧 *FDV:* ${float(data['fdv']):,.2f}\n"
        f"📈 *24s İşlem Hacmi:* ${float(data['volume_24h']):,.2f}"
    )
  else:
    mesaj = "Veriler alınırken bir hata oluştu veya API yanıt vermedi."

  await update.message.reply_text(mesaj, parse_mode="Markdown")


if __name__ == "__main__":
  # 'TELEGRAM_BOT_TOKEN' yazan yere BotFather'dan aldığınız token'ı tırnak içinde yazın
  app = ApplicationBuilder().token("TELEGRAM_BOT_TOKEN").build()

  app.add_handler(CommandHandler("fiyat", fiyat_komutu))

  print("Bot çalışıyor...")
  app.run_polling()
