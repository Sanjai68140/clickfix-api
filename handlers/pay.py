from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /create_link to get your payment link.")

handler = CommandHandler("pay", pay)