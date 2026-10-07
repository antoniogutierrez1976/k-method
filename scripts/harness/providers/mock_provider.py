from typing import List, Optional, AsyncGenerator, Dict, Any
from .base import BaseAgentProvider, AgentResponse


class MockProvider(BaseAgentProvider):
    """
    Deterministic mock provider for offline testing and verification.
    """

    def __init__(self, model: str = "mock-model", mock_responses: Optional[List[str]] = None):
        super().__init__(model=model)
        self.mock_responses = list(mock_responses or ["Mock response default"])
        self.response_index = 0
        self.call_history: List[Dict[str, Any]] = []

    async def chat_atomic(
        self,
        prompt: str,
        system_prompt: str,
        **kwargs
    ) -> AgentResponse:
        self.call_history.append({
            "prompt": prompt,
            "system_prompt": system_prompt,
            "kwargs": kwargs,
        })
        
        if self.response_index < len(self.mock_responses):
            content = self.mock_responses[self.response_index]
            self.response_index += 1
        else:
            content = self.mock_responses[-1] if self.mock_responses else ""

        return AgentResponse(
            content=content,
            model=self.model,
            usage={"prompt_tokens": len(prompt) // 4, "completion_tokens": len(content) // 4},
        )

    async def stream_atomic(
        self,
        prompt: str,
        system_prompt: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        res = await self.chat_atomic(prompt, system_prompt, **kwargs)
        for token in res.content.split(" "):
            yield token + " "
