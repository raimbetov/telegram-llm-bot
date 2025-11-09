"""
Telegram LLM Bot

A Telegram bot that uses LLMs to respond to messages with support for:
- Multiple LLM providers (Anthropic, OpenAI, OpenAI-compatible)
- Tool calling (web search, URL fetching, YouTube transcripts)
- Conversation history per chat
- Group chat and direct message support
"""

import os
import logging
import json
import re
from typing import Dict, List, Optional
from collections import defaultdict

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.constants import ChatAction

from dotenv import load_dotenv

from llm import get_llm_provider, Message, BaseLLM
from tools import (
    fetch_url,
    extract_urls,
    get_video_info,
    is_youtube_url,
    format_video_info,
    search_web,
    format_search_results,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic").lower()
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
SEARCH_ENGINE = os.getenv("SEARCH_ENGINE", "duckduckgo").lower()
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))

# Access control
ALLOWED_USERS = set(
    int(uid.strip()) for uid in os.getenv("ALLOWED_USERS", "").split(",") if uid.strip()
)
ALLOWED_GROUPS = set(
    int(gid.strip()) for gid in os.getenv("ALLOWED_GROUPS", "").split(",") if gid.strip()
)

# Conversation history storage (in-memory)
# Structure: {chat_id: [Message, Message, ...]}
conversation_history: Dict[int, List[Message]] = defaultdict(list)

# Initialize LLM provider
llm: BaseLLM = None


def initialize_llm():
    """Initialize the LLM provider based on environment variables."""
    global llm

    if not LLM_API_KEY:
        raise ValueError("LLM_API_KEY environment variable is required")

    # Set default models if not specified
    if not LLM_MODEL:
        if LLM_PROVIDER == "anthropic":
            model = "claude-3-5-sonnet-20241022"
        elif LLM_PROVIDER == "openai":
            model = "gpt-4o"
        else:
            model = os.getenv("LLM_MODEL", "gpt-4o")
    else:
        model = LLM_MODEL

    # Disable tool calling for Groq - it has very buggy/incomplete support
    supports_tools = False if "groq.com" in str(LLM_BASE_URL) else True

    llm = get_llm_provider(
        provider=LLM_PROVIDER,
        api_key=LLM_API_KEY,
        model=model,
        base_url=LLM_BASE_URL,
        supports_tools=supports_tools,
    )

    logger.info(f"Initialized LLM provider: {LLM_PROVIDER} with model: {model} (tools: {supports_tools})")

    # Log access control settings
    if ALLOWED_USERS or ALLOWED_GROUPS:
        logger.info(f"Access control enabled - Allowed users: {ALLOWED_USERS}, Allowed groups: {ALLOWED_GROUPS}")
    else:
        logger.info("Access control disabled - Bot is public")


# Define tools for LLM function calling
TOOLS = [
    {
        "name": "search_web",
        "description": "Search the web for information. Use this when you need to find current information, verify facts, or answer questions that require up-to-date knowledge.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            },
            "required": ["query"],
            "additionalProperties": False
        }
    },
    {
        "name": "fetch_url",
        "description": "Fetch and extract content from a web page URL. Use this to read articles, documentation, or any web page content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to fetch"
                }
            },
            "required": ["url"],
            "additionalProperties": False
        }
    },
    {
        "name": "get_youtube_info",
        "description": "Get information and transcript from a YouTube video. Use this when the user shares a YouTube link or asks about a video.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The YouTube video URL"
                }
            },
            "required": ["url"],
            "additionalProperties": False
        }
    },
]


def execute_tool(tool_name: str, arguments: Dict) -> str:
    """
    Execute a tool and return the result as a string.

    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments

    Returns:
        Tool execution result as a string
    """
    try:
        if tool_name == "search_web":
            query = arguments.get("query")
            # Default to 5 results if not specified
            max_results = 5
            result = search_web(query, max_results, SEARCH_ENGINE)
            return format_search_results(result)

        elif tool_name == "fetch_url":
            url = arguments.get("url")
            result = fetch_url(url)
            if result["success"]:
                return f"**{result['title']}**\n\nURL: {result['url']}\n\n{result['content']}"
            else:
                return f"Error fetching URL: {result.get('error', 'Unknown error')}"

        elif tool_name == "get_youtube_info":
            url = arguments.get("url")
            result = get_video_info(url)
            return format_video_info(result)

        else:
            return f"Unknown tool: {tool_name}"

    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        return f"Error executing {tool_name}: {str(e)}"


