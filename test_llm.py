#!/usr/bin/env python3
"""
Test script to validate LLM configuration.

Run this to test your LLM setup before starting the bot:
    python test_llm.py
"""

import os
from dotenv import load_dotenv
from llm import get_llm_provider, Message

# Load environment variables
load_dotenv()

def test_llm_connection():
    """Test the LLM provider configuration."""
    print("=" * 60)
    print("Testing LLM Configuration")
    print("=" * 60)

    # Get configuration
    provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
    api_key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL")
    base_url = os.getenv("LLM_BASE_URL")

    print(f"\nProvider: {provider}")
    print(f"API Key: {'*' * 20}{api_key[-10:] if api_key else 'NOT SET'}")
    print(f"Model: {model if model else 'default'}")
    if base_url:
        print(f"Base URL: {base_url}")

    if not api_key:
        print("\n❌ ERROR: LLM_API_KEY not set in .env file")
        return False

    try:
        # Initialize LLM
        print("\n⏳ Initializing LLM provider...")

        # Set default models
        if not model:
            if provider == "anthropic":
                model = "claude-3-5-sonnet-20241022"
            elif provider == "openai":
                model = "gpt-4o"
            else:
                model = "gpt-4o"

        llm = get_llm_provider(
            provider=provider,
            api_key=api_key,
            model=model,
            base_url=base_url,
        )

        print("✅ LLM provider initialized successfully")
        print(f"   Supports tool calling: {llm.supports_tool_calling()}")

        # Test a simple message
        print("\n⏳ Sending test message...")
        messages = [
            Message(role="user", content="Say 'Hello! I am working correctly.' and nothing else.")
        ]

        response = llm.generate(
            messages=messages,
            max_tokens=50,
            temperature=0.7
        )

        print("\n✅ Response received:")
        print(f"   Content: {response.content}")
        if response.usage:
            print(f"   Tokens used: {response.usage}")

        print("\n" + "=" * 60)
        print("✅ SUCCESS! Your LLM configuration is working!")
        print("=" * 60)
        print("\nYou can now run the bot with:")
        print("  python bot.py")
        print("or")
        print("  ./run.sh")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nPlease check:")
        print("  1. Your API key is correct")
        print("  2. You have sufficient credits/quota")
        print("  3. The provider name is correct")
        print("  4. For openai-compatible, the base URL is correct")
        return False


if __name__ == "__main__":
    test_llm_connection()
