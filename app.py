import os
import razorpay
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
DB = "fantasy_lock_bot.db"

def mark_payment_paid(user_id, match_name):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute(
            "UPDATE payments SET paid=1, paid_at=? WHERE user_id=? AND match_name=?",
            (datetime.now().isoformat(), user_id, match_name),
        )
        conn.commit()

@app.route('/webhook', methods=['POST'])
def webhook():
    signature = request.headers.get("X-Razorpay-Signature")
    body_str = request.data.decode('utf-8')

    try:
        razorpay_client.utility.verify_webhook_signature(body_str, signature, RAZORPAY_KEY_SECRET)

        webhook_data = request.json

        entity = None
        if "payment_link" in webhook_data.get("payload", {}):
            entity = webhook_data["payload"]["payment_link"].get("entity", {})
        elif "payment" in webhook_data.get("payload", {}):
            entity = webhook_data["payload"]["payment"].get("entity", {})
        else:
            return jsonify({"status": "failure", "reason": "missing entity"}), 400

        notes = entity.get("notes", {})
        user_id = notes.get("user_id")
        match_name = notes.get("match_name")

        if user_id and match_name:
            mark_payment_paid(user_id, match_name)
            print(f"Payment marked paid for user {user_id} match {match_name}")

        return jsonify({"status": "success"}), 200

    except razorpay.errors.SignatureVerificationError:
        print("Signature verification failed!")
        return jsonify({"status": "failure", "reason": "invalid signature"}), 400

@app.route('/')
def home():
    return "ClickFix API running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
