from flask import Flask, request
import requests
import os
import json
from multi_tracker import add_user

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN", "7569840561:AAHnbeez9FcYFM_IpwyxJ1AwaiqKA7r_jiA")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        if text.startswith("/track"):
            parts = text.split()
            if len(parts) == 2:
                username = parts[1].lstrip("@")
                add_user(str(chat_id), username)
                send_message(chat_id, f"Tracking Instagram user: {username}")
            else:
                send_message(chat_id, "Usage: /track <instagram_username>")
    except Exception as e:
        print("Webhook error:", e)
    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

