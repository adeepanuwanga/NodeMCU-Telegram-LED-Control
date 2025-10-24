# bot_server.py
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from flask import Flask, request, jsonify
import threading
import requests
import json

# Flask app for receiving NodeMCU status
app = Flask(__name__)

# Store NodeMCU status
nodemcu_status = {
    'led_state': 'off',
    'connected': False,
    'ip_address': None
}

# Telegram Bot Token from @BotFather
TELEGRAM_BOT_TOKEN = "your_bot_token_here"
# NodeMCU IP address (you'll need to set this statically or use mDNS)
NODEMCU_IP = "192.168.1.100"  # Change to your NodeMCU's IP

# Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 LED Control Bot Started!\n\n"
        "Available commands:\n"
        "/ledon - Turn LED ON\n"
        "/ledoff - Turn LED OFF\n"
        "/ledstatus - Check LED status\n"
        "/ledtoggle - Toggle LED state"
    )

async def led_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(f"http://{NODEMCU_IP}/led/on", timeout=5)
        if response.status_code == 200:
            nodemcu_status['led_state'] = 'on'
            await update.message.reply_text("💡 LED turned ON!")
        else:
            await update.message.reply_text("❌ Failed to turn LED ON")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: Could not reach NodeMCU\n{str(e)}")

async def led_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(f"http://{NODEMCU_IP}/led/off", timeout=5)
        if response.status_code == 200:
            nodemcu_status['led_state'] = 'off'
            await update.message.reply_text("🔌 LED turned OFF!")
        else:
            await update.message.reply_text("❌ Failed to turn LED OFF")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: Could not reach NodeMCU\n{str(e)}")

async def led_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = "ON ✅" if nodemcu_status['led_state'] == 'on' else "OFF ❌"
    connection = "Connected ✅" if nodemcu_status['connected'] else "Disconnected ❌"
    
    message = f"💡 LED Status: {status}\n"
    message += f"📡 Connection: {connection}\n"
    if nodemcu_status['ip_address']:
        message += f"🌐 IP: {nodemcu_status['ip_address']}"
    
    await update.message.reply_text(message)

async def led_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(f"http://{NODEMCU_IP}/led/toggle", timeout=5)
        if response.status_code == 200:
            # Toggle our local state
            nodemcu_status['led_state'] = 'on' if nodemcu_status['led_state'] == 'off' else 'off'
            state = "ON" if nodemcu_status['led_state'] == 'on' else "OFF"
            await update.message.reply_text(f"🔄 LED toggled to {state}!")
        else:
            await update.message.reply_text("❌ Failed to toggle LED")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: Could not reach NodeMCU\n{str(e)}")

# Flask endpoints for NodeMCU to report status
@app.route('/nodemcu/status', methods=['POST'])
def receive_nodemcu_status():
    data = request.get_json()
    nodemcu_status.update({
        'led_state': data.get('led_state', 'off'),
        'connected': True,
        'ip_address': request.remote_addr
    })
    return jsonify({"status": "received"})

@app.route('/nodemcu/heartbeat', methods=['GET'])
def heartbeat():
    return jsonify({"status": "alive"})

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

def run_telegram_bot():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ledon", led_on))
    application.add_handler(CommandHandler("ledoff", led_off))
    application.add_handler(CommandHandler("ledstatus", led_status))
    application.add_handler(CommandHandler("ledtoggle", led_toggle))
    
    print("🤖 Telegram Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    # Run Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Run Telegram bot in main thread
    run_telegram_bot()
