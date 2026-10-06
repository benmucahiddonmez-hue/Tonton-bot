import os
from flask import Flask, request
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Flask Uygulaması (Render'ın web servisi için zorunludur)
app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")


@app.route("/")
def home():
  return "Bot aktif ve çalışıyor!"


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
  """Telegram'dan gelen güncellemeleri webhook ile karşılar."""
  return "OK", 200


@app.route("/health")
def health():
  return "Healthy", 200


def main():
  if not TOKEN:
    print("Hata: TELEGRAM_TOKEN bulunamadı!")
    return

  print("Bot ve Flask Web Servisi başlatılıyor...")


if __name__ == "__main__":
  # Render'ın atadığı portu alıyoruz
  port = int(os.environ.get("PORT", 10000))

  # Render'ın port zaman aşımına uğramaması için Flask'ı doğrudan ana akışta başlatıyoruz
  # Not: Polling yerine Webhook yapısına geçmek Render Web Service için en kararlı yöntemdir.
  app.run(host="0.0.0.0", port=port)
