import os
import razorpay
import sqlite3
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
DB = "fantasy_lock_bot.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                match_name TEXT PRIMARY KEY,
                creator_id INTEGER,
                description TEXT,
                filename TEXT,
                price INTEGER,
                expires_at TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                match_name TEXT,
                razorpay_order_id TEXT,
                paid INTEGER DEFAULT 0,
                paid_at TEXT,
                payment_link_url TEXT,
                UNIQUE(user_id, match_name)
            )
        ''')
        conn.commit()

def mark_payment_paid(user_id, match_name):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute(
            "UPDATE payments SET paid=1, paid_at=? WHERE user_id=? AND match_name=?",
            (datetime.now().isoformat(), user_id, match_name),
        )
        conn.commit()

def send_telegram_locked_message(user_id, filename, description):
    try:
        if filename and filename.startswith("http"):
            text = f"🎉 Payment received! Your content is unlocked:\n{filename}"
        else:
            text = f"🎉 Payment received! Your content '{description}' is unlocked."
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": user_id, "text": text})
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    signature = request.headers.get("X-Razorpay-Signature")
    try:
        body_str = request.data.decode('utf-8')
        razorpay_client.utility.verify_webhook_signature(body_str, signature, RAZORPAY_KEY_SECRET)
    except razorpay.errors.SignatureVerificationError:
        print("Signature verification failed!")
        return jsonify({"status": "failure", "reason": "invalid signature"}), 400
    except Exception as e:
        print(f"Error during signature verification: {e}")
        return jsonify({"status": "failure", "reason": "server error"}), 500

    try:
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

            with sqlite3.connect(DB) as conn:
                c = conn.cursor()
                c.execute("SELECT filename, description FROM matches WHERE match_name=?", (match_name,))
                row = c.fetchone()
            if row:
                filename, description = row
                send_telegram_locked_message(user_id, filename, description)

            print(f"Payment marked and user notified for user {user_id} match {match_name}")

        return jsonify({"status": "success"}), 200
    
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        return jsonify({"status": "failure", "reason": "database error"}), 500
    except Exception as e:
        print(f"Error processing webhook data: {e}")
        return jsonify({"status": "failure", "reason": "server error"}), 500

@app.route('/')
def home():
    return "ClickFix API Running"

if __name__ == "__main__":
    init_db()  # Ensure tables exist
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
