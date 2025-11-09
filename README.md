# Telegram LLM Bot

A powerful Telegram bot that integrates with multiple LLM providers (Anthropic Claude, OpenAI, and OpenAI-compatible APIs) to provide intelligent responses with web search, URL fetching, and YouTube video analysis capabilities.

## Features

- **Multiple LLM Providers**: Easily switch between Anthropic Claude, OpenAI, or any OpenAI-compatible API (Nebius, SambaNova, Together AI, Groq, etc.)
- **Smart Conversation**: Maintains conversation history per chat for context-aware responses
- **Group Chat Support**: Responds when mentioned with `@botname` in groups, or to all messages in direct chats
- **Forwarded/Replied Messages**: Analyzes forwarded or replied-to messages when you mention the bot
- **Built-in Tools**:
  - Web search (DuckDuckGo, Brave Search, Tavily)
  - URL fetching and web scraping
  - YouTube video transcript extraction
- **Custom Commands**: Natural language commands like "verify claims", "provide context", "explain simply"
- **Tool Calling**: Native function calling support for compatible LLMs

## Architecture

The bot is designed with a clean abstraction layer that separates concerns:

```
telegram-llm-bot/
├── bot.py                 # Main bot logic
├── llm/                   # LLM abstraction layer
│   ├── __init__.py
│   ├── base.py           # Abstract LLM interface
│   └── providers.py      # Concrete implementations (Anthropic, OpenAI, etc.)
├── tools/                 # Bot tools/capabilities
│   ├── __init__.py
│   ├── web_tools.py      # URL fetching and web scraping
│   ├── youtube_tools.py  # YouTube video info and transcripts
│   └── search_tools.py   # Web search functionality
├── requirements.txt
├── .env.example
└── README.md
```

## Setup Instructions

### 1. Prerequisites

- Python 3.10 or higher
- A Telegram account
- API key for your chosen LLM provider

