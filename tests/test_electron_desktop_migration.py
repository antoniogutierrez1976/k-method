"""
Unit Tests for Phase 4: Electron Desktop Migration & Framework Modernization (04-electron-desktop-migration)
Verifies Acceptance Criteria AC-Sec-1 through AC-5 from specs/k-windows-gui/04-electron-desktop-migration/spec.md
"""
import json
import os
import unittest
from fastapi.testclient import TestClient

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DESKTOP_DIR = os.path.join(REPO_ROOT, "desktop")


class TestElectronDesktopMigration(unittest.TestCase):
    """
    Verifier test suite ensuring the Electron desktop studio meets all structural,
    security, and functional contracts defined in the migration specification.
    """

    def test_AC_Sec_1_context_isolation_and_security(self):
        """
        AC-Sec-1: BrowserWindow must declare nodeIntegration: false, contextIsolation: true,
        and webSecurity: true to prevent renderer RCE exploits.
        """
        main_ts_path = os.path.join(DESKTOP_DIR, "electron", "main.ts")
        self.assertTrue(os.path.exists(main_ts_path), "desktop/electron/main.ts must exist")
        with open(main_ts_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("nodeIntegration: false", content, "Must disable nodeIntegration in BrowserWindow")
        self.assertIn("contextIsolation: true", content, "Must enable contextIsolation in BrowserWindow")
        self.assertIn("webSecurity: true", content, "Must enable webSecurity in BrowserWindow")

    def test_AC_1_desktop_directory_layout(self):
        """
        AC-1: Desktop directory layout declares valid React, TypeScript, and Vite configurations
        without any obsolete v17 references.
        """
        required_files = [
            os.path.join(DESKTOP_DIR, "package.json"),
            os.path.join(DESKTOP_DIR, "vite.config.ts"),
            os.path.join(DESKTOP_DIR, "tsconfig.json"),
            os.path.join(DESKTOP_DIR, "index.html"),
            os.path.join(DESKTOP_DIR, "src", "App.tsx"),
        ]
        for path in required_files:
            self.assertTrue(os.path.exists(path), f"Required file missing: {path}")

        pkg_path = os.path.join(DESKTOP_DIR, "package.json")
        with open(pkg_path, "r", encoding="utf-8") as f:
            pkg = json.load(f)

        self.assertEqual(pkg.get("name"), "k-method-app")
        pkg_str = json.dumps(pkg)
        self.assertNotIn("v17", pkg_str, "Obsolete version v17 must not appear in desktop package.json")

    def test_AC_2_electron_main_and_sidecar(self):
        """
        AC-2: Electron main process manages window lifecycle and Python sidecar supervisor.
        """
        main_ts_path = os.path.join(DESKTOP_DIR, "electron", "main.ts")
        with open(main_ts_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("checkBackendHealth", content, "Must provide backend health check")
        self.assertIn("ensureBackendRunning", content, "Must provide sidecar supervision logic")
        self.assertIn("launch.py", content, "Must point to Python launch.py sidecar")
        self.assertIn("window-all-closed", content, "Must handle clean process shutdown on close")

    def test_AC_3_component_hierarchy(self):
        """
        AC-3: 3-column layout components implemented and linked to real backend API endpoints.
        """
        components_dir = os.path.join(DESKTOP_DIR, "src", "components")
        required_components = [
            "Header.tsx",
            "Sidebar.tsx",
            "ChatCanvas.tsx",
            "AuxiliaryPane.tsx",
            "StepCard.tsx",
            "ApprovalModal.tsx",
            "SkillModal.tsx",
        ]
        for comp in required_components:
            p = os.path.join(components_dir, comp)
            self.assertTrue(os.path.exists(p), f"Component missing: {comp}")

    def test_AC_4_cors_middleware_enabled(self):
        """
        AC-4: ASGI backend provides permissive CORS for local desktop and browser clients.
        """
        from scripts.harness.gui.server import create_app
        app = create_app()
        client = TestClient(app)

        # Preflight OPTIONS request
        response = client.options(
            "/api/status",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Access-Control-Request-Method": "GET",
            }
        )
        self.assertIn(response.status_code, (200, 204))
        self.assertIn(response.headers.get("access-control-allow-origin"), ("*", "http://127.0.0.1:5173"))

    def test_AC_5_launcher_script_exists(self):
        """
        AC-5: Windows launcher run-desktop.ps1 supports development and production execution modes.
        """
        launcher_path = os.path.join(REPO_ROOT, "run-desktop.ps1")
        self.assertTrue(os.path.exists(launcher_path), "run-desktop.ps1 launcher must exist")
        with open(launcher_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("[switch]$Dev", content, "Must declare -Dev switch for development mode")
        self.assertIn("pnpm run dev", content, "Must support pnpm run dev in development")
        self.assertIn("k-method app.exe", content, "Must target packaged executable in release mode")


if __name__ == "__main__":
    unittest.main()
