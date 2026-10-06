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
          # Ston.fi V1 Pools veya Assets uç noktasından detaylı arama
          url = "https://api.ston.fi/v1/assets"
          res = requests.get(url).json()

          found = False
          if "assets" in res:
            for asset in res["assets"]:
              symbol = asset.get("symbol", "").lower()
              name = asset.get("display_name", "").lower()

              if query == symbol or query in name:
                # Fiyat alanını kontrol ediyoruz (bazı varlıklarda usd_price veya dex_usd_price geçerlidir)
                price = asset.get("dex_usd_price") or asset.get("usd_price")

                if price and float(price) > 0:
                  msg = f"💎 {asset.get('symbol').upper()} (Ston.fi) Fiyatı: ${price}"
                else:
                  msg = f"'{asset.get('symbol').upper}' bulundu ancak aktif bir USD fiyat havuzu görünmüyor."
                found = True
                break

          if not found:
            # Ston.fi'da bulunamazsa CoinGecko yedek araması
            coin_map = {"btc": "bitcoin", "eth": "ethereum", "ton": "the-open-network"}
            coin_id = coin_map.get(query, query)

            cg_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
            cg_res = requests.get(cg_url).json()

            if coin_id in cg_res and "usd" in cg_res[coin_id]:
              price = cg_res[coin_id]["usd"]
              msg = f"💎 {query.upper()} (CoinGecko) Fiyatı: ${price}"
            else:
              msg = f"'{query}' coini Ston.fi veya CoinGecko sisteminde bulunamadı."

        except Exception as e:
          msg = f"Fiyat çekilirken hata oluştu: {e}"
      else:
        msg = "Lütfen bir coin adı belirtin. Örnek: `/fiyat ston`, `/fiyat ton`"
    elif text.startswith("/start"):
      msg = "Merhaba! Ston.fi ve Kripto Fiyat Botu aktif."
    else:
      msg = "Bilinmeyen komut."

    send_url = f"{TELEGRAM_API_URL}/sendMessage"
    requests.post(send_url, json={"chat_id": chat_id, "text": msg})

  return "OK", 200


def set_webhook():
  RENDER_URL = "https://tonton-bot-sou3.onrender.com"
  webhook_url = f"{TELEGRAM_API_URL}/setWebhook?url={RENDER_URL}/{TOKEN}"
  requests.get(webhook_url)


if __name__ == "__main__":
  set_webhook()
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
