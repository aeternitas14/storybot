FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create necessary directories
RUN mkdir -p alert_states

# Set environment variables
ENV PORT=8080
ENV BOT_TOKEN=${BOT_TOKEN}

# Run both the webhook server and story checker
CMD nohup python3 instagram_monitor.py > monitor.log 2>&1 & gunicorn -b 0.0.0.0:$PORT run_bot:app

