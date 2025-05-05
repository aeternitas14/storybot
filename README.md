# Instagram Story Alert Bot

A Telegram bot that alerts users when tracked Instagram accounts post new stories.

## Features

- Track multiple Instagram accounts
- Receive instant alerts when stories are posted
- Multi-user support (multiple Telegram users can track different accounts)
- Prevents duplicate alerts for the same story
- Robust error handling and state management

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/storybot.git
cd storybot
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure the bot:
   - Create a Telegram bot using [@BotFather](https://t.me/botfather)
   - Get your bot token and set it in `run_bot.py` and `multi_tracker.py`
   - Log in to Instagram and save the session state to `state.json`

4. Start the bot:
```bash
./run_bot.sh
```

## Usage

1. Start a chat with your bot on Telegram
2. Use the `/track <username>` command to start tracking an Instagram account
3. You'll receive alerts whenever the tracked accounts post new stories

## Deployment

The bot can be deployed to [Fly.io](https://fly.io):

1. Install the [Fly CLI](https://fly.io/docs/hands-on/install-flyctl/)
2. Login to Fly.io: `fly auth login`
3. Deploy: `fly deploy`

## Architecture

- `run_bot.py`: Telegram webhook server for receiving commands
- `instagram_monitor.py`: Main story monitoring class
- `multi_tracker.py`: Helper for managing user tracking
- `run_bot.sh`: Script to start both services

## State Management

- `users.json`: Stores which Instagram accounts each Telegram user is tracking
- `alert_states/`: Directory containing state files for each tracked account
- `state.json`: Instagram session state for authentication

## Error Handling

The bot includes robust error handling for:
- Network issues
- Instagram API changes
- Invalid usernames
- Duplicate alerts
- State file corruption

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request