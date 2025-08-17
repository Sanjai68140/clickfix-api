from config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
import razorpay

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

try:
    response = client.payment_link.all()
    print("✅ Connected to Razorpay. Payment links:")
    print(response)
except Exception as e:
    print("❌ Authentication failed:", e)