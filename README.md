# ClowTracker 🎪

A sarcastic Telegram bot that helps you track Instagram stories with style! Built with Python, Flask, and a healthy dose of humor.

## Features 🎭

- Track Instagram stories of any public account
- Get instant notifications when new stories are posted
- Sarcastic responses and fun interactions
- Achievement system and stalking levels
- Health monitoring and metrics

### Commands 📝

- `/track <username>` - Start tracking someone's stories 🕵️‍♂️
- `/untrack <username>` - Stop tracking someone's stories 🙈
- `/list` - See all accounts you're tracking 📋
- `/stats` - Check your stalking statistics 📊
- `/level` - See your current stalking level 🏆
- `/roast` - Get roasted for your stalking habits 🔥
- `/tips` - Get pro stalking tips 🎯
- `/achievements` - View your stalking achievements 🏅
- `/help` - Show all available commands 💡

## Deployment 🚀

The bot is deployed on Fly.io with automatic health checks and monitoring.

### Prerequisites

- Python 3.x
- Playwright
- Flask
- Required Python packages in `requirements.txt`

### Environment Variables

- `BOT_TOKEN` - Your Telegram bot token
- `PORT` - Server port (default: 8080 on Fly.io, 5001 locally)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/clowtracker.git
cd clowtracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright:
```bash
playwright install chromium
playwright install-deps
```

### Running Locally

```bash
python3 run_bot.py
python3 instagram_monitor.py
```

### Deploying to Fly.io

1. Install Fly.io CLI
2. Login to Fly.io
3. Create the app:
```bash
flyctl apps create
```

4. Set up volumes:
```bash
flyctl volumes create clowtracker_data -r lax -n 2
```

5. Deploy:
```bash
flyctl deploy
```

## Monitoring 📊

- Health checks run every 30 seconds
- Metrics available at `/metrics`
- Logs accessible via `flyctl logs`

## Files 📁

- `run_bot.py` - Main Telegram bot server
- `instagram_monitor.py` - Instagram story monitoring
- `multi_tracker.py` - User tracking management
- `users.json` - User data storage
- `alert_states/` - Story state tracking

## Contributing 🤝

Feel free to contribute! Just don't make the bot too nice - we have a reputation to maintain. 😈

## License 📄

MIT License - Feel free to use it, but don't blame us for any stalking-related incidents! 🎭