import os
import razorpay
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


@app.route('/webhook', methods=['POST'])
def webhook():
    signature = request.headers.get("X-Razorpay-Signature")
    body_bytes = request.data
    body_str = body_bytes.decode('utf-8')  # Decode bytes to string

    print("Received signature:", signature)
    print("Raw request body (decoded):", body_str)

    try:
        razorpay_client.utility.verify_webhook_signature(body_str, signature, RAZORPAY_KEY_SECRET)
        print("Signature verification succeeded")
        webhook_data = request.json
        print("Webhook payload:", webhook_data)

        # Your business logic goes here:
        # Extract data and deliver content, update database, etc.

        return jsonify({"status": "success"}), 200
    except razorpay.errors.SignatureVerificationError:
        print("Signature verification failed!")
        return jsonify({"status": "failure", "reason": "invalid signature"}), 400

@app.route('/')
def home():
    return "ClickFix API is live!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
