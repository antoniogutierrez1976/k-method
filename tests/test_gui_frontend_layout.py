import os
import sys
import unittest
from fastapi.testclient import TestClient

# Ensure repo root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from scripts.harness.gui.server import app


class TestGUIFrontendLayout(unittest.TestCase):
    """
    Test suite for Phase 2: Antigravity 2.0 GUI Frontend Layout.
    Covers AC-Sec-1 and AC-1 through AC-5.
    """

    def setUp(self):
        self.client = TestClient(app)
        self.static_dir = os.path.join(REPO_ROOT, "scripts", "harness", "gui", "static")

    def test_AC_Sec_1_xss_sanitization(self):
        """
        AC-Sec-1: Frontend JavaScript must sanitize dynamic user/LLM content against XSS.
        """
        app_js_path = os.path.join(self.static_dir, "app.js")
        if not os.path.exists(app_js_path):
            self.skipTest("scripts/harness/gui/static/app.js not yet implemented.")
        
        with open(app_js_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertTrue(
            "escapeHtml" in content or "sanitize" in content,
            "Security vulnerability: app.js lacks HTML escape/sanitization utility for dynamic content"
        )

    def test_AC_1_static_asset_serving(self):
        """
        AC-1: Server serves index.html at root '/' and mounts '/static' assets.
        """
        res_root = self.client.get("/")
        self.assertEqual(res_root.status_code, 200, "Root '/' must return HTTP 200")
        self.assertIn("text/html", res_root.headers.get("content-type", ""))

        res_js = self.client.get("/static/app.js")
        self.assertEqual(res_js.status_code, 200, "/static/app.js must be accessible")

        res_css = self.client.get("/static/style.css")
        self.assertEqual(res_css.status_code, 200, "/static/style.css must be accessible")

    def test_AC_2_antigravity_3_column_layout(self):
        """
        AC-2: index.html implements the exact 3-column layout of Antigravity 2.0.
        """
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.text

        # Verify 3 distinct layout columns
        self.assertIn('id="sidebar-left"', html, "Missing #sidebar-left column")
        self.assertIn('id="chat-canvas"', html, "Missing #chat-canvas central column")
        self.assertIn('id="auxiliary-pane"', html, "Missing #auxiliary-pane right column")

        # Verify controls in sidebar
        self.assertIn('id="provider-select"', html, "Missing provider selector")
        self.assertIn('id="model-select"', html, "Missing model selector")
        self.assertIn('id="skills-list"', html, "Missing active skills list")
        self.assertIn("k-method app", html, "index.html brand title must be 'k-method app'")

    def test_AC_3_websocket_client_contract(self):
        """
        AC-3: app.js contains logic to handle all SDLC streaming events over WebSocket.
        """
        app_js_path = os.path.join(self.static_dir, "app.js")
        if not os.path.exists(app_js_path):
            self.skipTest("app.js not yet implemented.")

        with open(app_js_path, "r", encoding="utf-8") as f:
            js = f.read()

        expected_events = ["stage_changed", "token", "approval_required", "tdd_output", "completed"]
        for ev in expected_events:
            self.assertIn(ev, js, f"app.js missing handler for event '{ev}'")

    def test_AC_4_human_approval_action_bar(self):
        """
        AC-4: DOM contains interactive approval action bar with approve and revise actions.
        """
        res = self.client.get("/")
        html = res.text

        self.assertIn('id="approval-bar"', html, "Missing #approval-bar container")
        self.assertIn('id="btn-approve"', html, "Missing #btn-approve button")
        self.assertIn('id="btn-revise"', html, "Missing #btn-revise button")

    def test_AC_5_auxiliary_tabs_switching(self):
        """
        AC-5: Auxiliary pane declares all 4 Antigravity 2.0 tabs.
        """
        res = self.client.get("/")
        html = res.text

        self.assertIn('data-tab="artifacts"', html, "Missing artifacts tab")
        self.assertIn('data-tab="diff"', html, "Missing diff tab")
        self.assertIn('data-tab="tdd"', html, "Missing tdd tab")
        self.assertIn('data-tab="okf"', html, "Missing okf graph tab")

    def test_AC_6_dynamic_model_filtering_contract(self):
        """
        AC-6: app.js defines updateModelOptions and hooks provider-select change event to update model-select.
        """
        app_js_path = os.path.join(self.static_dir, "app.js")
        with open(app_js_path, "r", encoding="utf-8") as f:
            js = f.read()

        self.assertIn("updateModelOptions", js, "app.js must define updateModelOptions")
        self.assertIn("provider-select", js, "app.js must bind to provider-select")
        self.assertIn("model-select", js, "app.js must update model-select options")

    def test_AC_7_custom_model_and_refresh_controls(self):
        """
        AC-7: DOM contains #btn-refresh-models and #custom-model-input for uncured SDK discovery.
        """
        res = self.client.get("/")
        html = res.text
        self.assertIn('id="btn-refresh-models"', html, "Missing #btn-refresh-models button")
        self.assertIn('id="custom-model-input"', html, "Missing #custom-model-input text input")


if __name__ == "__main__":
    unittest.main()
