# Project Structure

```
telegram-llm-bot/
│
├── bot.py                      # Main bot application
│   ├── Message handlers
│   ├── Conversation history management
│   ├── Tool execution logic
│   └── LLM integration
│
├── llm/                        # LLM abstraction layer
│   ├── __init__.py            # Package exports
│   ├── base.py                # BaseLLM abstract interface
│   │   ├── Message dataclass
│   │   ├── ToolCall dataclass
│   │   ├── LLMResponse dataclass
│   │   └── BaseLLM abstract class
│   └── providers.py           # Concrete LLM implementations
│       ├── AnthropicLLM       # Claude integration
│       ├── OpenAILLM          # OpenAI integration
│       ├── OpenAICompatibleLLM # For Nebius, SambaNova, etc.
│       └── get_llm_provider() # Factory function
│
├── tools/                      # Bot tools and capabilities
│   ├── __init__.py            # Package exports
│   ├── web_tools.py           # Web scraping
│   │   ├── fetch_url()        # Fetch and extract web content
│   │   ├── extract_urls()     # Find URLs in text
│   │   ├── _fetch_with_requests()
│   │   └── _fetch_with_playwright()
│   ├── youtube_tools.py       # YouTube integration
│   │   ├── extract_video_id() # Parse YouTube URLs
│   │   ├── is_youtube_url()   # Check if URL is YouTube
│   │   ├── get_video_info()   # Get video metadata + transcript
│   │   └── format_video_info() # Format for display
│   └── search_tools.py        # Web search
│       ├── search_web()       # Main search function
│       ├── _search_duckduckgo() # DuckDuckGo implementation
│       ├── _search_brave()    # Brave Search API
│       ├── _search_tavily()   # Tavily API
│       └── format_search_results()
│
├── telegram-llm-env/          # Python virtual environment
│
├── requirements.txt           # Python dependencies
├── .env.example              # Configuration template
├── .gitignore               # Git ignore rules
│
├── README.md                # Full documentation
├── QUICKSTART.md           # Quick start guide
├── PROJECT_STRUCTURE.md    # This file
│
├── run.sh                  # Start script
└── test_llm.py            # LLM configuration tester
```

## Key Components

### 1. Bot Core ([bot.py](bot.py))

**Main Functions:**
- `initialize_llm()` - Set up LLM provider from env vars
- `handle_message()` - Process incoming Telegram messages
- `execute_tool()` - Run tools requested by LLM
- `should_respond()` - Determine if bot should reply (DM vs group)
- `extract_user_message()` - Handle forwarded/replied messages
- `add_to_history()` - Manage conversation history
- `get_history()` - Retrieve chat history

**Features:**
- Conversation history per chat (in-memory)
- Automatic YouTube link detection
- Tool calling with iteration loop
- Group and DM support
- Error handling

### 2. LLM Abstraction ([llm/](llm/))

**Design Pattern:** Abstract Factory

**Base Classes:**
- `Message` - Represents chat messages (user/assistant/system)
- `ToolCall` - Represents LLM tool/function calls
- `LLMResponse` - Unified response format
- `BaseLLM` - Abstract base class for all providers

**Providers:**
- `AnthropicLLM` - Claude via Anthropic API
- `OpenAILLM` - GPT via OpenAI API
- `OpenAICompatibleLLM` - Any OpenAI-compatible API

**Key Methods:**
- `generate()` - Generate LLM response
- `supports_tool_calling()` - Check for function calling support

### 3. Tools ([tools/](tools/))

**Web Tools:**
- Fetch web pages with requests + BeautifulSoup
- Optional Playwright for JavaScript-heavy sites
- Extract clean text content
- Handle timeouts and errors

**YouTube Tools:**
- Parse various YouTube URL formats
- Extract video metadata using yt-dlp
- Get transcripts via youtube-transcript-api
- Format information for display

**Search Tools:**
- DuckDuckGo (free, no API key)
- Brave Search API (paid)
- Tavily API (paid)
- Unified search interface

## Data Flow

```
User Message (Telegram)
    ↓
should_respond() - Check if bot should reply
    ↓
extract_user_message() - Parse message content
    ↓
add_to_history() - Add to conversation
    ↓
Detect YouTube URLs → get_video_info()
    ↓
llm.generate(messages, tools) - Generate response
    ↓
Tool Calls?
├─ Yes → execute_tool() → Add result to history → Loop
└─ No → Send response to user
    ↓
add_to_history() - Save bot response
```

## Configuration Flow

```
.env file
    ↓
load_dotenv() - Load environment variables
    ↓
get_llm_provider(provider, api_key, model, base_url)
    ↓
Returns appropriate LLM instance
    ↓
Used by bot for all generation
```

## Extension Points

### Adding a New LLM Provider

1. Create class in `llm/providers.py` inheriting `BaseLLM`
2. Implement `generate()` and `supports_tool_calling()`
3. Add to `get_llm_provider()` factory
4. Update `.env.example` and README

### Adding a New Tool

1. Create function in appropriate `tools/*.py` module
2. Add tool schema to `TOOLS` list in `bot.py`
3. Add execution logic in `execute_tool()`
4. Update documentation

### Adding New Commands

1. Create handler function in `bot.py`
2. Add `CommandHandler` in `main()`
3. Update `/start` help text

## Dependencies

**Core:**
- `python-telegram-bot` - Telegram bot framework
- `python-dotenv` - Environment variable management

**LLM SDKs:**
- `anthropic` - Claude API
- `openai` - OpenAI/compatible APIs

**Tools:**
- `requests` + `beautifulsoup4` - Web scraping
- `yt-dlp` - YouTube metadata
- `youtube-transcript-api` - Video transcripts
- `duckduckgo-search` - Free web search

**Optional:**
- `playwright` - JavaScript rendering
- `tavily-python` - Tavily search API

## Environment Variables

**Required:**
- `TELEGRAM_TOKEN` - Bot token from @BotFather
- `LLM_PROVIDER` - Provider name (anthropic/openai/openai-compatible)
- `LLM_API_KEY` - API key for LLM provider

**Optional:**
- `LLM_MODEL` - Model name (defaults to best for provider)
- `LLM_BASE_URL` - Base URL for OpenAI-compatible APIs
- `SEARCH_ENGINE` - Search engine (duckduckgo/brave/tavily)
- `BRAVE_API_KEY` - Brave Search API key
- `TAVILY_API_KEY` - Tavily API key
- `MAX_HISTORY_MESSAGES` - Chat history limit (default: 20)

## Development Workflow

1. **Setup:** Copy `.env.example` → `.env`
2. **Test LLM:** Run `python test_llm.py`
3. **Run Bot:** Run `./run.sh` or `python bot.py`
4. **Test in Telegram:** Message your bot
5. **Monitor Logs:** Check console output
6. **Debug:** Add logging, check tool execution
7. **Iterate:** Modify code, restart bot

## Production Considerations

**Not Included (add for production):**
- Persistent storage (database for history)
- Rate limiting per user
- Admin commands
- Usage tracking/analytics
- Deployment configuration (Docker, systemd)
- Health checks
- Monitoring/alerting
- Backup/restore
- Security hardening
- Cost tracking for API usage

**Recommended Additions:**
- Redis for conversation history
- PostgreSQL for user data
- Docker Compose setup
- Environment-specific configs
- Logging to file/service
- Error reporting (Sentry)
- CI/CD pipeline
