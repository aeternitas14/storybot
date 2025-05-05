from flask import Flask, request
import requests
import os
import json
import random
import time
from datetime import datetime
from multi_tracker import add_user, is_new_user, remove_user, get_tracked_users, update_users

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN", "7569840561:AAHnbeez9FcYFM_IpwyxJ1AwaiqKA7r_jiA")

# Fun responses for different scenarios
STALKER_COMPLIMENTS = [
    "Wow, you're really committed to this whole stalking thing, aren't you? 🕵️‍♂️",
    "Another one? You're really building your collection of victims, huh? 📸",
    "Damn, you're really thirsty for that content, aren't you? 🥤",
    "Adding to your creep list, I see. No judgment here! 😏",
    "Another poor soul to stalk? You're really going all in! 🎭"
]

STALKER_INSULTS = [
    "Bruh, you're already stalking them. Get a life! 🤡",
    "Seriously? You're already creeping on them. Touch grass! 🌱",
    "You're really desperate, aren't you? They're already on your list! 🙄",
    "Get some help, you're already tracking them! 🏥",
    "Bruh, you're already obsessed with them. Maybe try therapy? 🛋️"
]

STALKER_LEVELS = [
    "Baby Stalker 👶",
    "Novice Creeper 🕵️‍♂️",
    "Intermediate Lurker 🎭",
    "Advanced Stalker 🎯",
    "Professional Stalker 🏆",
    "Legendary Stalker 👑",
    "Stalking God 🦹‍♂️"
]

STALKER_TIPS = [
    "Pro tip: Check their stories right after they post for maximum creepiness! 🕒",
    "Did you know? Most people post stories between 6-9 PM. Just saying... 👀",
    "Want to be extra creepy? Track their close friends too! 🎭",
    "Pro stalker move: Create a separate account just for stalking! 🎪",
    "Remember: The early stalker gets the story! Set up notifications! 🔔",
    "Want to level up? Start tracking their friends too! It's called networking! 🤝",
    "Pro tip: Save their stories to watch later. You know, for research! 📚",
    "Did you know? You can see who viewed their stories if you're quick enough! 🏃‍♂️"
]

