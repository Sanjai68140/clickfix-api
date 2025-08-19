import os
import razorpay
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

def send_locked_message(user_id, match_name):
    message = f"🔒 Payment received!\nYour locked content for '{match_name}' is now unlocked. Enjoy!"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": user_id,
        "text": message
    }
    resp = requests.post(url, data=data)
    print("Telegram response:", resp.text)

@app.route('/webhook', methods=['POST'])
def webhook():
    signature = request.headers.get("X-Razorpay-Signature")
    body_str = request.data.decode('utf-8')

    print("Received signature:", signature)
    print("Raw request body (decoded):", body_str)

    try:
        razorpay_client.utility.verify_webhook_signature(body_str, signature, RAZORPAY_KEY_SECRET)
        print("Signature verification succeeded")
        webhook_data = request.json
        print("Webhook payload:", webhook_data)

        # Extract user_id and match_name from event notes
        entity = None
        if "payment_link" in webhook_data.get("payload", {}):
            entity = webhook_data["payload"]["payment_link"].get("entity", {})
        elif "payment" in webhook_data.get("payload", {}):
            entity = webhook_data["payload"]["payment"].get("entity", {})
        else:
            return jsonify({"status": "failure", "reason": "missing entity"}), 400

        notes = entity.get("notes", {})
        user_id = notes.get("user_id")
        match_name = notes.get("match_name", "")

        # Only send message if user_id is present in notes
        if user_id:
            send_locked_message(user_id, match_name)
            print(f"Sent locked message to Telegram user {user_id} for match {match_name}")

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
