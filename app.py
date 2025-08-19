from flask import Flask, request, jsonify
import razorpay
import os

app = Flask(__name__)

# Get keys from environment (more secure for Render)
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', 'rzp_test_R6StCDC86N3nXo')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', 'JVTxQJs7CagOgc8nSGMEdMKB')

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@app.route('/')
def home():
    return "ClickFix API is live!"

@app.route('/create_order', methods=['POST'])
def create_order():
    data = request.json
    amount = data.get('amount')
    currency = data.get('currency', 'INR')
    receipt = data.get('receipt', 'receipt#1')
    order = razorpay_client.order.create({
        "amount": amount,
        "currency": currency,
        "receipt": receipt,
        "payment_capture": 1
    })
    return jsonify(order)

# ---- WEBHOOK ROUTE ----
@app.route('/webhook', methods=['POST'])
@app.route('/webhook/', methods=['POST'])
def webhook():
    print("Webhook hit! Method:", request.method)
    print("Headers:", dict(request.headers))
    print("Webhook JSON:", request.json)
    # In production, you should verify signature and act on event!
    return jsonify({"status": "ok"}), 200
# -----------------------

if __name__ == '__main__':
    # Always set host/port explicitly for platforms like Render
    app.run(host="0.0.0.0", port=5000)
