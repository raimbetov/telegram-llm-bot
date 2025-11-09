"""
Base LLM interface for the Telegram bot.

This module defines the abstract base class that all LLM providers must implement.
This abstraction allows easy switching between different LLM providers (Anthropic, OpenAI, etc.)
without changing the bot's core logic.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Message:
    """Represents a chat message with role and content."""
    role: str  # 'user', 'assistant', or 'system'
    content: str


@dataclass
class ToolCall:
    """Represents a tool/function call made by the LLM."""
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class LLMResponse:
    """Represents the response from an LLM."""
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, int]] = None


class BaseLLM(ABC):
    """
    Abstract base class for LLM providers.

    All LLM implementations (Anthropic, OpenAI, etc.) must inherit from this class
    and implement the `generate` method. This ensures a consistent interface across
    all providers.
    """

    def __init__(self, api_key: str, model: str, **kwargs):
        """
        Initialize the LLM provider.

        Args:
            api_key: API key for the LLM provider
            model: Model name/identifier to use
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.model = model
        self.config = kwargs

    @abstractmethod
    def generate(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from the LLM.

        Args:
            messages: List of conversation messages
            tools: Optional list of tool definitions for function calling
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse object containing the generated content and any tool calls
        """
        pass

    @abstractmethod
    def supports_tool_calling(self) -> bool:
        """
        Check if this LLM provider supports native tool/function calling.

        Returns:
            True if the provider supports tool calling, False otherwise
        """
        pass
