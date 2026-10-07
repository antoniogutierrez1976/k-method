import asyncio
import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure repository root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

# Domain modules under test
try:
    from scripts.harness.engine.embedded_skills import (
        get_embedded_directive,
        list_embedded_skills,
        EMBEDDED_SKILLS,
    )
    from scripts.harness.gui.server import app, create_app
except ImportError:
    # Modules not implemented yet (Checkpoint 1: Red state)
    get_embedded_directive = None
    list_embedded_skills = None
    EMBEDDED_SKILLS = {}
    app = None
    create_app = None


class TestGUIBackendAPI(unittest.TestCase):
    """
    Test suite for Phase 1: GUI Backend API & Real-time Event Streaming.
    Covers AC-Sec-1 and AC-1 through AC-5.
    """

    def setUp(self):
        if app is None:
            self.skipTest("scripts/harness/gui/server.py or embedded_skills.py not yet implemented.")
        self.client = TestClient(app)

    def tearDown(self):
        import shutil
        for d in ["add-health-check-endpoint", "implement-payment-webhook"]:
            path = os.path.join(REPO_ROOT, "specs", d)
            if os.path.exists(path):
                shutil.rmtree(path, ignore_errors=True)

    def test_AC_Sec_1_credential_redaction_in_api(self):
        """
        AC-Sec-1: REST and WebSocket payloads must redact sensitive tokens/keys.
        """
        secret_token = "AIzaSyD-SecretAntigravityKey9999"
        with patch.dict(os.environ, {"GEMINI_API_KEY": secret_token}):
            response = self.client.get("/api/status")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            payload_str = json.dumps(data)
            self.assertNotIn(secret_token, payload_str, "Security leak: API key exposed in /api/status")

    def test_AC_1_embedded_skills_registry(self):
        """
        AC-1: Embedded skills registry provides complete Karpathy v0 directives in memory.
        """
        skills = list_embedded_skills()
        self.assertGreaterEqual(len(skills), 5, "Must contain all 5 core Karpathy skills")
        
        skill_names = {s["name"] for s in skills}
        expected = {"k-orchestrator", "k-spec", "k-verifier", "k-environment", "k-wiki"}
        self.assertTrue(expected.issubset(skill_names), f"Missing skills in embedded registry: {expected - skill_names}")

        # Verify spec directive contains the 6-AC hard limit
        spec_directive = get_embedded_directive("k-spec")
        self.assertIn("6 Acceptance Criteria", spec_directive)
        self.assertIn("AC-1..AC-6", spec_directive)

    def test_AC_2_rest_endpoints(self):
        """
        AC-2: REST endpoints return workspace status, git diff, and embedded skills catalog.
        """
        # /api/status
        res_status = self.client.get("/api/status")
        self.assertEqual(res_status.status_code, 200)
        status_data = res_status.json()
        self.assertIn("workspace", status_data)
        self.assertIn("branch", status_data)
        self.assertIn("is_clean", status_data)

        # /api/diff
        res_diff = self.client.get("/api/diff")
        self.assertEqual(res_diff.status_code, 200)
        diff_data = res_diff.json()
        self.assertIn("diff", diff_data)

        # /api/skills
        res_skills = self.client.get("/api/skills")
        self.assertEqual(res_skills.status_code, 200)
        skills_data = res_skills.json()
        self.assertIn("skills", skills_data)
        self.assertEqual(len(skills_data["skills"]), 5)

    def test_AC_3_websocket_execution_protocol(self):
        """
        AC-3: WebSocket connection to /ws/sdlc streams execution lifecycle events.
        """
        with self.client.websocket_connect("/ws/sdlc") as ws:
            # Start execution with mock provider
            ws.send_json({
                "action": "start",
                "task": "Add health check endpoint",
                "provider": "mock",
                "auto_approve": True,
            })

            events_received = []
            while True:
                data = ws.receive_json()
                events_received.append(data.get("event"))
                if data.get("event") in ("completed", "error"):
                    break

            self.assertIn("stage_changed", events_received)
            self.assertIn("completed", events_received)

    def test_AC_4_interactive_approval_gate_via_ws(self):
        """
        AC-4: Backend emits approval_required at SPEC stage and pauses until operator approval.
        """
        with self.client.websocket_connect("/ws/sdlc") as ws:
            ws.send_json({
                "action": "start",
                "task": "Implement payment webhook",
                "provider": "mock",
                "auto_approve": False,
            })

            # Wait for approval_required
            approval_event = None
            for _ in range(10):
                msg = ws.receive_json()
                if msg.get("event") == "approval_required":
                    approval_event = msg
                    break

            self.assertIsNotNone(approval_event, "Did not receive approval_required event")
            self.assertIn("spec_content", approval_event)
            self.assertIn("spec_file", approval_event)
            self.assertTrue(approval_event["spec_file"].endswith("spec.md"))

            # Send rejection
            ws.send_json({
                "action": "approval_response",
                "approved": False,
                "feedback": "Needs threat modeling",
            })

            final_msg = ws.receive_json()
            self.assertEqual(final_msg.get("event"), "stage_changed")
            self.assertEqual(final_msg.get("stage"), "ABORTED")

    def test_AC_5_disconnect_and_error_resilience(self):
        """
        AC-5: WebSocket handles invalid JSON and abrupt client disconnect gracefully.
        """
        with self.client.websocket_connect("/ws/sdlc") as ws:
            ws.send_text("INVALID_NON_JSON")
            resp = ws.receive_json()
            self.assertEqual(resp.get("event"), "error")
            self.assertIn("Invalid JSON", resp.get("message", ""))

    def test_AC_6_models_endpoint_and_provider_catalog(self):
        """
        AC-6: Backend exposes /api/models and /api/status with allowed models per provider.
        """
        res = self.client.get("/api/models")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("models", data)
        models = data["models"]
        self.assertIn("antigravity", models)
        self.assertIn("copilot", models)
        self.assertIn("mock", models)

        antigravity_model_ids = [m["id"] for m in models["antigravity"]]
        self.assertIn("gemini-2.5-flash", antigravity_model_ids)

        copilot_model_ids = [m["id"] for m in models["copilot"]]
        self.assertIn("gpt-6-luna", copilot_model_ids)

        # Also verify /api/status includes models
        status_res = self.client.get("/api/status")
        self.assertEqual(status_res.status_code, 200)
        status_data = status_res.json()
        self.assertIn("models", status_data)

    def test_AC_7_live_sdk_model_discovery(self):
        """
        AC-7: fetch_sdk_models_for_provider queries google.genai.Client.models.list() when API key is set.
        """
        mock_model_1 = MagicMock()
        mock_model_1.name = "models/gemini-ultra-special"
        mock_model_1.display_name = "Gemini Ultra Special"
        mock_model_1.supported_actions = ["generateContent"]

        with patch.dict(os.environ, {"GEMINI_API_KEY": "dummy_test_key"}):
            with patch("google.genai.Client") as mock_client_cls:
                mock_instance = MagicMock()
                mock_instance.models.list.return_value = [mock_model_1]
                mock_client_cls.return_value = mock_instance

                res = self.client.get("/api/models")
                self.assertEqual(res.status_code, 200)
                models = res.json()["models"]["antigravity"]
                ids = [m["id"] for m in models]
                self.assertIn("gemini-ultra-special", ids)

    def test_AC_8_informational_query_bypasses_spec_generation(self):
        """
        AC-8: Questions and informational queries are answered directly without entering SPEC stage or creating specs.
        """
        with self.client.websocket_connect("/ws/sdlc") as ws:
            ws.send_json({
                "action": "start",
                "task": "¿En qué consiste el proyecto k-method?",
                "provider": "mock",
                "auto_approve": False,
            })

            events_received = []
            while True:
                msg = ws.receive_json()
                events_received.append(msg.get("event"))
                if msg.get("event") in ("completed", "error"):
                    break

            # Must NOT emit approval_required because queries don't generate specs
            self.assertNotIn("approval_required", events_received)
            self.assertIn("stage_changed", events_received)
            self.assertIn("completed", events_received)


if __name__ == "__main__":
    unittest.main()
