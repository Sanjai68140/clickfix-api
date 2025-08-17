from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to ClickFix! Type /create_link to generate a payment link.")

handler = CommandHandler("start", start)