import requests
import json
import os

USERS_FILE = "users.json"
BOT_TOKEN = "7569840561:AAHnbeez9FcYFM_IpwyxJ1AwaiqKA7r_jiA"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def update_users():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    response = requests.get(url)
    updates = response.json().get("result", [])
    users = load_users()

    for update in updates:
        try:
            chat_id = str(update["message"]["chat"]["id"])
            text = update["message"]["text"]
            if text.lower().startswith("track "):
                username = text.split(" ", 1)[1].strip()
                if chat_id not in users:
                    users[chat_id] = []
                if username not in users[chat_id]:
                    users[chat_id].append(username)
                    print(f"Added {username} for {chat_id}")
        except Exception:
            continue

    save_users(users)

def add_user(chat_id, username):
    users = load_users()
    if chat_id not in users:
        users[chat_id] = []
    if username not in users[chat_id]:
        users[chat_id].append(username)
        save_users(users)
        print(f"Added {username} for {chat_id}")

