import os
from flask import Flask, request
import requests

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"


@app.route("/")
def home():
  return "Bot ve Web Servisi Aktif!"


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
  json_data = request.get_json()

  if "message" in json_data:
    chat_id = json_data["message"]["chat"]["id"]
    text = json_data["message"].get("text", "")

    if text.startswith("/fiyat"):
      parts = text.split()
      if len(parts) > 1:
        query = parts[1].lower()

        try:
          # CoinGecko'nun en popüler coin pazar listesini çekiyoruz (Aynı tablodaki gibi)
          cg_url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false"
          res = requests.get(cg_url).json()

          found_coin = None
          if isinstance(res, list):
            for coin in res:
              if (
                  coin.get("symbol", "").lower() == query
                  or query in coin.get("name", "").lower()
              ):
                found_coin = coin
                break

          if found_coin:
            name = found_coin.get("name")
            symbol = found_coin.get("symbol").upper()
            price = found_coin.get("current_price")
            rank = found_coin.get("market_cap_rank")

            msg = (
                f"📊 **{name} ({symbol})**\n"
                f"🏆 Piyasa Sıralaması: #{rank}\n"
                f"💵 Güncel Fiyat: ${price}"
            )
          else:
            msg = (
                f"'{query}' adında bir coin listede bulunamadı. Lütfen sembolünü"
                " (örn: btc, eth, ton) doğru yazdığınızdan emin olun."
            )

        except Exception as e:
          msg = f"Veri çekilirken bir hata oluştu: {e}"
      else:
        msg = (
            "Lütfen bir coin adı belirtin.\nÖrnek kullanım: `/fiyat btc` veya"
            " `/fiyat sol`"
        )
    elif text.startswith("/start"):
      msg = (
          "Merhaba! Kripto Fiyat Botu aktif.\nKomutlar:\n`/fiyat [coin_adi]`"
          " (Örn: /fiyat btc)"
      )
    else:
      msg = "Bilinmeyen komut. /start yazarak komutları görebilirsiniz."

    send_url = f"{TELEGRAM_API_URL}/sendMessage"
    requests.post(
        send_url, json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}
    )

  return "OK", 200


def set_webhook():
  RENDER_URL = "https://tonton-bot-sou3.onrender.com"
  webhook_url = f"{TELEGRAM_API_URL}/setWebhook?url={RENDER_URL}/{TOKEN}"
  requests.get(webhook_url)


if __name__ == "__main__":
  set_webhook()
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
