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
        query = parts[1].upper()

        try:
          # 1. Önce Ston.fi havuzlarını (pools) kontrol edelim (V2 veya aktif havuzlar)
          pools_url = "https://api.ston.fi/v1/pools"
          pools_res = requests.get(pools_url).json()

          found = False
          if "pool_list" in pools_res:
            for pool in pools_res["pool_list"]:
              # Havuz içerisindeki token sembollerini kontrol ediyoruz
              lp_token0 = pool.get("token0_symbol", "").upper()
              lp_token1 = pool.get("token1_symbol", "").upper()

              if query in [lp_token0, lp_token1]:
                # Havuz verisinden USD karşılığını veya oranını çekmeye çalışıyoruz
                # Ston.fi havuzlarında lp token fiyatları lat/usd bazlı tutulabilir
                usd_price = pool.get("lp_price_usd") or pool.get(
                    "collected_token0_usd_value"
                )

                # Eğer doğrudan havuzda fiyat yoksa varlık listesinden denesin
                msg = f"💎 {query} (Ston.fi Havuzu Bulundu): Havuz adresi aktif, ancak bu havuz için doğrudan USD fiyatı API'de dönmüyor."
                found = True
                break

          # 2. Eğer havuzlarda bulunamadıysa varlık (assets) listesinden detaylı tarayalım
          if not found:
            assets_url = "https://api.ston.fi/v1/assets"
            assets_res = requests.get(assets_url).json()

            if "assets" in assets_res:
              for asset in assets_res["assets"]:
                if (
                    asset.get("symbol", "").upper() == query
                    or query in asset.get("display_name", "").upper()
                ):
                  price = asset.get("dex_usd_price") or asset.get("usd_price")
                  contract = asset.get("contract_address", "")
                  if price and float(price) > 0:
                    msg = f"💎 {query} (Ston.fi) Fiyatı: ${price}"
                  else:
                    msg = f"💎 {query} Ston.fi'da listelenmiş fakat aktif bir USD fiyatı (likiditesi) yok. Kontrat: `{contract}`"
                  found = True
                  break

          # 3. Hiçbir yerde yoksa CoinGecko yedek araması
          if not found:
            coin_map = {
                "BTC": "bitcoin",
                "ETH": "ethereum",
                "TON": "the-open-network",
            }
            coin_id = coin_map.get(query, query.lower())

            cg_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
            cg_res = requests.get(cg_url).json()

            if coin_id in cg_res and "usd" in cg_res[coin_id]:
              price = cg_res[coin_id]["usd"]
              msg = f"💎 {query} (CoinGecko) Fiyatı: ${price}"
            else:
              msg = f"'{query}' varlığı Ston.fi veya CoinGecko sisteminde fiyat verisiyle bulunamadı."

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
