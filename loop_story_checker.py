import time
from playwright.sync_api import sync_playwright
import requests
import os
import json

TARGET_USERNAME = 'sarahjclow'
BOT_TOKEN = '7569840561:AAHnbeez9FcYFM_IpwyxJ1AwaiqKA7r_jiA'
CHAT_IDS = []
CHECK_INTERVAL_MINUTES = 10
SUBSCRIBERS_FILE = "subscribers.json"

# Load chat IDs from file
if os.path.exists(SUBSCRIBERS_FILE):
    with open(SUBSCRIBERS_FILE, "r") as f:
        CHAT_IDS = json.load(f)
else:
    CHAT_IDS = []

last_alert_sent = False
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    success = True
    for chat_id in CHAT_IDS:
        data = {"chat_id": chat_id, "text": message}
        response = requests.post(url, data=data)
        print(f"Sent alert to {chat_id}: {response.status_code}")
        if not response.ok:
            success = False
    return success

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
    global last_alert_sent
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="state.json")
        page = context.new_page()

        try:
            update_subscribers()
            page.goto(f'https://www.instagram.com/{TARGET_USERNAME}/', wait_until='domcontentloaded')
            page.wait_for_timeout(4000)

            has_story = bool(page.query_selector("canvas"))

            if has_story and not last_alert_sent:
                send_telegram_message(f"{TARGET_USERNAME} just posted a story!")
                print("Story detected. Alert sent.")
                last_alert_sent = True
            elif not has_story:
                print("No story.")
                last_alert_sent = False

        finally:
            browser.close()
if __name__ == "__main__":
    send_telegram_message("Test: This is a manual broadcast to all subscribers.")
    while True:
        check_story()
        time.sleep(CHECK_INTERVAL_MINUTES * 60)