### 2. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the instructions
3. Choose a name and username for your bot
4. Save the API token provided by BotFather (you'll need this later)
5. (Optional) Configure your bot settings:
   - `/setdescription` - Set bot description
   - `/setabouttext` - Set about text
   - `/setuserpic` - Set bot profile picture

### 3. Clone and Setup

```bash
# Clone the repository (or download the code)
cd telegram-llm-bot

# Create a virtual environment
python3 -m venv telegram-llm-env

# Activate the virtual environment
# On Linux/Mac:
source telegram-llm-env/bin/activate
# On Windows:
# telegram-llm-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and configure your settings. See [Configuration Examples](#configuration-examples) below.

### 5. Run the Bot

```bash
# Make sure virtual environment is activated
python bot.py
```

The bot will start and begin polling for messages. You should see:
```
INFO - Starting bot...
```

## Configuration Examples

### Anthropic Claude (Recommended)

Claude offers excellent instruction-following and tool use capabilities.

```bash
# .env
TELEGRAM_TOKEN=your_telegram_bot_token
LLM_PROVIDER=anthropic
LLM_API_KEY=sk-ant-api03-xxx
LLM_MODEL=claude-3-5-sonnet-20241022
```

Get your API key from: https://console.anthropic.com/

**Available Models**:
- `claude-3-5-sonnet-20241022` (Recommended - best balance)
- `claude-3-opus-20240229` (Most capable)
- `claude-3-haiku-20240307` (Fastest, most economical)

### OpenAI

```bash
# .env
TELEGRAM_TOKEN=your_telegram_bot_token
LLM_PROVIDER=openai
LLM_API_KEY=sk-xxx
LLM_MODEL=gpt-4o
```

Get your API key from: https://platform.openai.com/api-keys

**Available Models**:
- `gpt-4o` (Recommended)
- `gpt-4o-mini` (Faster, cheaper)
- `gpt-4-turbo`

### Nebius AI Studio

Nebius provides free access to various open-source models.

```bash
# .env
TELEGRAM_TOKEN=your_telegram_bot_token
LLM_PROVIDER=openai-compatible
LLM_API_KEY=your_nebius_api_key
LLM_BASE_URL=https://api.studio.nebius.ai/v1
LLM_MODEL=meta-llama/Meta-Llama-3.1-70B-Instruct
```

Get your API key from: https://studio.nebius.ai/

### SambaNova

SambaNova offers fast inference for Llama models.

```bash
# .env
TELEGRAM_TOKEN=your_telegram_bot_token
LLM_PROVIDER=openai-compatible
LLM_API_KEY=your_sambanova_api_key
LLM_BASE_URL=https://api.sambanova.ai/v1
LLM_MODEL=Meta-Llama-3.1-405B-Instruct
```

Get your API key from: https://cloud.sambanova.ai/

### Together AI

```bash
# .env
TELEGRAM_TOKEN=your_telegram_bot_token
LLM_PROVIDER=openai-compatible
LLM_API_KEY=your_together_api_key
LLM_BASE_URL=https://api.together.xyz/v1
LLM_MODEL=meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo
```

Get your API key from: https://api.together.xyz/

### Groq

Groq provides extremely fast inference.

```bash
# .env
TELEGRAM_TOKEN=your_telegram_bot_token
LLM_PROVIDER=openai-compatible
LLM_API_KEY=your_groq_api_key
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.1-70b-versatile
```

Get your API key from: https://console.groq.com/

## How It Works

### LLM Abstraction Layer

The bot uses an abstraction layer to support multiple LLM providers:

1. **Base Interface** ([llm/base.py](llm/base.py)): Defines `BaseLLM` abstract class with a `generate()` method
2. **Providers** ([llm/providers.py](llm/providers.py)): Implements concrete classes for each provider
3. **Factory Pattern**: `get_llm_provider()` function returns the appropriate LLM instance based on configuration

This design allows you to:
- Switch providers by changing environment variables (no code changes)
- Add new providers by implementing the `BaseLLM` interface
- Use provider-specific features while maintaining a common interface

### Tool Integration

The bot supports two modes of tool integration:

#### 1. Native Tool Calling (Anthropic, OpenAI)

For providers that support function calling:

1. Tools are defined with JSON schemas in [bot.py](bot.py:165)
2. The LLM can request tool execution in its response
3. Bot executes the tool and adds results to conversation history
4. LLM generates a final response using the tool results

#### 2. Fallback Mode

For providers without native tool calling:

- Tools can still be invoked through natural language instructions
- The bot detects URLs and YouTube links automatically
- You can extend this with prompt engineering or manual tool detection

### Conversation History

Each chat (direct or group) has its own conversation history:

- Stored in-memory (cleared on bot restart)
- Limited to `MAX_HISTORY_MESSAGES` (default: 20) to manage token usage
- Includes system message, user messages, and assistant responses
- Tool results are added to history for context

To clear history in a chat, use the `/clear` command.

### Message Handling

The bot intelligently handles different message types:

1. **Direct Messages**: Responds to all messages
2. **Group Chats**: Responds only when:
   - Mentioned with `@botname`
   - Replying to a bot message
3. **Forwarded Messages**: Includes forwarded content in context
4. **Replies**: Includes the replied-to message in context
5. **YouTube Links**: Automatically fetches video info and transcript

## Usage Examples

### Basic Conversation

```
You: What's the weather like today?
Bot: I don't have real-time weather data. Let me search for current weather information...
[Bot searches the web and provides answer]
```

### Verify Claims

```
You: verify claims: "Coffee is bad for your health"
Bot: [Searches for evidence and provides fact-check]
```

### Analyze YouTube Videos

```
You: https://www.youtube.com/watch?v=dQw4w9WgXcQ
Bot: [Fetches video title, description, and transcript]

You: Summarize the main points from this video
Bot: [Uses transcript to provide summary]
```

### Fetch Web Pages

```
You: Can you read this article and summarize it? https://example.com/article
Bot: [Fetches article content and provides summary]
```

### Group Chat Usage

```
User1: @yourbot explain quantum computing simply
Bot: [Provides ELI5 explanation]

User2: @yourbot provide context about the recent tech news
Bot: [Searches and provides context]
```

## Available Commands

- `/start` - Show welcome message and bot capabilities
- `/clear` - Clear conversation history for the current chat

## Advanced Configuration

### Search Engines

The bot supports multiple search engines:

**DuckDuckGo** (Default, no API key needed):
```bash
SEARCH_ENGINE=duckduckgo
```

**Brave Search** (Requires API key from https://brave.com/search/api/):
```bash
SEARCH_ENGINE=brave
BRAVE_API_KEY=your_brave_api_key
```

**Tavily** (Requires API key from https://tavily.com/):
```bash
SEARCH_ENGINE=tavily
TAVILY_API_KEY=your_tavily_api_key
```

### Playwright for JavaScript Sites

Some websites require JavaScript rendering. To enable Playwright:

1. Uncomment in `requirements.txt`:
   ```
   playwright==1.49.0
   ```

2. Install Playwright:
   ```bash
   pip install playwright
   playwright install
   ```

3. The bot will automatically use Playwright when needed

### Conversation History Limit

Adjust the number of messages kept in history:

```bash
MAX_HISTORY_MESSAGES=30  # Increase for more context (uses more tokens)
```

## Troubleshooting

### Bot doesn't respond in groups

Make sure you:
1. Added the bot to the group
2. Mention the bot with `@botname` in your message
3. Check bot logs for errors

### Tool calling not working

- Verify your LLM provider supports tool calling
- Check logs to see if tools are being invoked
- For OpenAI-compatible providers, some may not support function calling

### Rate limiting errors

- Reduce `MAX_HISTORY_MESSAGES` to use fewer tokens
- Add delays between requests
- Check your API provider's rate limits

### Import errors

Make sure you installed all dependencies:
```bash
pip install -r requirements.txt
```

## Development

### Adding a New LLM Provider

1. Create a new class in [llm/providers.py](llm/providers.py) inheriting from `BaseLLM`
2. Implement the `generate()` and `supports_tool_calling()` methods
3. Add the provider to `get_llm_provider()` factory function
4. Update `.env.example` and README with configuration examples

### Adding a New Tool

1. Create tool function in appropriate module under `tools/`
2. Define tool schema in `TOOLS` list in [bot.py](bot.py:165)
3. Add tool execution logic in `execute_tool()` function
4. Update README with tool documentation

## Security Considerations

- **Never commit `.env` file** - It contains sensitive API keys
- Keep your `TELEGRAM_TOKEN` secret
- The bot stores conversation history in memory (not persistent)
- Consider rate limiting for production use
- Review and sanitize user inputs if deploying publicly

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Review the code comments in the source files
3. Open an issue on GitHub

## Acknowledgments

Built with:
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python)
- [OpenAI SDK](https://github.com/openai/openai-python)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [DuckDuckGo Search](https://github.com/deedy5/duckduckgo_search)
