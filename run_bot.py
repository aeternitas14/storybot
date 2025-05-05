import os
import json
import logging
from typing import Dict, List, Optional
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from instagram_monitor import InstagramMonitor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize bot and dispatcher
bot_token = os.getenv('BOT_TOKEN', '7569840561:AAHnbeez9FcYFM_IpwyxJ1AwaiqKA7r_jiA')
bot = Bot(token=bot_token)
dispatcher = Dispatcher(bot, None, use_context=True)

# Initialize Instagram monitor
monitor = InstagramMonitor()

def load_users() -> Dict[str, List[str]]:
    """Load users from the users file."""
    if not os.path.exists("users.json"):
        return {}
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading users: {e}")
        return {}

def save_users(users: Dict[str, List[str]]) -> None:
    """Save users to the users file."""
    try:
        with open("users.json", "w") as f:
            json.dump(users, f)
    except Exception as e:
        logger.error(f"Error saving users: {e}")

def add_user(chat_id: str, username: str) -> bool:
    """Add a user to the tracking list."""
    users = load_users()
    if str(chat_id) not in users:
        users[str(chat_id)] = []
    if username not in users[str(chat_id)]:
        users[str(chat_id)].append(username)
        save_users(users)
        return True
    return False

def remove_user(chat_id: str, username: str) -> bool:
    """Remove a user from the tracking list."""
    users = load_users()
    if str(chat_id) in users and username in users[str(chat_id)]:
        users[str(chat_id)].remove(username)
        if not users[str(chat_id)]:
            del users[str(chat_id)]
        save_users(users)
        return True
    return False

def start(update: Update, context: Any) -> None:
    """Handle the /start command."""
    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id,
        text="🎭 <b>Welcome to the Instagram Story Tracker!</b>\n\n"
             "I'll notify you when your favorite Instagram accounts post new stories.\n\n"
             "Commands:\n"
             "/track <username> - Start tracking an account\n"
             "/untrack <username> - Stop tracking an account\n"
             "/list - See all accounts you're tracking\n\n"
             "Example: /track instagram",
        parse_mode="HTML"
    )

def track(update: Update, context: Any) -> None:
    """Handle the /track command."""
    chat_id = update.effective_chat.id
    if not context.args:
        context.bot.send_message(
            chat_id=chat_id,
            text="❌ Please provide an Instagram username to track.\n"
                 "Example: /track instagram",
            parse_mode="HTML"
        )
        return

    username = context.args[0].lower()
    if add_user(chat_id, username):
        context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ Now tracking @{username}!\n"
                 "You'll be notified when they post new stories. 🎭",
            parse_mode="HTML"
        )
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text=f"ℹ️ You're already tracking @{username}!",
            parse_mode="HTML"
        )

def untrack(update: Update, context: Any) -> None:
    """Handle the /untrack command."""
    chat_id = update.effective_chat.id
    if not context.args:
        context.bot.send_message(
            chat_id=chat_id,
            text="❌ Please provide an Instagram username to stop tracking.\n"
                 "Example: /untrack instagram",
            parse_mode="HTML"
        )
        return

    username = context.args[0].lower()
    if remove_user(chat_id, username):
        context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ Stopped tracking @{username}.",
            parse_mode="HTML"
        )
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text=f"ℹ️ You weren't tracking @{username}.",
            parse_mode="HTML"
        )

def list_tracked(update: Update, context: Any) -> None:
    """Handle the /list command."""
    chat_id = update.effective_chat.id
    users = load_users()
    tracked = users.get(str(chat_id), [])
    
    if not tracked:
        context.bot.send_message(
            chat_id=chat_id,
            text="ℹ️ You're not tracking any Instagram accounts yet.\n"
                 "Use /track <username> to start tracking.",
            parse_mode="HTML"
        )
    else:
        message = "📋 <b>You're tracking these Instagram accounts:</b>\n\n"
        message += "\n".join([f"• @{username}" for username in tracked])
        context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode="HTML"
        )

def error_handler(update: Optional[Update], context: Any) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_chat:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ An error occurred. Please try again later.",
            parse_mode="HTML"
        )

# Register handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("track", track))
dispatcher.add_handler(CommandHandler("untrack", untrack))
dispatcher.add_handler(CommandHandler("list", list_tracked))
dispatcher.add_error_handler(error_handler)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook updates."""
    if request.method == "POST":
        try:
            update = Update.de_json(request.get_json(force=True), bot)
            dispatcher.process_update(update)
            return "ok"
        except Exception as e:
            logger.error(f"Error processing webhook update: {e}")
            return "error", 500
    return "method not allowed", 405

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return "ok"

if __name__ == '__main__':
    # Start the Flask app
    port = int(os.getenv('PORT', 443))
    app.run(host='0.0.0.0', port=port)

