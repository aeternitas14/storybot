# ClowTracker 🎪

A fun and sarcastic Instagram story tracking bot that helps you stay updated with your favorite accounts' stories.

## Features

- Track Instagram stories with fun, sarcastic messages
- Get roasted for your stalking habits
- Earn achievements and level up your stalking game
- Get pro stalking tips
- Multi-user support
- Automatic story alerts

## Commands

- `/track <username>` - Start stalking someone 🕵️‍♂️
- `/untrack <username>` - Stop being a creep 🙈
- `/list` - See your stalking list 📝
- `/stats` - See how much of a stalker you are 📊
- `/level` - Check your stalking level 🏆
- `/roast` - Get roasted for your stalking habits 🔥
- `/tips` - Get pro stalking tips 🎯
- `/achievements` - See your stalking achievements 🏅
- `/help` - Show all commands 💡

## Deployment

The bot is deployed on Fly.io. To deploy your own instance:

1. Install the [Fly.io CLI](https://fly.io/docs/hands-on/install-flyctl/)
2. Run `flyctl auth signup` or `flyctl auth login`
3. Run `flyctl launch` to create a new app
4. Set your bot token: `flyctl secrets set BOT_TOKEN=your_bot_token`
5. Deploy: `flyctl deploy`

## Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables:
   ```
   BOT_TOKEN=your_bot_token
   ```
4. Run the bot: `python3 run_bot.py`

## License

MIT License - Feel free to use and modify!