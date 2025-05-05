FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p alert_states

# Start both services
CMD ["sh", "-c", "python run_bot.py & python instagram_monitor.py"]

