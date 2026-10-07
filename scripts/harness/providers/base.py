from abc import ABC, abstractmethod
from dataclasses import dataclass
import re
from typing import Optional, Dict, Any, AsyncGenerator

TOKEN_PATTERNS = [
    re.compile(r"(gh[uopsr]_[A-Za-z0-9_]{16,})"),
    re.compile(r"(sk-[A-Za-z0-9_-]{20,})"),
    re.compile(r"(AIza[0-9A-Za-z-_]{35})"),
    re.compile(r"(Bearer\s+[A-Za-z0-9_.-]{16,})", re.IGNORECASE),
]

def redact_secrets(text: str) -> str:
    """Redacts potential API keys and tokens from strings."""
    if not isinstance(text, str):
        return text
    sanitized = text
    for pattern in TOKEN_PATTERNS:
        sanitized = pattern.sub("[REDACTED_CREDENTIAL]", sanitized)
    return sanitized


@dataclass
class AgentResponse:
    """Normalized response returned by any provider."""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    raw_payload: Optional[Dict[str, Any]] = None


class ProviderError(Exception):
    """Base exception for provider errors with credential redaction."""
    def __init__(self, message: str):
        safe_message = redact_secrets(str(message))
        super().__init__(safe_message)


class BaseAgentProvider(ABC):
    """
    Abstract interface for atomic LLM execution providers.
    Guarantees zero-history context window isolation per call.
    """

    def __init__(self, model: str):
        self.model = model

    @abstractmethod
    async def chat_atomic(
        self,
        prompt: str,
        system_prompt: str,
        **kwargs
    ) -> AgentResponse:
        """
        Executes an isolated, single-turn completion without context retention.
        """
        pass

    @abstractmethod
    async def stream_atomic(
        self,
        prompt: str,
        system_prompt: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Streams response tokens asynchronously in real time.
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} model='{self.model}'>"

    def __str__(self) -> str:
        return self.__repr__()
