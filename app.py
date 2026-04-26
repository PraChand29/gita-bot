from flask import Flask, request
import json
import os
import requests

app = Flask(__name__)

# 🔑 CONFIG (use environment variable on Render)
TOKEN = os.getenv("8266373988:AAHsTdafXaqEBpYhsqDG9fxG82HSvOV6Iv8")

DATA_FILE = "gita_final.json"
USER_FILE = "users.json"

# 📂 Load dataset
with open(DATA_FILE, "r", encoding="utf-8") as f:
    shloks = json.load(f)

# 📂 Load users progress
if os.path.exists(USER_FILE):
    with open(USER_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

# 📩 Send message to Telegram
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    # Optional: nice keyboard button
    keyboard = {
        "keyboard": [[{"text": "Next Shlok"}]],
        "resize_keyboard": True
    }

    requests.post(url, json={
        "chat_id": chat_id,
        "text": text,
        "reply_markup": keyboard
    })

# 🎯 Get next shlok (no repeat per user)
def get_next(chat_id):
    chat_id = str(chat_id)

    index = users.get(chat_id, 0)

    if index >= len(shloks):
        index = 0  # reset after full cycle

    v = shloks[index]

    users[chat_id] = index + 1

    return v

# 📝 Format message
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

# 🌐 Home route (for browser check)
@app.route("/", methods=["GET"])
def home():
    return "✅ Gita Bot is Live!"

# 🤖 Webhook route (Telegram hits this)
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    print("Incoming:", data)  # DEBUG logs

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text:
            text = text.lower()

        if text in ["/start", "/next", "next shlok"]:
            shlok = get_next(chat_id)
            msg = format_msg(shlok)
            send_message(chat_id, msg)

    # 💾 Save user progress
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

    return "ok"

# 🚀 Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)