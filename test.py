import razorpay
from razorpay.errors import BadRequestError

client = razorpay.Client(auth=("rzp_test_R6StCDC86N3nXo", "JVTxQJs7CagOgc8nSGMEdMKB"))

try:
    response = client.payment_link.all()
    print("✅ Connected to Razorpay. Payment links:")
    print(response)
except BadRequestError as e:
    print("❌ Authentication failed:", e)
except Exception as e:
    print("❌ Other error:", e)