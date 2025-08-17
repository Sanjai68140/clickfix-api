from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def razorpay_webhook():
    data = request.get_json()
    print("Webhook received:", data)
    return '', 200