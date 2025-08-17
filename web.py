from flask import Flask, request
import razorpay
import json
import logging
from config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, RAZORPAY_WEBHOOK_SECRET

app = Flask(__name__)

# Initialize Razorpay client
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Configure logging
logging.basicConfig(level=logging.INFO)

# Razorpay webhook for server-to-server verification
@app.route("/webhook", methods=["POST"])
def razorpay_webhook():
    payload = request.data
    signature = request.headers.get("X-Razorpay-Signature")

    try:
        client.utility.verify_webhook_signature(payload, signature, RAZORPAY_WEBHOOK_SECRET)
        data = json.loads(payload)

        logging.info("✅ Webhook verified")
        logging.info(json.dumps(data, indent=2))

        # TODO: Update DB, notify user, unlock content

        return "Webhook received and verified", 200

    except razorpay.errors.SignatureVerificationError as e:
        logging.error(f"❌ Signature verification failed: {e}")
        return "Invalid signature", 400

    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        return "Webhook processing error", 500

# Razorpay callback for user-facing redirect after payment
@app.route("/payment_callback", methods=["GET"])
def payment_callback():
    payment_id = request.args.get("razorpay_payment_id")
    link_id = request.args.get("razorpay_payment_link_id")
    status = request.args.get("razorpay_payment_link_status")

    logging.info("🔁 Razorpay redirected after payment")
    logging.info(f"Payment ID: {payment_id}")
    logging.info(f"Link ID: {link_id}")
    logging.info(f"Status: {status}")

    # TODO: Show confirmation page, trigger Telegram message, etc.

    return "✅ Payment received. Thank you!", 200