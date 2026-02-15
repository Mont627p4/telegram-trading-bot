from flask import Flask
import logging
import requests
import threading
import time

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Your Render app URL - REPLACE THIS AFTER DEPLOYMENT
RENDER_URL = "https://YOUR-APP-NAME.onrender.com"

def self_ping():
    """Ping itself every 5 minutes to keep awake"""
    time.sleep(300)  # Wait 5 minutes
    while True:
        try:
            requests.get(f"{RENDER_URL}/health")
            logging.info("🏓 Self-ping sent")
        except:
            pass
        time.sleep(300)  # Every 5 minutes

@app.route('/')
def home():
    return "Bot is running 24/7!"

@app.route('/health')
def health():
    return "OK", 200

# Start self-ping in background
ping_thread = threading.Thread(target=self_ping, daemon=True)
ping_thread.start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
