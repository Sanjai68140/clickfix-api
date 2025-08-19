import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import razorpay

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@app.route('/webhook', methods=['POST'])
def razorpay_webhook():
    signature = request.headers.get("X-Razorpay-Signature")
    body = request.data.decode('utf-8')

    try:
        razorpay_client.utility.verify_webhook_signature(body, signature, RAZORPAY_KEY_SECRET)
        logging.info("Signature verification succeeded.")
    except razorpay.errors.SignatureVerificationError:
        logging.error("Invalid Razorpay webhook signature!")
        return jsonify({"status": "failure", "reason": "invalid signature"}), 400
    except Exception as e:
        logging.error(f"Signature verification error: {e}")
        return jsonify({"status": "failure", "reason": "server error"}), 500

    # Log webhook payload for inspection
    data = request.json
    logging.info(f"Received webhook: {data}")

    # Immediately respond with 200 OK to acknowledge receipt
    return jsonify({"status": "success"}), 200

@app.route('/')
def home():
    return "Razorpay webhook test server running."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
