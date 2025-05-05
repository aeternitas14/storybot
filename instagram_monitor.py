import time
import requests
import os
import json
import sys
import hashlib
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
import asyncio
import random

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

        # Add session refresh settings
        self.session_refresh_interval = timedelta(hours=12)  # Refresh every 12 hours
        self.last_session_refresh = None
        self.session_file = "instagram_session.json"

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

    def is_session_expired(self):
        if not os.path.exists(self.session_file):
            return True
            
        try:
            with open(self.session_file, "r") as f:
                session_data = json.load(f)
                last_refresh = datetime.fromisoformat(session_data.get("last_refresh", ""))
                return datetime.now() - last_refresh > self.session_refresh_interval
        except:
            return True

    def refresh_session(self):
        try:
            print("Refreshing Instagram session...")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                
                # Add random delays to mimic human behavior
                page.set_default_timeout(30000)  # 30 second timeout
                
                # Go to Instagram
                page.goto('https://www.instagram.com/', wait_until='networkidle')
                page.wait_for_timeout(random.randint(2000, 5000))  # Random delay
                
                # Check if already logged in
                if page.url == 'https://www.instagram.com/':
                    print("Already logged in, saving session...")
                else:
                    # Check for suspicious login attempt warning
                    if "suspicious" in page.url.lower() or "challenge" in page.url.lower():
                        print("Instagram detected suspicious activity. Please verify manually.")
                        # Save the current state anyway
                        context.storage_state(path=self.state_file)
                        browser.close()
                        return False
                    
                    # Try to log in
                    try:
                        # Wait for login form
                        page.wait_for_selector('input[name="username"]', timeout=5000)
                        
                        # Type username with random delays
                        page.type('input[name="username"]', os.getenv('INSTAGRAM_USERNAME'), delay=random.randint(100, 300))
                        page.wait_for_timeout(random.randint(500, 1000))
                        
                        # Type password with random delays
                        page.type('input[name="password"]', os.getenv('INSTAGRAM_PASSWORD'), delay=random.randint(100, 300))
                        page.wait_for_timeout(random.randint(500, 1000))
                        
                        # Click login button
                        page.click('button[type="submit"]')
                        page.wait_for_timeout(random.randint(2000, 4000))
                        
                        # Check for any challenges or suspicious activity
                        if "challenge" in page.url.lower() or "suspicious" in page.url.lower():
                            print("Instagram detected suspicious activity. Please verify manually.")
                            browser.close()
                            return False
                        
                    except Exception as e:
                        print(f"Error during login: {e}")
                        browser.close()
                        return False
                
                # Save the session state
                context.storage_state(path=self.state_file)
                
                # Update session refresh timestamp
                with open(self.session_file, "w") as f:
                    json.dump({
                        "last_refresh": datetime.now().isoformat(),
                        "next_refresh": (datetime.now() + self.session_refresh_interval).isoformat(),
                        "user_agent": context.user_agent
                    }, f)
                
                browser.close()
                print("Session refreshed successfully!")
                return True
        except Exception as e:
            print(f"Error refreshing session: {e}")
            return False

    def check_story(self):
        """Check for new stories and send alerts."""
        try:
            # Check if session needs refresh
            if self.is_session_expired():
                print("Session expired, attempting refresh...")
                if not self.refresh_session():
                    print("Failed to refresh session. Stories might not be accessible.")
                    # Try to use existing session anyway
                    if not os.path.exists(self.state_file):
                        print("No session file found. Stories will not be accessible.")
                        return
            
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

    def save_story(self, username, story_url, story_type):
        try:
            # Create directory if it doesn't exist
            story_dir = f"{self.alert_states_dir}/{username}_stories"
            os.makedirs(story_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            extension = ".mp4" if story_type == "video" else ".jpg"
            filename = f"{story_dir}/{timestamp}{extension}"
            
            # Download and save the story
            response = requests.get(story_url)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                return True
            return False
        except Exception as e:
            print(f"Error saving story: {e}")
            return False

    async def check_stories(self):
        while True:
            try:
                with open(self.users_file, "r") as f:
                    users = json.load(f)
                
                for chat_id, tracked_users in users.items():
                    for username in tracked_users:
                        try:
                            # ... existing story checking code ...
                            
                            if new_stories:
                                for story in new_stories:
                                    # Save the story
                                    if self.save_story(username, story['url'], story['type']):
                                        # Send notification with download option
                                        message = f"New story from @{username} 🤡\nUse /download {username} to save it to your collection of despair"
                                        self.send_telegram_message(message, chat_id)
                        
                        except Exception as e:
                            print(f"Error checking stories for {username}: {e}")
                
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Error in main loop: {e}")
                await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        monitor = InstagramMonitor()
        monitor.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"\nFatal error: {e}") 