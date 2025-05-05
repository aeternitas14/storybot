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
    "Look who's back in the circus of obsession 🤡",
    "Another victim added to your freak show collection 🤡",
    "Your parents must be so proud of your stalking skills 🤡",
    "Congratulations, you've reached a new level of pathetic 🤡",
    "Your therapist is gonna love hearing about this one 🤡"
]

STALKER_INSULTS = [
    "You're already tracking them, you absolute circus act 🤡",
    "Wow, your memory is as good as your life choices 🤡",
    "Did your last two brain cells forget you're already stalking them? 🤡",
    "Peak clown behavior - trying to track someone twice 🤡",
    "Your desperation is showing, and it's not a good look 🤡"
]

STALKER_LEVELS = [
    "Circus Trainee 🤡",
    "Professional Disappointment 🤡",
    "Master of Mediocrity 🤡",
    "Distinguished Degenerate 🤡",
    "Supreme Waste of Space 🤡",
    "God of Getting No Bitches 🤡",
    "CEO of Down Bad Industries 🤡"
]

STALKER_TIPS = [
    "Pro tip: Your crush still won't notice you exist 🤡",
    "Fun fact: This won't fill the void in your life 🤡",
    "Expert advice: Your parents' disappointment is permanent 🤡",
    "Life hack: Try having a personality instead 🤡",
    "Secret technique: Maybe try therapy instead of stalking 🤡",
    "Advanced strategy: Touch grass, it's free 🤡",
    "Insider tip: They're not playing hard to get, you're just creepy 🤡",
    "Premium advice: Your ex isn't coming back, chief 🤡"
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
            welcome_message = """Welcome to the Circus of Sadness 🤡

I'm your ringmaster in this pathetic show. Here's your toolkit for being a professional disappointment:

/track <username> - Add another person who won't notice you exist
/untrack <username> - Pretend you're finally moving on
/list - See all the people living rent-free in your head
/stats - Quantify your life choices
/level - See how far you've fallen
/roast - Get reminded of your life decisions
/tips - Learn from fellow circus members
/achievements - Celebrate your downward spiral
/help - Too dumb to remember commands? I got you

Example: /track instagram
Now get out there and make your therapist earn their money 🤡"""
            send_message(chat_id, welcome_message)

        if text.startswith("/track"):
            parts = text.split()
            if len(parts) == 2:
                username = parts[1].lstrip("@")
                if add_user(chat_id, username):
                    compliment = random.choice(STALKER_COMPLIMENTS)
                    send_message(chat_id, f"{compliment}\nNow watching @{username} like the clown you are 🤡")
                else:
                    insult = random.choice(STALKER_INSULTS)
                    send_message(chat_id, insult)
            else:
                send_message(chat_id, "Even a circus needs standards. Usage: /track <username> 🤡")
        
        elif text.startswith("/untrack"):
            parts = text.split()
            if len(parts) == 2:
                username = parts[1].lstrip("@")
                if remove_user(chat_id, username):
                    send_message(chat_id, f"Congratulations on pretending to move on from @{username} 🤡\nWe both know you'll be back when you're drunk at 3am")
                else:
                    send_message(chat_id, f"You're not even tracking @{username}, you absolute clown 🤡")
            else:
                send_message(chat_id, "Reading comprehension not your strong suit? Usage: /untrack <username> 🤡")
        
        elif text == "/list":
            tracked_users = get_tracked_users(chat_id)
            if tracked_users:
                user_list = "\n".join([f"- @{user} (living rent-free in your head) 🤡" for user in tracked_users])
                level = get_stalker_level(len(tracked_users))
                send_message(chat_id, f"Your personal circus of obsession:\n{user_list}\n\nVictim count: {len(tracked_users)} 🤡\nCurrent title: {level}")
            else:
                send_message(chat_id, "Wow, no one to stalk? That's a new level of lonely 🤡\nUse /track to join the circus")

        elif text == "/stats":
            tracked_users = get_tracked_users(chat_id)
            count = len(tracked_users)
            level = get_stalker_level(count)
            achievements = get_stalker_achievements(count)
            if count == 0:
                send_message(chat_id, f"Zero people tracked. Even by circus standards, that's pathetic 🤡\nCurrent title: {level}")
            elif count < 3:
                send_message(chat_id, f"Only {count}? My grandma stalks more people than you 🤡\nCurrent title: {level}")
            elif count < 10:
                send_message(chat_id, f"{count} victims? Mediocrity at its finest 🤡\nCurrent title: {level}")
            else:
                send_message(chat_id, f"Tracking {count} people? Your parents must be so proud 🤡\nCurrent title: {level}")
            
            if achievements:
                send_message(chat_id, f"🤡 Your Circus Achievements:\n" + "\n".join(achievements))

        elif text == "/level":
            tracked_users = get_tracked_users(chat_id)
            count = len(tracked_users)
            level = get_stalker_level(count)
            next_level = STALKER_LEVELS[min(STALKER_LEVELS.index(level) + 1, len(STALKER_LEVELS) - 1)]
            send_message(chat_id, f"Current Role: {level}\n\nVictim Count: {count} 🤡\n\nNext Title: {next_level}\nKeep digging that hole deeper! 🤡")

        elif text == "/roast":
            tracked_users = get_tracked_users(chat_id)
            count = len(tracked_users)
            roasts = [
                f"Tracking {count} people? Your therapist is getting rich 🤡",
                f"{count} victims and still no one wants you 🤡",
                f"With {count} people to stalk, who needs a personality? 🤡",
                f"Imagine spending time on {count} people who don't know you exist 🤡",
                f"Your parents' disappointment grows with each of your {count} victims 🤡",
                f"{count} people to stalk? Get a hobby that doesn't require restraining orders 🤡",
                f"Congratulations on being {count} times more pathetic than average 🤡",
                f"Is stalking {count} people filling that void in your life? (Spoiler: No) 🤡"
            ]
            send_message(chat_id, random.choice(roasts))

        elif text == "/tips":
            tip = random.choice(STALKER_TIPS)
            send_message(chat_id, f"Circus Pro Tip:\n{tip}")

        elif text == "/achievements":
            tracked_users = get_tracked_users(chat_id)
            count = len(tracked_users)
            achievements = get_stalker_achievements(count)
            if achievements:
                send_message(chat_id, f"🤡 Your Circus Achievements:\n" + "\n".join(achievements))
            else:
                send_message(chat_id, "No achievements? You're failing at failing. Impressive. 🤡")

        elif text == "/start":
            send_message(chat_id, "Back for more emotional damage? Use /help to see all the ways you can disappoint yourself 🤡")

        elif text == "/help":
            help_message = """Welcome to the Circus 🤡

Your toolkit of self-destruction:
/track <username> - New victim unlocked
/untrack <username> - Pretend to move on
/list - Your wall of shame
/stats - Quantify your downward spiral
/level - Check your circus rank
/roast - Get reminded of your life choices
/tips - Learn from fellow clowns
/achievements - Celebrate hitting rock bottom
/help - Too dumb to remember? I got you

Example: /track instagram
Now go make your therapist proud 🤡"""
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

