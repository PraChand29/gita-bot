from flask import Flask, request
import json
import os
import requests

app = Flask(__name__)

# 🔑 Load token from Render
TOKEN = os.getenv("8266373988:AAHsTdafXaqEBpYhsqDG9fxG82HSvOV6Iv8")
print("TOKEN:", TOKEN)  # DEBUG

DATA_FILE = "gita_final.json"
USER_FILE = "users.json"

# 📂 Load dataset
with open(DATA_FILE, "r", encoding="utf-8") as f:
    shloks = json.load(f)

# 📂 Load user progress
if os.path.exists(USER_FILE):
    with open(USER_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

# 📩 Send message to Telegram
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    response = requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })

    print("Telegram response:", response.text)  # DEBUG

# 🎯 Get next shlok
def get_next(chat_id):
    chat_id = str(chat_id)

    index = users.get(chat_id, 0)

    if index >= len(shloks):
        index = 0

    v = shloks[index]
    users[chat_id] = index + 1

    return v

# 📝 Format message safely
def format_msg(v):
    return f"""🧘 Daily Gita Wisdom

📖 Chapter {v.get('chapter')}, Verse {v.get('verse')}

Sanskrit:
{v.get('sanskrit', 'N/A')}

Hindi:
{v.get('hindi', 'N/A')}

English:
{v.get('english', 'N/A')}

Insight:
{v.get('insight', 'N/A')}
"""

# 🌐 Home route
@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

# 🤖 Webhook route
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Incoming:", data)  # DEBUG

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "").lower()

        if text in ["/start", "/next", "next shlok"]:
            shlok = get_next(chat_id)
            msg = format_msg(shlok)
            send_message(chat_id, msg)

    # 💾 Save progress
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

    return "ok"

# 🚀 Run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)