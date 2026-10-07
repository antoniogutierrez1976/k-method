from typing import Optional
from .base import BaseAgentProvider
from .mock_provider import MockProvider
from .copilot_provider import CopilotProvider
from .antigravity_provider import AntigravityProvider


class ProviderFactory:
    """
    Factory creating configured provider adapters.
    """

    @staticmethod
    def create(
        provider_type: str,
        model: Optional[str] = None,
        **kwargs
    ) -> BaseAgentProvider:
        normalized_type = provider_type.strip().lower()
        
        if normalized_type == "mock":
            target_model = model or "mock-model"
            return MockProvider(model=target_model, **kwargs)
        
        elif normalized_type == "copilot":
            target_model = model or "gpt-6-luna"
            return CopilotProvider(model=target_model, **kwargs)
        
        elif normalized_type == "antigravity":
            target_model = model or "gemini-3.8-flash"
            return AntigravityProvider(model=target_model, **kwargs)
        
        else:
            raise ValueError(
                f"Unknown provider type '{provider_type}'. Supported providers: 'copilot', 'antigravity', 'mock'."
            )
