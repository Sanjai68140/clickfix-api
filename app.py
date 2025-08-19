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
    body = request.data

    print("Received signature:", signature)
    print("Raw request body:", body)

    # Use Razorpay SDK utility for webhook signature verification
    try:
        razorpay_client.utility.verify_webhook_signature(request.data, signature, RAZORPAY_KEY_SECRET)
        print("Signature verification succeeded")

        # Process webhook payload
        webhook_data = request.json
        print("Webhook JSON:", webhook_data)

        # Your logic here – example: just returning success
        return jsonify({"status": "success"}), 200

    except razorpay.errors.SignatureVerificationError:
        print("Signature verification failed!")
        return jsonify({"status": "failure", "reason": "invalid signature"}), 400


if __name__ == '__main__':
    # Use PORT from env or default 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
