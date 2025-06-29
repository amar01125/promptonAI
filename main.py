from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Example: https://promptonai.onrender.com/webhook

app = Flask(__name__)

application = ApplicationBuilder().token(BOT_TOKEN).build()

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot Render par successfully chal raha hai!")

application.add_handler(CommandHandler("start", start))

# webhook route
@app.post("/webhook")
async def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)

        # Ensure application is initialized and started
        if not application.running:
            await application.initialize()
            await application.start()

        await application.process_update(update)
        return "OK"
    except Exception as e:
        print(f"❌ Webhook Error: {e}")
        return "Internal Server Error", 500

# Automatically set webhook when Flask starts on Render
@app.before_first_request
def setup_webhook():
    asyncio.run(application.bot.set_webhook(url=WEBHOOK_URL))

# local testing (optional)
if __name__ == '__main__':
    asyncio.run(application.initialize())
    asyncio.run(application.start())
    app.run(port=10000)
