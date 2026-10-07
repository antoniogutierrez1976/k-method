import os
from typing import Optional, AsyncGenerator
from .base import BaseAgentProvider, AgentResponse, ProviderError, redact_secrets


class CopilotProvider(BaseAgentProvider):
    """
    GitHub Copilot SDK provider adapter.
    Enables execution of models such as GPT-6 Luna and Sol via enterprise Copilot or BYOK.
    """

    def __init__(self, model: str = "gpt-6-luna", api_token: Optional[str] = None):
        super().__init__(model=model)
        self._api_token = api_token or os.environ.get("GITHUB_TOKEN") or os.environ.get("COPILOT_API_KEY")

    def _get_client(self, system_prompt: str):
        """
        Dynamically imports and initializes the GitHub Copilot SDK agent session.
        Allows mocking in tests without requiring live network connections.
        """
        try:
            from github_copilot_sdk import CopilotAgent, SessionConfig
            config = SessionConfig(
                model=self.model,
                system_instructions=system_prompt,
                api_token=self._api_token,
            )
            return CopilotAgent(config=config)
        except ImportError as e:
            raise ProviderError(
                "GitHub Copilot SDK is not installed. Install with: pip install github-copilot-sdk"
            ) from e
        except Exception as e:
            raise ProviderError(f"Failed to initialize CopilotAgent: {e}") from e

    async def chat_atomic(
        self,
        prompt: str,
        system_prompt: str,
        **kwargs
    ) -> AgentResponse:
        try:
            client = self._get_client(system_prompt=system_prompt)
            result = await client.send_message(prompt)
            content = getattr(result, "content", str(result))
            usage = getattr(result, "usage", None)
            return AgentResponse(content=content, model=self.model, usage=usage)
        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError(f"Copilot execution failed: {e}") from e

    async def stream_atomic(
        self,
        prompt: str,
        system_prompt: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        res = await self.chat_atomic(prompt, system_prompt, **kwargs)
        for chunk in res.content.splitlines(keepends=True):
            yield chunk

    def __repr__(self) -> str:
        return f"<CopilotProvider model='{self.model}' auth_configured={bool(self._api_token)}>"

    def __str__(self) -> str:
        return self.__repr__()
