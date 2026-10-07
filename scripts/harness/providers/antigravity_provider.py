import os
from typing import Optional, AsyncGenerator
from .base import BaseAgentProvider, AgentResponse, ProviderError


class AntigravityProvider(BaseAgentProvider):
    """
    Google Antigravity SDK provider adapter.
    Enables local testing and native integration with Antigravity workspace capabilities.
    """

    def __init__(
        self,
        model: str = "gemini-3.8-flash",
        allow_write: bool = False,
        allow_terminal: bool = False,
        api_key: Optional[str] = None,
    ):
        super().__init__(model=model)
        self.allow_write = allow_write
        self.allow_terminal = allow_terminal
        self._api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    def _spawn_agent(self, system_prompt: str):
        """
        Dynamically imports and configures the Antigravity Agent instance.
        """
        try:
            from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig
        except ImportError as e:
            raise ProviderError(
                "Google Antigravity SDK is not installed. Install with: pip install google-antigravity"
            ) from e

        is_vertex = (
            os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() in ("true", "1")
            or os.environ.get("GOOGLE_GENAI_USE_ENTERPRISE", "").lower() in ("true", "1")
        )
        if not self._api_key and not is_vertex:
            raise ProviderError(
                "Se requiere una API Key de Gemini para usar Antigravity SDK.\n"
                "1. Obtén una clave gratuita en: https://aistudio.google.com/app/apikey\n"
                "2. Configúrala en PowerShell antes de ejecutar:\n"
                "   $env:GEMINI_API_KEY = '<tu_clave>'\n"
                "3. O pásala como parámetro: AntigravityProvider(api_key='...')"
            )

        try:
            capabilities = CapabilitiesConfig(
                allow_write=self.allow_write,
                allow_terminal=self.allow_terminal,
            )
            config_kwargs = {
                "model": self.model,
                "system_instructions": system_prompt,
                "capabilities": capabilities,
            }
            if self._api_key:
                config_kwargs["api_key"] = self._api_key
            config = LocalAgentConfig(**config_kwargs)
            return Agent(config)
        except Exception as e:
            raise ProviderError(f"Failed to spawn Antigravity Agent: {e}") from e

    async def chat_atomic(
        self,
        prompt: str,
        system_prompt: str,
        **kwargs
    ) -> AgentResponse:
        try:
            agent = self._spawn_agent(system_prompt=system_prompt)
            if hasattr(agent, "__aenter__"):
                async with agent as active_agent:
                    chat_result = await active_agent.chat(prompt)
                    collected = []
                    if hasattr(chat_result, "__aiter__"):
                        async for token in chat_result:
                            collected.append(str(token))
                    elif hasattr(chat_result, "__iter__"):
                        for token in chat_result:
                            collected.append(str(token))
                    else:
                        collected.append(str(chat_result))
                    content = "".join(collected)
            else:
                chat_result = await agent.chat(prompt)
                collected = []
                if hasattr(chat_result, "__aiter__"):
                    async for token in chat_result:
                        collected.append(str(token))
                elif hasattr(chat_result, "__iter__"):
                    for token in chat_result:
                        collected.append(str(token))
                else:
                    collected.append(str(chat_result))
                content = "".join(collected)

            return AgentResponse(content=content, model=self.model)
        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError(f"Antigravity execution failed: {e}") from e

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
        return (
            f"<AntigravityProvider model='{self.model}' "
            f"allow_write={self.allow_write} allow_terminal={self.allow_terminal} "
            f"auth_configured={bool(self._api_key)}>"
        )

    def __str__(self) -> str:
        return self.__repr__()
