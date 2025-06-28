from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import os, asyncio

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)
application = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is live! ✅")

application.add_handler(CommandHandler("start", start))

@app.route("/", methods=["GET"])
def health():
    return "OK"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.create_task(application.process_update(update))
    return "OK"


def setup():
    asyncio.get_event_loop().run_until_complete(
        application.bot.set_webhook(WEBHOOK_URL + "/webhook")
    )
    print("✅ Webhook set:", WEBHOOK_URL + "/webhook")

if __name__ == "__main__":
    setup()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