def send_typing(chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendChatAction"
    data = {"chat_id": chat_id, "action": "typing"}
    requests.post(url, data=data)

def send_message(chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"Error sending message: {response.text}")
    except Exception as e:
        print(f"Error sending message: {e}")

def get_stalker_level(count):
    if count == 0:
        return STALKER_LEVELS[0]
    elif count < 3:
        return STALKER_LEVELS[1]
    elif count < 5:
        return STALKER_LEVELS[2]
    elif count < 10:
        return STALKER_LEVELS[3]
    elif count < 20:
        return STALKER_LEVELS[4]
    elif count < 50:
        return STALKER_LEVELS[5]
    else:
        return STALKER_LEVELS[6]

def get_stalker_achievements(count):
    achievements = []
    if count >= 1:
        achievements.append("First Victim 🎯")
    if count >= 5:
        achievements.append("Stalking Spree 🏃‍♂️")
    if count >= 10:
        achievements.append("Serial Stalker 🎭")
    if count >= 20:
        achievements.append("Stalking Master 🏆")
    if count >= 50:
        achievements.append("Stalking Legend 👑")
    return achievements

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        message = data["message"]
        chat_id = str(message["chat"]["id"])
        text = message.get("text", "")

        # Send typing indicator for all commands
        if text.startswith("/"):
            send_typing(chat_id)

        # Check if this is a new user
        if is_new_user(chat_id):
            welcome_message = """🎪 Welcome to ClowTracker, where dreams are made of! 🎭

Here's what you can do with me:
- /track <username> - Start stalking someone (e.g., /track instagram) 🕵️‍♂️
- /untrack <username> - Stop being a creep (e.g., /untrack instagram) 🙈
- /list - See all the poor souls you're tracking 📝
- /stats - See how much of a stalker you are 📊
- /level - Check your stalking level 🏆
- /roast - Get roasted for your stalking habits 🔥
- /tips - Get pro stalking tips 🎯
- /achievements - See your stalking achievements 🏅
- /help - Show this menu again 💡

Example: /track instagram 
Happy stalking! 🍆 💦"""
            send_message(chat_id, welcome_message)

        if text.startswith("/track"):
            parts = text.split()
            if len(parts) == 2:
                username = parts[1].lstrip("@")
                if add_user(chat_id, username):
                    compliment = random.choice(STALKER_COMPLIMENTS)
                    send_message(chat_id, f"{compliment}\nNow tracking @{username} 🍆 💦")
                else:
                    insult = random.choice(STALKER_INSULTS)
                    send_message(chat_id, insult)
            else:
                send_message(chat_id, "Bruh, learn to use commands properly! Usage: /track <instagram_username> 🤦‍♂️")
        
        elif text.startswith("/untrack"):
            parts = text.split()
            if len(parts) == 2:
                username = parts[1].lstrip("@")
                if remove_user(chat_id, username):
                    send_message(chat_id, f"Fine, I'll stop tracking @{username}. No more creeping 👋\nBut we both know you'll be back... 😏")
                else:
                    send_message(chat_id, f"Bruh, you're not even tracking @{username}. Are you hallucinating? 🤔")
            else:
                send_message(chat_id, "Bruh, learn to use commands properly! Usage: /untrack <instagram_username> 🤦‍♂️")
        
        elif text == "/list":
            send_typing(chat_id)  # Send typing indicator for list command
            tracked_users = get_tracked_users(chat_id)
            if tracked_users:
                user_list = "\n".join([f"- @{user} 👀" for user in tracked_users])
                level = get_stalker_level(len(tracked_users))
                send_message(chat_id, f"🎭 Your stalking list (you really need a hobby):\n{user_list}\n\nTotal victims: {len(tracked_users)} 🎯\nCurrent level: {level}")
            else:
                send_message(chat_id, "You're not tracking anyone yet! Use /track to start being creepy 😈\nDon't worry, we all start somewhere! 🎪")

        elif text == "/stats":
            tracked_users = get_tracked_users(chat_id)
            count = len(tracked_users)
            level = get_stalker_level(count)
            achievements = get_stalker_achievements(count)
            if count == 0:
                send_message(chat_id, f"Wow, you're not even trying! 0 people tracked. Pathetic. 😒\nCurrent level: {level}")
            elif count < 3:
                send_message(chat_id, f"Only {count} people? You call that stalking? Amateur hour! 😤\nCurrent level: {level}")
            elif count < 10:
                send_message(chat_id, f"{count} victims? Not bad, but you could do better! Keep going! 🎯\nCurrent level: {level}")
            else:
                send_message(chat_id, f"Damn, {count} people? You're really committed to this whole stalking thing! 🏆\nCurrent level: {level}\nMaybe consider therapy? 🛋️")
            
            if achievements:
                send_message(chat_id, f"🏅 Your Achievements:\n" + "\n".join(achievements))

        elif text == "/level":
            tracked_users = get_tracked_users(chat_id)
            count = len(tracked_users)
            level = get_stalker_level(count)
            next_level = STALKER_LEVELS[min(STALKER_LEVELS.index(level) + 1, len(STALKER_LEVELS) - 1)]
            send_message(chat_id, f"🎭 Your Stalking Level: {level}\n\nCurrent victims: {count} 🎯\n\nNext level: {next_level}\nKeep stalking to level up! 🏆")

        elif text == "/roast":
            tracked_users = get_tracked_users(chat_id)
            count = len(tracked_users)
            roasts = [
                f"Bruh, you're tracking {count} people? Get a life! 🌱",
                f"Imagine having {count} people's stories to watch. Touch grass! 🌿",
                f"{count} victims? Your phone must be running out of storage! 📱",
                f"With {count} people to stalk, when do you even sleep? 😴",
                f"Your mom would be so proud of your {count} victims! 👩‍👦",
                f"At this rate, you'll need a second phone for all {count} of your victims! 📱",
                f"Bro, {count} people? You're basically a professional stalker! 🏆",
                f"Your therapist would have a field day with your {count} victims! 🛋️"
            ]
            send_message(chat_id, random.choice(roasts))

        elif text == "/tips":
            tip = random.choice(STALKER_TIPS)
            send_message(chat_id, f"🎯 Pro Stalking Tip:\n{tip}")

        elif text == "/achievements":
            tracked_users = get_tracked_users(chat_id)
            count = len(tracked_users)
            achievements = get_stalker_achievements(count)
            if achievements:
                send_message(chat_id, f"🏅 Your Stalking Achievements:\n" + "\n".join(achievements))
            else:
                send_message(chat_id, "No achievements yet! Start stalking to earn some! 🎯")

        elif text == "/start":
            send_message(chat_id, "Welcome back to ClowTracker! 🎪\nReady to continue your stalking journey? Use /help to see what I can do for you 🎭")

        elif text == "/help":
            help_message = """🎪 ClowTracker Commands:
/track <username> - Start stalking someone 🕵️‍♂️
/untrack <username> - Stop being a creep 🙈
/list - See your stalking list 📝
/stats - See how much of a stalker you are 📊
/level - Check your stalking level 🏆
/roast - Get roasted for your stalking habits 🔥
/tips - Get pro stalking tips 🎯
/achievements - See your stalking achievements 🏅
/help - Show this menu 💡

Example: /track instagram
Happy stalking! 🍆 💦"""
            send_message(chat_id, help_message)

    except Exception as e:
        print("Webhook error:", e)
    return {"ok": True}

@app.route("/health", methods=["GET"])
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.route("/metrics", methods=["GET"])
def metrics():
    try:
        # Get basic metrics
        total_users = len(get_all_users())
        active_trackers = sum(1 for users in get_all_users().values() if users)
        return {
            "total_users": total_users,
            "active_trackers": active_trackers,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}, 500

def get_all_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

if __name__ == "__main__":
    # Use port 8080 on Fly.io, 5001 locally
    is_fly_io = os.getenv("FLY_APP_NAME") is not None
    port = int(os.environ.get("PORT", "8080")) if is_fly_io else 5001
    app.run(host="0.0.0.0", port=port)

