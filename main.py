from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

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
        if not application.initialized:
            await application.initialize()
        await application.process_update(update)
        return "OK"
    except Exception as e:
        print(f"❌ Webhook Error: {e}")
        return "Internal Server Error", 500

# local testing (not used on render)
if __name__ == '__main__':
    app.run(port=10000)
