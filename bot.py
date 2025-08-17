from telegram.ext import ApplicationBuilder
from config import BOT_TOKEN
from handlers import start, create_link, pay

def build_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(start.handler)
    app.add_handler(create_link.handler)
    app.add_handler(pay.handler)
    return app