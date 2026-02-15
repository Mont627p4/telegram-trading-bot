from trading_bot import main
import asyncio
import threading
import logging
from flask import Flask
import time
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ========== SIMPLE FIX ==========
# Create event loop at the VERY START
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
# ================================

def run_bot():
    """Run bot in background"""
    try:
        # Use the existing loop
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except Exception as e:
        logging.error(f"Bot error: {e}")

def keep_alive():
    """Keep Render awake"""
    time.sleep(60)
    while True:
        try:
            requests.get("https://YOUR-APP-NAME.onrender.com")
            logging.info("💓 Ping")
        except:
            pass
        time.sleep(240)  # Ping every 4 minutes

@app.route('/')
def home():
    return "Bot Running 24/7!"

@app.route('/health')
def health():
    return "OK"

# Start bot in background
thread = threading.Thread(target=run_bot, daemon=True)
thread.start()

# Start keep-alive
alive = threading.Thread(target=keep_alive, daemon=True)
alive.start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
