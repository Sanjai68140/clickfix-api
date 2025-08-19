import os
import hmac
import hashlib
import sqlite3
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DB = "fantasy_lock_bot.db"


def add_sale(user_id, match_name):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute(
            "UPDATE payments SET paid = 1, paid_at = ? WHERE user_id = ? AND match_name = ?",
            (datetime.now().isoformat(), user_id, match_name)
        )
        conn.commit()


def deliver_content(user_id, match_name):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT filename, description FROM matches WHERE match_name=?", (match_name,))
        row = c.fetchone()
    if not row:
        print(f"No file found for match: {match_name}")
        return
    filename, description = row
    try:
        with open(filename, "rb") as f:
            response = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument",
                files={'document': f},
                data={'chat_id': user_id, 'caption': description}
            )
            if response.status_code != 200:
                print(f"Failed to deliver document: {response.text}")
    except Exception as e:
        print(f"Error sending file: {e}")


def verify_signature(data, signature):
    computed_sig = hmac.new(
        bytes(RAZORPAY_KEY_SECRET, 'utf-8'), data, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed_sig, signature)


@app.route('/webhook', methods=['POST'])
@app.route('/webhook/', methods=['POST'])
def webhook():
    signature = request.headers.get("X-Razorpay-Signature")
    body = request.data
    if not verify_signature(body, signature):
        print("Invalid signature")
        return jsonify({"status": "failure", "reason": "invalid signature"}), 400

    webhook_data = request.json

    entity = None
    if "payment_link" in webhook_data.get("payload", {}):
        entity = webhook_data["payload"]["payment_link"].get("entity", {})
    elif "payment" in webhook_data.get("payload", {}):
        entity = webhook_data["payload"]["payment"].get("entity", {})
    else:
        print("No valid payment or payment_link entity found in payload")
        return jsonify({"status": "failure", "reason": "missing entity"}), 400

    notes = entity.get("notes", {})
    user_id = int(notes.get("user_id", "0")) if str(notes.get("user_id", "0")).isdigit() else 0
    match_name = notes.get("match_name", "")
    if user_id and match_name:
        add_sale(user_id, match_name)
        deliver_content(user_id, match_name)
    else:
        print(f"Could not process: user_id={user_id}, match_name={match_name}")
        return jsonify({"status": "failure", "reason": "missing user_id or match_name"}), 400

    return jsonify({"status": "success"}), 200


@app.route('/')
def home():
    return "ClickFix API is live!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
