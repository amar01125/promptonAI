from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio

TOKEN = "8163568593:AAFfCXQP_LvkOBHAL7RFirofxe0aAMHe8Lc"

# Flask App
app = Flask(__name__)

# Telegram Application
application = ApplicationBuilder().token(TOKEN).build()

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is live! ✅")

application.add_handler(CommandHandler("start", start))

# Webhook route
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return "OK"

# Optional: basic route for Render's health check
@app.route("/", methods=["GET"])
def home():
    return "Bot server running ✅"

