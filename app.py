from flask import Flask, request
import json
import os
import requests

app = Flask(__name__)

# 🔑 CONFIG
TOKEN = "8266373988:AAHycU-PT9IM0dD3zzi7WHwmh16FVplPn5A"
DATA_FILE = "gita_final.json"
USER_FILE = "users.json"

# Load dataset
with open(DATA_FILE, "r", encoding="utf-8") as f:
    shloks = json.load(f)

# Load users
if os.path.exists(USER_FILE):
    with open(USER_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

# Send message
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text})

# Get next shlok
def get_next(chat_id):
    chat_id = str(chat_id)
    index = users.get(chat_id, 0)

    if index >= len(shloks):
        index = 0

    v = shloks[index]
    users[chat_id] = index + 1

    return v

# Format message
def format_msg(v):
    return f"""🧘 Daily Gita Wisdom

📖 Chapter {v['chapter']}, Verse {v['verse']}

Sanskrit:
{v['sanskrit']}

Hindi:
{v['hindi']}

English:
{v['english']}

Insight:
{v['insight']}
"""

# Webhook endpoint
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.lower() in ["/start", "/next"]:
            shlok = get_next(chat_id)
            msg = format_msg(shlok)
            send_message(chat_id, msg)

    # save users
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

    return "ok"

# Health check
@app.route("/")
def home():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)