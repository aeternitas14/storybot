#!/bin/zsh

# Kill any existing Python processes
killall -9 Python 2>/dev/null || true

# Clear cache files
rm -rf __pycache__/* 2>/dev/null || true
rm -f *.pyc 2>/dev/null || true

# Clear log file
echo "" > log.txt

# Change to project directory
cd ~/storybot

# Activate virtual environment
source ~/venv/bin/activate

# Start the webhook server
nohup python3 run_bot.py > webhook.log 2>&1 &

# Start the story checker
nohup python3 instagram_monitor.py > monitor.log 2>&1 &

# Show process status
echo "Bot processes started:"
ps aux | grep -E "python3 (run_bot.py|instagram_monitor.py)" | grep -v grep

