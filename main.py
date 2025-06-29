import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.executor import start_webhook
import aiohttp
import asyncio

# Load env vars
from dotenv import load_dotenv
load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")  # e.g. https://your-app.onrender.com
WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

PORT = int(os.getenv("PORT", "8080"))
ADMIN_USER_IDS = [
    755778598  # <-- replace/add Telegram user IDs of admins here if needed
]

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- Simple User Context Storage (in-memory) ---
user_sessions = {}

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Middleware for Logging ---
class SimpleLoggingMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        logger.info(f"Message from {message.from_user.id}: {message.text}")

dp.middleware.setup(SimpleLoggingMiddleware())

# --- Handlers ---
@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    await message.reply(
        "🤖 *Welcome to ChatGPT Bot!*\n\n"
        "Just type any message and I'll reply using OpenAI's GPT-4.\n"
        "_/reset_ – Clear conversation memory.\n"
        "_/help_ – Show this help message.",
        parse_mode="Markdown",
    )

@dp.message_handler(commands=["reset"])
async def reset_session(message: types.Message):
    user_sessions.pop(message.from_user.id, None)
    await message.reply("✅ Your conversation context has been reset.")

@dp.message_handler(commands=["admin"])
async def admin_cmd(message: types.Message):
    if message.from_user.id in ADMIN_USER_IDS:
        await message.reply("👑 Admin command received. (Extend me for admin actions!)")
    else:
        await message.reply("⛔ This command is for admins only.")

@dp.message_handler()
async def chatgpt_handler(message: types.Message):
    user_id = message.from_user.id
    text = message.text
    session = user_sessions.get(user_id, [])
    # Add latest message
    session.append({"role": "user", "content": text})
    # Limit conversation history for memory/cost
    session = session[-10:]
    user_sessions[user_id] = session
    # Call OpenAI API
    reply = await ask_openai(session)
    # Save reply
    session.append({"role": "assistant", "content": reply})
    user_sessions[user_id] = session
    await message.reply(reply, parse_mode=None)

# --- OpenAI ChatGPT Call ---
async def ask_openai(messages):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "max_tokens": 500,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=body) as resp:
                data = await resp.json()
                return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return "⚠️ OpenAI API error. Try again later."

# --- Webhook Setup for Render ---
async def on_startup(dp):
    logger.info(f"Setting webhook: {WEBHOOK_URL}")
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dp):
    logger.info("Shutting down bot...")
    await bot.delete_webhook()
    await bot.session.close()

# --- Health Check Endpoint ---
async def health(request):
    return web.Response(text="ok")

def main():
    app = web.Application()
    app.router.add_get("/", health)
    # For Render: aiogram's start_webhook runs aiohttp server itself, so main() is only for local dev health.
    # On Render, use start_webhook below:
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host="0.0.0.0",
        port=PORT,
    )

if __name__ == "__main__":
    main()
