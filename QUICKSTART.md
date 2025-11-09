# Quick Start Guide

Get your Telegram LLM bot running in 5 minutes!

## Step 1: Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Follow the prompts to name your bot
4. Save the API token (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Step 2: Get an LLM API Key

Choose one provider:

### Anthropic Claude (Recommended)
- Go to: https://console.anthropic.com/
- Sign up and get API key
- You'll get free credits to start

### OpenAI
- Go to: https://platform.openai.com/
- Sign up and create API key
- Requires payment setup

### Nebius (Free)
- Go to: https://studio.nebius.ai/
- Sign up for free access
- Get API key

## Step 3: Configure the Bot

```bash
# Copy the example config
cp .env.example .env

# Edit the config file
nano .env  # or use any text editor
```

**Minimal configuration** (for Anthropic):
```bash
TELEGRAM_TOKEN=your_bot_token_from_botfather
LLM_PROVIDER=anthropic
LLM_API_KEY=your_anthropic_api_key
```

**For Nebius** (free alternative):
```bash
TELEGRAM_TOKEN=your_bot_token_from_botfather
LLM_PROVIDER=openai-compatible
LLM_API_KEY=your_nebius_api_key
LLM_BASE_URL=https://api.studio.nebius.ai/v1
LLM_MODEL=meta-llama/Meta-Llama-3.1-70B-Instruct
```

## Step 4: Run the Bot

```bash
# Using the provided script
./run.sh

# OR manually
source telegram-llm-env/bin/activate
python bot.py
```

You should see:
```
INFO - Initialized LLM provider: anthropic with model: claude-3-5-sonnet-20241022
INFO - Starting bot...
```

## Step 5: Test Your Bot

1. Open Telegram and search for your bot by username
2. Click "Start" or send `/start`
3. Try these test messages:

```
Hello! Can you help me?

What's the weather like today?

https://www.youtube.com/watch?v=dQw4w9WgXcQ
Summarize this video

Search for the latest news about AI
```

## Troubleshooting

### "TELEGRAM_TOKEN environment variable is required"
- Make sure you created `.env` file
- Check that the token is correct (no extra spaces)

### "LLM_API_KEY environment variable is required"
- Add your API key to `.env` file
- Make sure there are no quotes around the key

### Bot doesn't respond in groups
- Make sure you mention the bot: `@yourbotname your message`
- OR reply to one of the bot's messages

### Rate limiting / Too many requests
- Wait a few minutes
- Reduce MAX_HISTORY_MESSAGES in `.env`

## Next Steps

- Read the full [README.md](README.md) for advanced features
- Try different LLM providers
- Customize the system prompt in [bot.py](bot.py:309)
- Add the bot to group chats
- Enable additional search engines (Brave, Tavily)

## Commands

- `/start` - Welcome message
- `/clear` - Clear conversation history

## Support

If you have issues:
1. Check the bot logs for errors
2. Verify your API keys are valid
3. Make sure you have internet connection
4. Check the [README.md](README.md) troubleshooting section

Enjoy your AI-powered Telegram bot!
