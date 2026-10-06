async def fiyat(update: Update, context: ContextTypes.DEFAULT_TYPE):
  """CoinGecko üzerinden dinamik fiyat çeker."""
  if not context.args:
    await update.message.reply_text(
        "Lütfen bir coin adı belirtin. Örnek: `/fiyat btc`, `/fiyat ton`",
        parse_mode="Markdown",
    )
    return

  query = context.args[0].lower()

  # En yaygın coinler için ID eşleştirmesi
  coin_map = {
      "btc": "bitcoin",
      "eth": "ethereum",
      "ton": "the-open-network",
      "ston": "ston",
  }

  coin_id = coin_map.get(query, query)

  try:
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
      data = response.json()
      if coin_id in data and "usd" in data[coin_id]:
        price = data[coin_id]["usd"]
        await update.message.reply_text(
            f"💎 {query.upper()} Fiyatı: ${price}"
        )
      else:
        await update.message.reply_text(
            f"'{query}' için fiyat bulunamadı. Lütfen coinin tam adını veya"
            " geçerli bir kısaltmasını yazın."
        )
    else:
      await update.message.reply_text(
          "API şu an yanıt vermiyor (Rate limit aşılmış olabilir)."
      )
  except Exception as e:
    await update.message.reply_text(f"Hata oluştu: {e}")
