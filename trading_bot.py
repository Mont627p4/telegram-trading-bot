from telethon import TelegramClient, events
from telethon.sessions import StringSession
from binance.client import Client
import re
import math
import asyncio
import logging
import os
import time

# ========== YOUR CREDENTIALS - REPLACE THESE ==========
API_ID = 38099889  # <-- REPLACE with your API_ID
API_HASH = "333fe09debc36b6aac46aa60dac30e30"  # <-- REPLACE with your API_HASH
BINANCE_KEY = "ApgzC2cpewhBKqb1YPODfRCPzzV1Cy1y3wtpUiDAk8Dq21o6dFG4r6fcVpISey9W"  # <-- REPLACE
BINANCE_SECRET = "TllMkU490TyHO5HORsIF9QZsbgveitB2nb95CWgh39HbmOHz0GSJZnf9mlNa5r95"  # <-- REPLACE
CHANNEL_ID = -1002840783921  # YOUR CHANNEL ID
SESSION_STRING = "1BVtsOLsBu7-3Uaw0j6l5j0saUw58qhJ1cidZFrnw3lEI6nFRILffsW2gDtBX__8WaQZ0zkDRl3HtLs5DY9x-sbiHkJcoX1lXGcG7YDgTfXvqweasefhPC6Vp_F7itL6-LOd9pSueRJCxaNgA-VTNcA2PjfYBxejy7ueKpGD1b-ttjUIXEHX3J1gGPJKS47jMmNdcVN_b2x3JtcFO-nO35gRb1YMaDFfdJ_svj6bbP_hRZo3JLMs6ka31J9MGUMrJjKdQpmoMWMLKfnAeo3OP_kVs-lCFGTB8t7QQhMDqoeuxtDiXy6vBBmN_djpbTl7OSny2OoXbRGeG1Auxa_1fIn-_8a4gV-w="  # <-- REPLACE
# =====================================================

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

RISK_PERCENT = 1

# Initialize clients
telegram_client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
binance_client = Client(BINANCE_KEY, BINANCE_SECRET, testnet=True)
binance_client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'

def get_usdt_balance():
    try:
        balance = binance_client.futures_account_balance()
        for item in balance:
            if item['asset'] == 'USDT':
                return float(item['balance'])
        return 0
    except Exception as e:
        logger.error(f"Balance error: {e}")
        return 0

def calculate_quantity(entry_price, stop_loss, symbol):
    try:
        balance = get_usdt_balance()
        risk_amount = balance * (RISK_PERCENT / 100)
        
        info = binance_client.futures_exchange_info()
        step_size = 0.001
        
        for s in info['symbols']:
            if s['symbol'] == symbol:
                for filt in s['filters']:
                    if filt['filterType'] == 'LOT_SIZE':
                        step_size = float(filt['stepSize'])
                        break
        
        price_diff = abs(entry_price - stop_loss)
        if price_diff == 0:
            return 0
            
        raw_quantity = risk_amount / price_diff
        precision = int(round(-math.log10(step_size)))
        quantity = math.floor(raw_quantity * (10 ** precision)) / (10 ** precision)
        
        return quantity
    except Exception as e:
        logger.error(f"Quantity error: {e}")
        return 0

async def find_channel():
    logger.info("🔍 Searching for your private channel...")
    async for dialog in telegram_client.iter_dialogs():
        if dialog.id == CHANNEL_ID:
            logger.info(f"✅ Found channel: {dialog.name}")
            return dialog.entity
    logger.error("❌ Channel not found!")
    return None

@telegram_client.on(events.NewMessage)
async def handle_signal(event):
    try:
        if event.chat_id != CHANNEL_ID:
            return
            
        text = event.message.text
        logger.info(f"📨 Signal received")
        
        if not text or 'USDT' not in text:
            return
        if 'LONG' not in text and 'SHORT' not in text:
            return
        
        pair_match = re.search(r'([A-Z]+USDT)', text)
        entry_match = re.search(r'Entry.*?(\d+\.?\d*)', text, re.IGNORECASE)
        sl_match = re.search(r'SL.*?(\d+\.?\d*)', text, re.IGNORECASE)
        lev_match = re.search(r'\((\d+)X\)', text)
        
        if not all([pair_match, entry_match, sl_match]):
            return
        
        symbol = pair_match.group(1)
        entry_price = float(entry_match.group(1))
        stop_loss = float(sl_match.group(1))
        side = 'BUY' if 'LONG' in text else 'SELL'
        
        quantity = calculate_quantity(entry_price, stop_loss, symbol)
        
        if quantity <= 0:
            return
        
        leverage = int(lev_match.group(1)) if lev_match else 5
        binance_client.futures_change_leverage(symbol=symbol, leverage=leverage)
        
        order = binance_client.futures_create_order(
            symbol=symbol,
            side=side,
            type='LIMIT',
            price=entry_price,
            quantity=quantity,
            timeInForce='GTC'
        )
        
        logger.info(f"✅ ORDER PLACED!")
        
    except Exception as e:
        logger.error(f"Error: {e}")

async def keep_alive():
    """Send periodic pings to keep the bot alive"""
    while True:
        await asyncio.sleep(60)  # Ping every minute
        logger.debug("⏰ Keep-alive ping")

async def main():
    logger.info("🚀 Starting bot...")
    await telegram_client.start()
    me = await telegram_client.get_me()
    logger.info(f"✅ Logged in as: {me.first_name}")
    
    channel = await find_channel()
    if not channel:
        return
    
    @telegram_client.on(events.NewMessage(chats=channel))
    async def channel_handler(event):
        await handle_signal(event)
    
    logger.info(f"👂 Listening for signals from: {channel.title}")
    
    # Start keep-alive task
    asyncio.create_task(keep_alive())
    
    await telegram_client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