def add_to_history(chat_id: int, message: Message):
    """
    Add a message to conversation history.

    Args:
        chat_id: Telegram chat ID
        message: Message to add
    """
    conversation_history[chat_id].append(message)

    # Trim history if it exceeds max length
    if len(conversation_history[chat_id]) > MAX_HISTORY_MESSAGES:
        # Keep system message if present, trim oldest user/assistant messages
        system_messages = [msg for msg in conversation_history[chat_id] if msg.role == "system"]
        other_messages = [msg for msg in conversation_history[chat_id] if msg.role != "system"]
        other_messages = other_messages[-(MAX_HISTORY_MESSAGES - len(system_messages)):]
        conversation_history[chat_id] = system_messages + other_messages


def get_history(chat_id: int) -> List[Message]:
    """
    Get conversation history for a chat.

    Args:
        chat_id: Telegram chat ID

    Returns:
        List of messages
    """
    return conversation_history[chat_id]


def should_respond(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Determine if the bot should respond to a message.

    In direct chats: respond to all messages
    In group chats: respond only when mentioned

    Args:
        update: Telegram update
        context: Bot context

    Returns:
        True if bot should respond, False otherwise
    """
    message = update.message

    # Always respond to direct messages
    if message.chat.type == "private":
        return True

    # In groups, check if bot is mentioned
    bot_username = context.bot.username
    if message.text:
        # Check for @botname mention
        if f"@{bot_username}" in message.text:
            return True

    # Check if message is a reply to the bot
    if message.reply_to_message and message.reply_to_message.from_user.id == context.bot.id:
        return True

    return False


def extract_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """
    Extract the user's message, handling replies and forwarded messages.

    Args:
        update: Telegram update
        context: Bot context

    Returns:
        Extracted message text
    """
    message = update.message
    parts = []

    # Handle forwarded message
    if message.forward_from or message.forward_from_chat:
        parts.append("[Forwarded message]")

    # Handle reply to another message
    if message.reply_to_message:
        replied_text = message.reply_to_message.text or message.reply_to_message.caption or "[No text]"
        parts.append(f"[Replying to: {replied_text}]")

    # Get the actual message text
    text = message.text or message.caption or ""

    # Remove bot mention from group messages
    if message.chat.type != "private":
        bot_username = context.bot.username
        text = text.replace(f"@{bot_username}", "").strip()

    parts.append(text)

    return "\n".join(parts)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle incoming messages.

    Args:
        update: Telegram update
        context: Bot context
    """
    try:
        if not should_respond(update, context):
            return

        chat_id = update.message.chat_id
        user_id = update.effective_user.id

        # Access control check
        if ALLOWED_USERS or ALLOWED_GROUPS:
            # If chat is a group, check against ALLOWED_GROUPS
            if chat_id < 0:  # Negative IDs are groups/channels
                if chat_id not in ALLOWED_GROUPS:
                    logger.warning(f"Unauthorized group access attempt: {chat_id}")
                    return
            # If chat is a direct message, check against ALLOWED_USERS
            else:
                if user_id not in ALLOWED_USERS:
                    logger.warning(f"Unauthorized user access attempt: {user_id}")
                    return

        user_message = extract_user_message(update, context)

        if not user_message.strip():
            return

        logger.info(f"Chat {chat_id}: User message: {user_message[:100]}...")

        # Send typing indicator
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

        # Initialize conversation with system message if empty
        if not conversation_history[chat_id]:
            system_message = Message(
                role="system",
                content=(
                    "You are a helpful AI assistant in a Telegram chat. "
                    "You can search the web, fetch web pages, and analyze YouTube videos. "
                    "When asked to verify claims, provide context, suggest alternatives, or explain simply, "
                    "use the available tools to gather accurate information. "
                    "Be concise but thorough in your responses."
                )
            )
            add_to_history(chat_id, system_message)

        # Add user message to history
        add_to_history(chat_id, Message(role="user", content=user_message))

        # Check for YouTube URLs in the message
        urls = extract_urls(user_message)
        youtube_urls = [url for url in urls if is_youtube_url(url)]

        # If there are YouTube URLs, automatically fetch info
        if youtube_urls:
            for yt_url in youtube_urls:
                await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
                yt_info = get_video_info(yt_url)
                formatted_info = format_video_info(yt_info)
                # Add YouTube info to context
                add_to_history(
                    chat_id,
                    Message(role="assistant", content=f"[YouTube video info]\n{formatted_info}")
                )

        # Generate response with tool support
        max_iterations = 5  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Get conversation history
            history = get_history(chat_id)

            # Generate response
            await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            response = llm.generate(
                messages=history,
                tools=TOOLS if llm.supports_tool_calling() else None,
                max_tokens=4096,
                temperature=0.7,
            )

            # Check if there are tool calls
            if response.tool_calls:
                logger.info(f"Chat {chat_id}: LLM requested {len(response.tool_calls)} tool calls")

                # Execute each tool call
                for tool_call in response.tool_calls:
                    tool_name = tool_call.name
                    tool_args = tool_call.arguments

                    logger.info(f"Chat {chat_id}: Executing tool {tool_name} with args {tool_args}")

                    # Execute tool
                    tool_result = execute_tool(tool_name, tool_args)

                    # Add tool result to history
                    # For Anthropic, we need to add the assistant message with tool use first
                    if LLM_PROVIDER == "anthropic":
                        # Add assistant message with tool use
                        add_to_history(
                            chat_id,
                            Message(role="assistant", content=response.content or f"[Using tool: {tool_name}]")
                        )
                        # Add tool result as user message
                        add_to_history(
                            chat_id,
                            Message(role="user", content=f"[Tool result for {tool_name}]\n{tool_result}")
                        )
                    else:
                        # For OpenAI, add tool result differently
                        add_to_history(
                            chat_id,
                            Message(role="assistant", content=f"[Used tool: {tool_name}]")
                        )
                        add_to_history(
                            chat_id,
                            Message(role="user", content=f"[Tool result]\n{tool_result}")
                        )

                # Continue to next iteration to get final response
                continue

            # No tool calls, send response to user
            if response.content:
                # Add assistant response to history
                add_to_history(chat_id, Message(role="assistant", content=response.content))

                # Send response to user
                await update.message.reply_text(response.content)

                logger.info(f"Chat {chat_id}: Sent response ({len(response.content)} chars)")
                break
            else:
                # Empty response, ask for clarification
                await update.message.reply_text("I'm not sure how to respond. Could you rephrase your question?")
                break

        if iteration >= max_iterations:
            await update.message.reply_text("I encountered an issue processing your request. Please try again.")

    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)
        await update.message.reply_text("Sorry, I encountered an error processing your message.")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    welcome_message = (
        "Hello! I'm an AI assistant powered by LLMs.\n\n"
        "I can:\n"
        "- Answer questions and have conversations\n"
        "- Search the web for information\n"
        "- Fetch and analyze web pages\n"
        "- Extract information from YouTube videos\n"
        "- Verify claims and provide context\n\n"
        "In direct messages, just send me a message.\n"
        "In groups, mention me with @botname to get my attention.\n\n"
        "Try commands like:\n"
        "• 'verify claims' - fact-check statements\n"
        "• 'provide context' - get background info\n"
        "• 'suggest alternatives' - explore different explanations\n"
        "• 'explain simply' or 'eli5' - simplify complex topics"
    )
    await update.message.reply_text(welcome_message)


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /clear command to clear conversation history."""
    chat_id = update.message.chat_id
    if chat_id in conversation_history:
        conversation_history[chat_id].clear()
    await update.message.reply_text("Conversation history cleared!")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)


def main():
    """Start the bot."""
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN environment variable is required")

    # Initialize LLM
    initialize_llm()

    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    # Start bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
