import time
from playwright.sync_api import sync_playwright
import requests
import os
import json
import sys
import hashlib

log_file = open("log.txt", "a")
sys.stdout = sys.stderr = log_file

print(">>> Bot started...")
from multi_tracker import load_users

TARGET_USERNAME = 'sarahjclow'
BOT_TOKEN = '7569840561:AAHnbeez9FcYFM_IpwyxJ1AwaiqKA7r_jiA'
CHAT_IDS = []
CHECK_INTERVAL_MINUTES = 5
SUBSCRIBERS_FILE = "subscribers.json"

ALERT_STATE_FILE = "alert_state.json"

def get_last_alert_state(file_path):
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "r") as f:
        return json.load(f).get("last_alert", "")

def set_last_alert_state(file_path, thumbnail_url):
    hash_val = hashlib.sha256(thumbnail_url.encode()).hexdigest()
    with open(file_path, "w") as f:
        json.dump({"last_alert": hash_val}, f)
def get_story_thumbnail_url(page):
    try:
        # Try to find the story thumbnail image URL
        img = page.query_selector('header ~ div img')
        if img:
            return img.get_attribute("src")
    except Exception as e:
        print("Error getting thumbnail:", e)
    return None

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

                    thumbnail_url = get_story_thumbnail_url(page)
                    last_seen_hash = get_last_alert_state(alert_file)

                    if thumbnail_url and hashlib.sha256(thumbnail_url.encode()).hexdigest() != last_seen_hash:
                        send_telegram_message(f"{username} just posted a story!", chat_id)
                        print(f"New story for {username} ({chat_id}). Alert sent.")
                        set_last_alert_state(alert_file, thumbnail_url)

                    elif thumbnail_url == last_seen_hash:
                        print(f"No new story for {username}")

                    else:
                        print(f"Could not find story thumbnail for {username}")

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
            time.sleep(5)  # wait 5 seconds before retrying

