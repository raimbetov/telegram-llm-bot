# Deployment Guide

## Deploying to Railway

Railway is a platform that makes it easy to deploy and host your Telegram bot.

### Prerequisites

1. A GitHub account with your repository pushed
2. A Railway account (sign up at https://railway.app)
3. Your bot token and LLM API key ready

### Deployment Steps

#### 1. Push Your Code to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR-USERNAME/telegram-llm-bot.git
git branch -M main
git push -u origin main
```

#### 2. Deploy to Railway

1. Go to [Railway](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Select your `telegram-llm-bot` repository
5. Railway will automatically detect the Python project

#### 3. Configure Environment Variables

In the Railway dashboard for your project:

1. Go to the **Variables** tab
2. Add the following environment variables:

**Required:**
- `TELEGRAM_TOKEN` - Your bot token from @BotFather
- `LLM_PROVIDER` - e.g., `openai-compatible`
- `LLM_API_KEY` - Your LLM API key
- `LLM_MODEL` - e.g., `llama-3.3-70b-versatile`
- `LLM_BASE_URL` - e.g., `https://api.groq.com/openai/v1`

**Optional:**
- `SEARCH_ENGINE` - Default: `duckduckgo`
- `MAX_HISTORY_MESSAGES` - Default: `20`
- `BRAVE_API_KEY` - If using Brave Search
- `TAVILY_API_KEY` - If using Tavily Search

#### 4. Deploy

Railway will automatically:
1. Install dependencies from `requirements.txt`
2. Start the bot using `Procfile`
3. Keep the bot running 24/7

#### 5. Monitor Your Bot

In the Railway dashboard:
- **Deployments** tab: See deployment status
- **Logs** tab: View bot logs in real-time
- **Metrics** tab: Monitor resource usage

### Important Notes

#### Pricing

Railway offers:
- **Free tier**: $5 credit per month (usually enough for a bot)
- **Pro tier**: Pay for what you use

Monitor your usage to stay within limits.

#### Bot Restarts

The bot will automatically restart if it crashes (configured in `railway.json`).

#### Environment Variables

Never commit your `.env` file! Railway uses its own environment variable system.

#### Updates

To update your bot:
```bash
git add .
git commit -m "Update message"
git push
```

Railway will automatically redeploy.

### Troubleshooting

#### Bot Not Starting

1. Check logs in Railway dashboard
2. Verify all required environment variables are set
3. Check that `TELEGRAM_TOKEN` is correct

#### Bot Not Responding

1. Check logs for errors
2. Verify LLM API key is valid and has credits
3. Test locally first with `python bot.py`

#### Out of Memory

If the bot crashes due to memory:
1. Reduce `MAX_HISTORY_MESSAGES` (try `10`)
2. Consider upgrading Railway plan
3. Check for memory leaks in logs

### Alternative Deployment Options

- **Heroku**: Similar to Railway, use same Procfile
- **Google Cloud Run**: Containerized deployment
- **AWS EC2**: Traditional VPS hosting
- **DigitalOcean**: VPS with more control
- **Render**: Another PaaS option
- **VPS**: Any VPS with Python 3.10+

For VPS deployment, simply:
```bash
git clone https://github.com/YOUR-USERNAME/telegram-llm-bot.git
cd telegram-llm-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys
python bot.py
```

Use `screen`, `tmux`, or `systemd` to keep it running.

### Production Best Practices

1. **Monitoring**: Set up alerts for bot downtime
2. **Backups**: Keep your configuration backed up
3. **Updates**: Regularly update dependencies
4. **Security**: Rotate API keys periodically
5. **Logs**: Monitor logs for errors or abuse
6. **Rate Limiting**: Be aware of API rate limits

### Cost Optimization

- Use cheaper LLM models (e.g., `gpt-4o-mini` or Groq's free tier)
- Reduce `MAX_HISTORY_MESSAGES` to save tokens
- Use DuckDuckGo search (free) instead of paid alternatives
- Monitor usage to avoid unexpected costs

### Support

- Railway Docs: https://docs.railway.app/
- Railway Discord: https://discord.gg/railway
- Check bot logs first when troubleshooting
