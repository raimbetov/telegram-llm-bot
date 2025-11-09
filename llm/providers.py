"""
Concrete implementations of LLM providers.

This module contains implementations for:
- Anthropic (Claude)
- OpenAI (GPT models)
- OpenAI-compatible APIs (Nebius, SambaNova, Together, etc.)
"""

import json
import logging
from typing import List, Dict, Any, Optional

from llm.base import BaseLLM, Message, LLMResponse, ToolCall

logger = logging.getLogger(__name__)


class AnthropicLLM(BaseLLM):
    """Anthropic Claude implementation."""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", **kwargs):
        super().__init__(api_key, model, **kwargs)
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("Please install anthropic: pip install anthropic")

    def supports_tool_calling(self) -> bool:
        return True

    def generate(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate response using Anthropic API."""
        # Convert messages to Anthropic format
        # Anthropic requires system messages to be passed separately
        system_messages = [msg.content for msg in messages if msg.role == "system"]
        conversation_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
            if msg.role != "system"
        ]

        api_params = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": conversation_messages,
        }

        if system_messages:
            api_params["system"] = "\n\n".join(system_messages)

        if tools:
            api_params["tools"] = tools

        try:
            response = self.client.messages.create(**api_params)

            # Extract content
            content = ""
            tool_calls = []

            for block in response.content:
                if block.type == "text":
                    content += block.text
                elif block.type == "tool_use":
                    tool_calls.append(
                        ToolCall(
                            id=block.id,
                            name=block.name,
                            arguments=block.input
                        )
                    )

            usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }

            return LLMResponse(
                content=content,
                tool_calls=tool_calls if tool_calls else None,
                finish_reason=response.stop_reason,
                usage=usage
            )

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise


class OpenAILLM(BaseLLM):
    """OpenAI implementation."""

    def __init__(self, api_key: str, model: str = "gpt-4o", base_url: Optional[str] = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        try:
            import openai
            client_kwargs = {"api_key": api_key}
            if base_url:
                client_kwargs["base_url"] = base_url
            self.client = openai.OpenAI(**client_kwargs)
        except ImportError:
            raise ImportError("Please install openai: pip install openai")

    def supports_tool_calling(self) -> bool:
        return True

    def generate(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate response using OpenAI API."""
        # Convert messages to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        api_params = {
            "model": self.model,
            "messages": openai_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if tools:
            # Convert tools to OpenAI function calling format
            api_params["tools"] = [
                {"type": "function", "function": tool}
                for tool in tools
            ]

        try:
            response = self.client.chat.completions.create(**api_params)

            message = response.choices[0].message
            content = message.content or ""
            tool_calls = []

            if message.tool_calls:
                for tc in message.tool_calls:
                    tool_calls.append(
                        ToolCall(
                            id=tc.id,
                            name=tc.function.name,
                            arguments=json.loads(tc.function.arguments)
                        )
                    )

            usage = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            }

            return LLMResponse(
                content=content,
                tool_calls=tool_calls if tool_calls else None,
                finish_reason=response.choices[0].finish_reason,
                usage=usage
            )

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise


class OpenAICompatibleLLM(OpenAILLM):
    """
    OpenAI-compatible API implementation.

    Works with providers that implement OpenAI's API format:
    - Nebius AI Studio
    - SambaNova
    - Together AI
    - Groq
    - Local deployments (vLLM, text-generation-webui, etc.)
    """

    def __init__(self, api_key: str, model: str, base_url: str, **kwargs):
        if not base_url:
            raise ValueError("base_url is required for OpenAI-compatible providers")
        super().__init__(api_key, model, base_url, **kwargs)
        self._supports_tools = kwargs.get("supports_tools", True)
        logger.info(f"Initialized OpenAI-compatible provider with base_url: {base_url}")

    def supports_tool_calling(self) -> bool:
        # Some OpenAI-compatible providers don't support tool calling
        # Can be configured via supports_tools parameter
        return self._supports_tools


def get_llm_provider(
    provider: str,
    api_key: str,
    model: str,
    base_url: Optional[str] = None,
    **kwargs
) -> BaseLLM:
    """
    Factory function to get the appropriate LLM provider.

    Args:
        provider: Provider name ('anthropic', 'openai', 'openai-compatible')
        api_key: API key for the provider
        model: Model name to use
        base_url: Base URL for OpenAI-compatible providers
        **kwargs: Additional provider-specific configuration

    Returns:
        BaseLLM instance

    Raises:
        ValueError: If provider is not supported
    """
    provider = provider.lower()

    if provider == "anthropic":
        return AnthropicLLM(api_key, model, **kwargs)
    elif provider == "openai":
        return OpenAILLM(api_key, model, base_url, **kwargs)
    elif provider == "openai-compatible":
        if not base_url:
            raise ValueError("base_url is required for openai-compatible provider")
        return OpenAICompatibleLLM(api_key, model, base_url, **kwargs)
    else:
        raise ValueError(
            f"Unsupported provider: {provider}. "
            f"Supported providers: anthropic, openai, openai-compatible"
        )
