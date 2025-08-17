from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
import razorpay
from config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, BASE_PUBLIC_URL

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

async def create_link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        payment = client.payment_link.create({
            "amount": 50000,
            "currency": "INR",
            "description": "ClickFix Service",
            "callback_url": f"{BASE_PUBLIC_URL}/webhook",
            "notify": {
                "sms": True,
                "email": True
            }
        })
        short_url = payment['short_url']
        await update.message.reply_text(f"✅ Payment link created:\n{short_url}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error creating payment link:\n{str(e)}")

handler = CommandHandler("create_link", create_link_handler)