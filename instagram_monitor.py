import time
import requests
import os
import json
import sys
import hashlib
from datetime import datetime
from playwright.sync_api import sync_playwright

class InstagramMonitor:
    def __init__(self):
        # Set up logging
        self.log_file = open("log.txt", "a")
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
        # Create a custom print function that writes to both file and terminal
        class DualOutput:
            def __init__(self, log_file, original_stdout):
                self.log_file = log_file
                self.original_stdout = original_stdout

            def write(self, message):
                if message.strip():
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_message = f"[{timestamp}] {message}"
                    self.log_file.write(log_message)
                    self.log_file.flush()
                self.original_stdout.write(message)

            def flush(self):
                self.log_file.flush()
                self.original_stdout.flush()

        sys.stdout = sys.stderr = DualOutput(self.log_file, self.original_stdout)

        print("\n>>> Instagram Monitor started...")

        # Configuration
        self.bot_token = '7569840561:AAHnbeez9FcYFM_IpwyxJ1AwaiqKA7r_jiA'
        self.check_interval_minutes = 5
        self.users_file = "users.json"
        self.alert_states_dir = "alert_states"
        self.state_file = "state.json"

        # Create alert states directory if it doesn't exist
        if not os.path.exists(self.alert_states_dir):
            os.makedirs(self.alert_states_dir)

        # Verify required files exist
        if not os.path.exists(self.state_file):
            print(f"Error: {self.state_file} not found. Please log in to Instagram first.")
            sys.exit(1)

    def __del__(self):
        """Cleanup when the object is destroyed."""
        if hasattr(self, 'log_file'):
            self.log_file.close()
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

    def load_users(self):
        """Load users from the users file."""
        if not os.path.exists(self.users_file):
            print(f"Error: {self.users_file} not found")
            return {}
            
        try:
            with open(self.users_file, "r") as f:
                users = json.load(f)
                if not isinstance(users, dict):
                    print(f"Error: {self.users_file} does not contain a valid dictionary")
                    return {}
                print(f"Loaded {len(users)} users from {self.users_file}")
                return users
        except Exception as e:
            print(f"Error loading users: {e}")
            return {}

    def get_last_alert_state(self, username):
        """Get the last alert state for a user."""
        file_path = os.path.join(self.alert_states_dir, f"{username}.json")
        if not os.path.exists(file_path):
            print(f"Alert state file for {username} not found. Creating new one.")
            with open(file_path, "w") as f:
                json.dump({"last_alert": "", "last_check": "", "alerted_chats": []}, f)
            return {"hash": "", "timestamp": "", "alerted_chats": []}
            
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                return {
                    "hash": data.get("last_alert", ""),
                    "timestamp": data.get("last_check", ""),
                    "alerted_chats": data.get("alerted_chats", [])
                }
        except Exception as e:
            print(f"Error reading alert state file for {username}: {e}")
            return {"hash": "", "timestamp": "", "alerted_chats": []}

    def set_last_alert_state(self, username, thumbnail_url, alerted_chats):
        """Set the last alert state for a user."""
        if not thumbnail_url:
            print("No thumbnail URL provided to set_last_alert_state.")
            return
            
        try:
            file_path = os.path.join(self.alert_states_dir, f"{username}.json")
            hash_val = hashlib.sha256(thumbnail_url.encode()).hexdigest()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(file_path, "w") as f:
                json.dump({
                    "last_alert": hash_val,
                    "last_check": timestamp,
                    "alerted_chats": alerted_chats
                }, f)
        except Exception as e:
            print(f"Error setting alert state for {username}: {e}")

    def get_story_thumbnail_url(self, page):
        """Get the story thumbnail URL from the page."""
        try:
            img = page.query_selector('header ~ div img')
            if img:
                return img.get_attribute("src")
            print("No story thumbnail found on page")
        except Exception as e:
            print(f"Error getting thumbnail: {e}")
        return None

    def send_telegram_message(self, message, chat_id):
        """Send a message via Telegram bot."""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {"chat_id": chat_id, "text": message}
            response = requests.post(url, data=data)
            if response.ok:
                print(f"Successfully sent alert to {chat_id}")
            else:
                print(f"Failed to send alert to {chat_id}: {response.status_code} - {response.text}")
            return response.ok
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False

    def check_story(self):
        """Check for new stories and send alerts."""
        try:
            # Load users
            users = self.load_users()
            if not users:
                print("No users to monitor. Please check users.json")
                return

            # Initialize Playwright and browser
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                try:
                    context = browser.new_context(storage_state=self.state_file)
                    page = context.new_page()

                    # Track unique usernames across all chat_ids
                    checked_usernames = set()

                    # Check each user's stories
                    for chat_id, usernames in users.items():
                        # Skip invalid chat IDs
                        if not chat_id.isdigit() or len(chat_id) < 5:
                            print(f"Skipping invalid chat ID: {chat_id}")
                            continue

                        for username in usernames:
                            # Clean username and skip if empty or invalid
                            username = username.strip().lstrip('@')
                            if not username or username.startswith('<'):
                                continue

                            # Skip if we've already checked this username
                            if username in checked_usernames:
                                continue
                            checked_usernames.add(username)

                            try:
                                print(f"\nChecking stories for {username}")
                                page.goto(f'https://www.instagram.com/{username}/', wait_until='domcontentloaded')
                                page.wait_for_timeout(4000)

                                thumbnail_url = self.get_story_thumbnail_url(page)
                                if thumbnail_url:
                                    last_state = self.get_last_alert_state(username)
                                    current_hash = hashlib.sha256(thumbnail_url.encode()).hexdigest()

                                    print(f"Last check: {last_state['timestamp']}")
                                    print(f"Last hash: {last_state['hash']}")
                                    print(f"Current hash: {current_hash}")

                                    if current_hash != last_state['hash']:
                                        # Find all chat_ids that follow this user
                                        alert_chat_ids = [cid for cid, unames in users.items() 
                                                        if cid.isdigit() and len(cid) >= 5  # Valid chat IDs only
                                                        and username in [u.strip().lstrip('@') for u in unames]]
                                        
                                        # Send alert to all relevant chat_ids that haven't been alerted yet
                                        success = False
                                        alerted_chats = last_state['alerted_chats'].copy()
                                        
                                        for alert_chat_id in alert_chat_ids:
                                            if alert_chat_id not in alerted_chats:
                                                if self.send_telegram_message(f"{username} just posted a story!", alert_chat_id):
                                                    success = True
                                                    alerted_chats.append(alert_chat_id)
                                            
                                        if success:
                                            print(f"New story for {username}. Alerts sent.")
                                            self.set_last_alert_state(username, thumbnail_url, alerted_chats)
                                    else:
                                        print(f"No new story for {username}")
                                else:
                                    print(f"Could not find story thumbnail for {username}")
                            except Exception as e:
                                print(f"Error checking story for {username}: {e}")
                finally:
                    if browser:
                        browser.close()
        except Exception as e:
            print(f"Error in check_story: {e}")

    def run(self):
        """Main loop."""
        while True:
            try:
                self.check_story()
                print(f"\nSleeping for {self.check_interval_minutes} minutes...")
                time.sleep(self.check_interval_minutes * 60)
            except KeyboardInterrupt:
                print("\nShutting down...")
                break
            except Exception as e:
                print(f"\nError in main loop: {e}")
                time.sleep(5)  # wait 5 seconds before retrying

if __name__ == "__main__":
    try:
        monitor = InstagramMonitor()
        monitor.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"\nFatal error: {e}") 