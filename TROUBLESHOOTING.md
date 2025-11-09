# Troubleshooting Guide

Common issues and solutions for the Telegram LLM bot.

## Configuration Issues

### Error: "TELEGRAM_TOKEN environment variable is required"

**Cause:** `.env` file not found or TELEGRAM_TOKEN not set

**Solution:**
```bash
# Make sure .env exists
ls .env

# If not, copy from example
cp .env.example .env

# Edit and add your token
nano .env
```

Add:
```
TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

### Error: "LLM_API_KEY environment variable is required"

**Cause:** API key not set in `.env`

**Solution:**
```bash
# Edit .env and add your API key
nano .env
```

Add:
```
LLM_API_KEY=your_actual_api_key_here
```

**Note:** Don't use quotes around the value.

### Error: "Unsupported provider"

**Cause:** Invalid LLM_PROVIDER value

**Solution:**
Valid values are:
- `anthropic`
- `openai`
- `openai-compatible`

Example:
```
LLM_PROVIDER=anthropic
```

### Error: "base_url is required for openai-compatible provider"

**Cause:** Using `openai-compatible` without LLM_BASE_URL

**Solution:**
```
LLM_PROVIDER=openai-compatible
LLM_BASE_URL=https://api.studio.nebius.ai/v1
```

## Bot Runtime Issues

### Bot starts but doesn't respond

**Check 1:** In direct messages?
- Bot should respond to all DMs
- Try `/start` command

**Check 2:** In group chat?
- Bot only responds when mentioned: `@yourbotname message`
- Or when replying to bot's message

**Check 3:** Check logs
```bash
# Look for errors in console output
# Should see: "INFO - Starting bot..."
```

**Check 4:** Verify bot token
```bash
# Test with curl
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
```

Should return bot info, not error.

### Error: "Unauthorized" or "Invalid token"

**Cause:** Wrong Telegram bot token

**Solution:**
1. Go to @BotFather on Telegram
2. Send `/mybots`
3. Select your bot
4. Click "API Token"
5. Copy the correct token to `.env`

### Error: "Invalid API key" (Anthropic/OpenAI)

**Cause:** Wrong or expired API key

**Solution:**
1. Check your API key is correct (no extra spaces)
2. Verify key is active in provider dashboard:
   - Anthropic: https://console.anthropic.com/
   - OpenAI: https://platform.openai.com/
3. Check you have credits/quota remaining

### Bot stops responding after a few messages

**Possible causes:**

**1. Rate limiting**
```bash
# Check logs for rate limit errors
# Wait a few minutes, then try again

# Reduce history size in .env
MAX_HISTORY_MESSAGES=10
```

**2. Token limit exceeded**
```bash
# Clear conversation history
# In Telegram, send: /clear

# Or reduce history limit in .env
MAX_HISTORY_MESSAGES=10
```

**3. API quota exceeded**
- Check your API provider dashboard
- Add more credits or wait for quota reset

## Tool-Related Issues

### Web search not working

**DuckDuckGo errors:**
```bash
# Make sure package is installed
source telegram-llm-env/bin/activate
pip install duckduckgo-search --upgrade
```

**Brave/Tavily errors:**
```bash
# Make sure API key is set
nano .env

# Add:
BRAVE_API_KEY=your_key
# or
TAVILY_API_KEY=your_key

# Set search engine
SEARCH_ENGINE=brave
```

### YouTube transcript not available

**Possible causes:**
1. Video has no captions/transcript
2. Captions are disabled
3. Video is age-restricted or private

**Solution:**
- Try a different video
- Bot will still fetch title and description
- Check logs to see specific error

### URL fetching fails

**Timeout errors:**
```bash
# Some sites take long to load
# This is normal, bot has 10s timeout
```

**JavaScript-required sites:**
```bash
# Install Playwright (optional)
pip install playwright
playwright install

# Bot will auto-use Playwright for JS sites
```

**Blocked by site:**
- Some sites block bots
- Try a different URL
- Not much can be done without proxy rotation

## Import/Dependency Errors

### ImportError: No module named 'anthropic'

**Cause:** Dependencies not installed

**Solution:**
```bash
# Make sure virtual env is activated
source telegram-llm-env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### ImportError: No module named 'telegram'

**Cause:** Wrong package or virtual env not activated

**Solution:**
```bash
# Activate virtual environment
source telegram-llm-env/bin/activate

# Reinstall telegram bot
pip install python-telegram-bot==20.8
```

