from flask import Flask, request
import razorpay
@app.route('/webhook', methods=['POST'])
@app.route('/webhook/', methods=['POST'])
def webhook():
    print("Webhook hit! Method:", request.method)
    data = request.json
    print("Webhook JSON:", data)
    return {"status": "ok"}, 200

app = Flask(__name__)

# Razorpay client setup (replace with your actual keys)
razorpay_client = razorpay.Client(auth=("rzp_test_R6StCDC86N3nXo", "JVTxQJs7CagOgc8nSGMEdMKB"))

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
    return order

if __name__ == '__main__':
    app.run(debug=True)

