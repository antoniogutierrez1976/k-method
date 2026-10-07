import unittest
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch

# Add repository root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.harness.providers.base import (
    BaseAgentProvider,
    AgentResponse,
    ProviderError,
)
from scripts.harness.providers.factory import ProviderFactory
from scripts.harness.providers.mock_provider import MockProvider
from scripts.harness.providers.copilot_provider import CopilotProvider
from scripts.harness.providers.antigravity_provider import AntigravityProvider


class TestProviderAdapters(unittest.IsolatedAsyncioTestCase):
    """
    Test suite enforcing Layer 2 (Verifier) for Phase 1: Multi-Provider Adapters.
    Covers AC-Sec-1 and AC-1 through AC-5.
    """

    async def test_AC_Sec_1_credential_redaction(self):
        """
        AC-Sec-1: Provider representations and exceptions must redact sensitive credentials.
        """
        token = "ghu_SecretToken1234567890abcdef"
        provider = CopilotProvider(model="gpt-6-luna", api_token=token)
        
        # Test __repr__ and __str__ do not expose token
        self.assertNotIn(token, repr(provider), "Security leak: API token exposed in repr()")
        self.assertNotIn(token, str(provider), "Security leak: API token exposed in str()")
        
        # Test exception string redaction
        err = ProviderError(f"Authentication failed with token: {token}")
        self.assertNotIn(token, str(err), "Security leak: API token exposed in ProviderError message")

        # Test AntigravityProvider credential redaction
        api_key = "AIzaSyD-SecretAntigravityKey12345678"
        agy_provider = AntigravityProvider(api_key=api_key)
        self.assertNotIn(api_key, repr(agy_provider), "Security leak: API key exposed in AntigravityProvider repr()")
        self.assertNotIn(api_key, str(agy_provider), "Security leak: API key exposed in AntigravityProvider str()")

    async def test_AC_1_factory_and_mock(self):
        """
        AC-1 (Happy Path - Factory & Mock): ProviderFactory creates functional mock provider.
        """
        provider = ProviderFactory.create("mock", mock_responses=["Test response content"])
        self.assertIsInstance(provider, MockProvider)
        
        response = await provider.chat_atomic(prompt="Hello", system_prompt="System instructions")
        self.assertIsInstance(response, AgentResponse)
        self.assertEqual(response.content, "Test response content")
        self.assertEqual(response.model, "mock-model")

    async def test_AC_2_copilot_adapter(self):
        """
        AC-2 (Happy Path - Copilot Adapter): CopilotProvider interacts with Copilot runtime and returns AgentResponse.
        """
        provider = CopilotProvider(model="gpt-6-luna", api_token="dummy_token")
        
        # Mock Copilot SDK response
        mock_copilot_response = MagicMock()
        mock_copilot_response.content = "Response from GPT-6 Luna via Copilot SDK"
        
        mock_agent_instance = AsyncMock()
        mock_agent_instance.send_message.return_value = mock_copilot_response
        
        with patch.object(provider, "_get_client", return_value=mock_agent_instance):
            response = await provider.chat_atomic(prompt="Write test", system_prompt="Act as verifier")
            self.assertIsInstance(response, AgentResponse)
            self.assertEqual(response.content, "Response from GPT-6 Luna via Copilot SDK")
            self.assertEqual(response.model, "gpt-6-luna")
            mock_agent_instance.send_message.assert_awaited_once_with("Write test")

    async def test_AC_3_antigravity_adapter(self):
        """
        AC-3 (Happy Path - Antigravity Adapter): AntigravityProvider maps capabilities and streams content into AgentResponse.
        """
        provider = AntigravityProvider(model="gemini-3.8-flash", allow_write=False, allow_terminal=False)
        
        # Mock Antigravity Agent async stream
        async def mock_token_generator(prompt):
            tokens = ["Hello ", "from ", "Antigravity!"]
            for t in tokens:
                yield t

        mock_agent_instance = MagicMock()
        mock_agent_instance.__aenter__ = AsyncMock(return_value=mock_agent_instance)
        mock_agent_instance.__aexit__ = AsyncMock(return_value=None)
        mock_agent_instance.chat = AsyncMock(return_value=mock_token_generator("prompt"))
        
        with patch.object(provider, "_spawn_agent", return_value=mock_agent_instance):
            response = await provider.chat_atomic(prompt="Explain architecture", system_prompt="System instructions")
            self.assertIsInstance(response, AgentResponse)
            self.assertEqual(response.content, "Hello from Antigravity!")
            self.assertEqual(response.model, "gemini-3.8-flash")

    async def test_AC_4_error_normalization(self):
        """
        AC-4 (Edge Case - Error Normalization): Unhandled SDK exceptions are wrapped in ProviderError.
        """
        provider = CopilotProvider(model="gpt-6-luna")
        
        mock_agent_instance = AsyncMock()
        mock_agent_instance.send_message.side_effect = ConnectionResetError("Network failure")
        
        with patch.object(provider, "_get_client", return_value=mock_agent_instance):
            with self.assertRaises(ProviderError) as ctx:
                await provider.chat_atomic(prompt="Test", system_prompt="Test")
            self.assertIn("Network failure", str(ctx.exception))

    async def test_AC_5_atomic_zero_history(self):
        """
        AC-5 (Boundary - Atomic Zero-History): Successive calls to chat_atomic do not leak context across turns.
        """
        provider = MockProvider(mock_responses=["First reply", "Second reply"])
        
        res1 = await provider.chat_atomic(prompt="Turn 1", system_prompt="Context 1")
        res2 = await provider.chat_atomic(prompt="Turn 2", system_prompt="Context 2")
        
        self.assertEqual(res1.content, "First reply")
        self.assertEqual(res2.content, "Second reply")
        
        # Check history was recorded independently in calls log with zero state bleeding
        self.assertEqual(len(provider.call_history), 2)
        self.assertEqual(provider.call_history[0]["prompt"], "Turn 1")
        self.assertEqual(provider.call_history[1]["prompt"], "Turn 2")
        self.assertEqual(provider.call_history[0]["system_prompt"], "Context 1")
        self.assertEqual(provider.call_history[1]["system_prompt"], "Context 2")

    async def test_factory_all_provider_branches(self):
        """
        Verify ProviderFactory branches for copilot, antigravity and invalid types.
        """
        copilot_p = ProviderFactory.create("copilot", model="gpt-6.1-sol")
        self.assertIsInstance(copilot_p, CopilotProvider)
        self.assertEqual(copilot_p.model, "gpt-6.1-sol")

        agy_p = ProviderFactory.create("antigravity", model="gemini-2.0-flash")
        self.assertIsInstance(agy_p, AntigravityProvider)
        self.assertEqual(agy_p.model, "gemini-2.0-flash")

        with self.assertRaises(ValueError):
            ProviderFactory.create("unsupported_provider")

    async def test_streaming_atomic_tokens(self):
        """
        Verify stream_atomic across providers.
        """
        mock_p = MockProvider(mock_responses=["Token1 Token2 Token3"])
        tokens = []
        async for t in mock_p.stream_atomic("Prompt", "System"):
            tokens.append(t)
        self.assertEqual(tokens, ["Token1 ", "Token2 ", "Token3 "])

    async def test_import_error_normalization(self):
        """
        Verify ProviderError when SDK packages are missing.
        """
        copilot_p = CopilotProvider()
        with patch.dict("sys.modules", {"github_copilot_sdk": None}):
            with self.assertRaises(ProviderError) as ctx:
                copilot_p._get_client("Sys")
            self.assertIn("GitHub Copilot SDK is not installed", str(ctx.exception))

        agy_p = AntigravityProvider()
        with patch.dict("sys.modules", {"google.antigravity": None}):
            with self.assertRaises(ProviderError) as ctx:
                agy_p._spawn_agent("Sys")
            self.assertIn("Google Antigravity SDK is not installed", str(ctx.exception))

    async def test_antigravity_missing_api_key_error(self):
        """
        Verify AntigravityProvider raises clear ProviderError if GEMINI_API_KEY is missing.
        """
        env_clean = {k: v for k, v in os.environ.items() if k not in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENAI_USE_VERTEXAI", "GOOGLE_GENAI_USE_ENTERPRISE")}
        with patch.dict(os.environ, env_clean, clear=True):
            agy_p = AntigravityProvider()
            with self.assertRaises(ProviderError) as ctx:
                agy_p._spawn_agent("Sys")
            self.assertIn("Se requiere una API Key de Gemini", str(ctx.exception))
            self.assertIn("https://aistudio.google.com/app/apikey", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