### ModuleNotFoundError: No module named 'llm'

**Cause:** Running from wrong directory

**Solution:**
```bash
# Make sure you're in project root
cd /path/to/telegram-llm-bot

# Run bot
python bot.py
```

## Performance Issues

### Bot is slow to respond

**Possible causes:**

**1. Large conversation history**
```bash
# Reduce in .env
MAX_HISTORY_MESSAGES=10
```

**2. Slow LLM model**
```bash
# Use faster model
# For Anthropic:
LLM_MODEL=claude-3-haiku-20240307

# For OpenAI:
LLM_MODEL=gpt-4o-mini
```

**3. Tool calls take time**
- Web searches: 2-5 seconds
- YouTube transcripts: 3-10 seconds
- This is normal

### High API costs

**Solutions:**
```bash
# 1. Use cheaper models
LLM_MODEL=claude-3-haiku-20240307  # Anthropic
LLM_MODEL=gpt-4o-mini              # OpenAI

# 2. Reduce context size
MAX_HISTORY_MESSAGES=10

# 3. Use free provider
LLM_PROVIDER=openai-compatible
LLM_BASE_URL=https://api.studio.nebius.ai/v1
LLM_MODEL=meta-llama/Meta-Llama-3.1-70B-Instruct
```

## Group Chat Issues

### Bot responds to every message in group

**Not expected behavior** - check if:
1. Bot username is in every message
2. Bot is replying to its own messages

**Should only respond when:**
- Mentioned: `@botname message`
- Replying to bot's message

### Bot doesn't respond when mentioned

**Check 1:** Correct username?
```bash
# Make sure you use the right username
# Check in @BotFather: /mybots
```

**Check 2:** Bot has permissions?
- Make sure bot is a member of the group
- Bot has permission to read messages
- In group settings, check bot permissions

## Advanced Debugging

### Enable verbose logging

Edit [bot.py](bot.py:37):
```python
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Change from INFO to DEBUG
)
```

### Test LLM connection separately

```bash
python test_llm.py
```

This will:
- Verify API key works
- Test model access
- Check tool calling support

### Check conversation history

Add to [bot.py](bot.py) in `handle_message()`:
```python
# After getting history
history = get_history(chat_id)
print(f"History has {len(history)} messages")
for msg in history:
    print(f"  {msg.role}: {msg.content[:50]}...")
```

### Monitor API calls

Add logging to [llm/providers.py](llm/providers.py):
```python
# In generate() method
logger.info(f"Calling API with {len(messages)} messages")
logger.info(f"Response: {response}")
```

### Test individual tools

```python
# Test in Python REPL
from tools import search_web, fetch_url, get_video_info

# Test search
result = search_web("Python programming")
print(result)

# Test URL fetch
result = fetch_url("https://example.com")
print(result)

# Test YouTube
result = get_video_info("https://youtube.com/watch?v=...")
print(result)
```

## Common Error Messages

### "This chat is not a group chat"
- Trying to use group-only features in DM
- Ignore, not an error

### "Message is too long"
- Response exceeds Telegram's 4096 character limit
- Bot should handle this, if not, report as bug

### "Bad Request: wrong file identifier/http url specified"
- Issue with media handling
- Check if trying to send invalid URLs

### Connection errors / Timeout
- Network issue or API is down
- Wait and retry
- Check API status pages

## Still Having Issues?

1. **Check logs carefully** - errors usually have good descriptions
2. **Test components separately**:
   - Run `python test_llm.py`
   - Test tools in Python REPL
   - Verify bot token with curl
3. **Search for error message** - likely others had same issue
4. **Check API provider status** - might be downtime
5. **Simplify configuration** - use minimal .env to isolate issue

## Getting Help

When asking for help, include:
1. Exact error message from logs
2. Your configuration (hide API keys!):
   ```
   LLM_PROVIDER=anthropic
   LLM_MODEL=claude-3-5-sonnet-20241022
   SEARCH_ENGINE=duckduckgo
   ```
3. What you were trying to do
4. What you've already tried

## Reporting Bugs

If you found a bug:
1. Check if it's in this troubleshooting guide
2. Make sure dependencies are up to date
3. Test with minimal configuration
4. Include:
   - Python version: `python --version`
   - OS: `uname -a` (Linux/Mac)
   - Error logs
   - Steps to reproduce
