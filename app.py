from trading_bot import main
import asyncio
import threading
import logging
from flask import Flask

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def start_bot():
    """Start the bot with its own event loop"""
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

@app.route('/')
def home():
    return "Bot is alive!"

# Start bot when app starts
thread = threading.Thread(target=start_bot, daemon=True)
thread.start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
