from bot import build_bot
from web import app as flask_app
import threading

if __name__ == "__main__":
    bot_app = build_bot()

    # Run Flask in a separate thread
    threading.Thread(target=lambda: flask_app.run(port=5000)).start()

    # Run Telegram bot
    bot_app.run_polling()