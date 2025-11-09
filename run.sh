#!/bin/bash
# Quick start script for the Telegram LLM bot

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your settings:"
    echo "  cp .env.example .env"
    echo "  nano .env  # or use your preferred editor"
    exit 1
fi

# Activate virtual environment
source telegram-llm-env/bin/activate

# Run the bot
python bot.py
