from trading_bot import main
import asyncio
import threading
import logging
from flask import Flask
import time
import requests
import sys

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# THIS IS THE KEY FIX - Create event loop in main thread FIRST
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

def run_bot():
    """Run bot in a separate thread"""
    # Create NEW event loop for this thread
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    
    # Run the bot
    new_loop.run_until_complete(main())

def keep_alive():
    """Keep Render awake"""
    time.sleep(60)
    while True:
        try:
            requests.get("https://YOUR-APP-NAME.onrender.com")
            logging.info("💓 Keep-alive ping")
        except:
            pass
        time.sleep(300)

@app.route('/')
def home():
    return "🤖 Bot is running 24/7!"

@app.route('/health')
def health():
    return "OK", 200

# Start bot in background thread
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

# Start keep-alive thread
alive_thread = threading.Thread(target=keep_alive, daemon=True)
alive_thread.start()

# This runs the Flask app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
