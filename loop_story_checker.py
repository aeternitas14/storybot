import time
from playwright.sync_api import sync_playwright
import requests
import os
import json
print(">>> Bot started...")
from multi_tracker import load_users

TARGET_USERNAME = 'sarahjclow'
BOT_TOKEN = '7569840561:AAHnbeez9FcYFM_IpwyxJ1AwaiqKA7r_jiA'
CHAT_IDS = []
CHECK_INTERVAL_MINUTES = 10
SUBSCRIBERS_FILE = "subscribers.json"

ALERT_STATE_FILE = "alert_state.json"

def get_last_alert_state(file_path):
    if not os.path.exists(file_path):
        return False
    with open(file_path, "r") as f:
        return json.load(f).get("last_alert", False)

def set_last_alert_state(file_path, state):
    with open(file_path, "w") as f:
        json.dump({"last_alert": state}, f)

# Load chat IDs from file
if os.path.exists(SUBSCRIBERS_FILE):
    with open(SUBSCRIBERS_FILE, "r") as f:
        CHAT_IDS = json.load(f)
else:
    CHAT_IDS = []

last_alert_sent = False
def send_telegram_message(message, chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    print(f"Sent alert to {chat_id}: {response.status_code}")
    return response.ok

def add_chat_id(chat_id):
    if chat_id not in CHAT_IDS:
        CHAT_IDS.append(chat_id)
        with open(SUBSCRIBERS_FILE, "w") as f:
            json.dump(CHAT_IDS, f)
        print(f"New subscriber added: {chat_id}")

def update_subscribers():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    response = requests.get(url)
    updates = response.json().get("result", [])

    for update in updates:
        try:
            chat_id = update["message"]["chat"]["id"]
            add_chat_id(chat_id)
        except KeyError:
            continue

def check_story():
    users = load_users()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="state.json")
        page = context.new_page()

        try:
            update_subscribers()

            for chat_id, usernames in users.items():
                for username in usernames:
                    alert_file = f"alert_state_{chat_id}_{username}.json"
                    page.goto(f'https://www.instagram.com/{username}/', wait_until='domcontentloaded')
                    page.wait_for_timeout(4000)

                    has_story = bool(page.query_selector("canvas"))
                    alert_previously_sent = get_last_alert_state(alert_file)

                    if has_story and not alert_previously_sent:
                        send_telegram_message(f"{username} just posted a story!", chat_id)
                        print(f"Story detected for {username} ({chat_id}). Alert sent.")
                        set_last_alert_state(alert_file, True)

                    elif not has_story and alert_previously_sent:
                        print(f"No story for {username}. Resetting alert state.")
                        set_last_alert_state(alert_file, False)

                    else:
                        print(f"No change in story state for {username}.")

        finally:
            browser.close()
if __name__ == "__main__":
    while True:
        try:
            check_story()
            print("Sleeping for", CHECK_INTERVAL_MINUTES, "minutes...")
            time.sleep(CHECK_INTERVAL_MINUTES * 60)
        except Exception as e:
            print("Error in main loop:", e)
            time.sleep(60)  # wait 1 minute before retrying

