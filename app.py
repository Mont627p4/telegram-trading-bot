from trading_bot import main
import asyncio
import threading
import logging
from flask import Flask
import requests
import time

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# This keeps Render from sleeping
def ping_self():
    """Ping ourselves every 10 minutes to prevent sleep"""
    time.sleep(300)  # Wait 5 minutes after start
    while True:
        try:
            # Ping the app itself
            requests.get("https://YOUR-APP-NAME.onrender.com/health")
            logging.info("🏓 Self-ping sent")
        except:
            pass
        time.sleep(600)  # Ping every 10 minutes

def start_bot():
    """Start the bot with its own event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

@app.route('/')
def home():
    return "Bot is alive and running 24/7!"

@app.route('/health')
def health():
    return "OK", 200

# Start bot in background
bot_thread = threading.Thread(target=start_bot, daemon=True)
bot_thread.start()

# Start self-ping in background
ping_thread = threading.Thread(target=ping_self, daemon=True)
ping_thread.start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
