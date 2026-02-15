from trading_bot import main
import asyncio
import threading
import logging
from flask import Flask
import time
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def run_bot():
    """Run bot in a new thread with its own event loop"""
    # Create NEW event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Run the bot
    loop.run_until_complete(main())

def keep_alive():
    """Keep the Render app alive"""
    time.sleep(60)  # Wait 1 minute
    while True:
        try:
            # Ping ourselves
            requests.get("https://YOUR-APP-NAME.onrender.com")
            logging.info("🏓 Keep-alive ping sent")
        except:
            pass
        time.sleep(300)  # Ping every 5 minutes

@app.route('/')
def home():
    return "Bot is running 24/7!"

# Start bot in background thread
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

# Start keep-alive thread
alive_thread = threading.Thread(target=keep_alive, daemon=True)
alive_thread.start()

# This is for Render
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
