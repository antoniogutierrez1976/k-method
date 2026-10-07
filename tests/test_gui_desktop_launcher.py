import os
import socket
import sys
import unittest
from unittest.mock import patch, MagicMock

# Ensure repo root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    from scripts.harness.gui.launch import (
        find_available_port,
        parse_launcher_args,
        verify_server_health,
    )
except ImportError:
    find_available_port = None
    parse_launcher_args = None
    verify_server_health = None


class TestGUIDesktopLauncher(unittest.TestCase):
    """
    Test suite for Phase 3: Windows Desktop Launcher & PowerShell Integration.
    Covers AC-Sec-1 and AC-1 through AC-5.
    """

    def setUp(self):
        if parse_launcher_args is None:
            self.skipTest("scripts/harness/gui/launch.py not yet implemented.")

    def test_AC_Sec_1_localhost_binding_default(self):
        """
        AC-Sec-1: Default host must be 127.0.0.1 to avoid exposing the SDLC server to the network.
        """
        args = parse_launcher_args([])
        self.assertEqual(args.host, "127.0.0.1", "Security violation: default host must be 127.0.0.1 (localhost)")

    def test_AC_1_port_auto_resolution(self):
        """
        AC-1: Launcher skips occupied ports and finds the next available TCP port.
        """
        # Occupy a temporary port with a dummy socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 0))
        occupied_port = sock.getsockname()[1]
        
        try:
            free_port = find_available_port(occupied_port)
            self.assertNotEqual(free_port, occupied_port)
            self.assertGreater(free_port, occupied_port)
        finally:
            sock.close()

    def test_AC_2_launch_cli_args(self):
        """
        AC-2: launch.py CLI parser parses port, host, and no-browser flags.
        """
        args = parse_launcher_args(["--port", "9050", "--host", "127.0.0.1", "--no-browser"])
        self.assertEqual(args.port, 9050)
        self.assertEqual(args.host, "127.0.0.1")
        self.assertTrue(args.no_browser)

    def test_AC_3_powershell_launcher_contract(self):
        """
        AC-3: run-gui.ps1 exists in root and contains UTF-8 enforcement and parameter declarations.
        """
        ps1_path = os.path.join(REPO_ROOT, "run-gui.ps1")
        self.assertTrue(os.path.exists(ps1_path), "run-gui.ps1 must exist in repository root")

        with open(ps1_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("OutputEncoding = [System.Text.Encoding]::UTF8", content)
        self.assertIn("$Port", content)
        self.assertIn("$NoBrowser", content)
        self.assertIn("scripts\\harness\\gui\\launch.py", content)

    def test_AC_4_healthcheck_verification(self):
        """
        AC-4: verify_server_health checks /api/status response.
        """
        # Mocking an unreachable port
        unreachable_port = 59999
        is_healthy = verify_server_health("127.0.0.1", unreachable_port, timeout=0.1)
        self.assertFalse(is_healthy)

    def test_AC_5_documentation_updated(self):
        """
        AC-5: README.md documents run-gui.ps1 usage.
        """
        readme_path = os.path.join(REPO_ROOT, "README.md")
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("run-gui.ps1", content, "README.md must document the GUI runner launcher")
        self.assertIn("k-method app", content, "README.md must reference k-method app")

    def test_AC_6_packaging_spec_and_build_script(self):
        """
        AC-6: PyInstaller spec and build-exe.ps1 exist and declare valid bundling directives.
        """
        spec_path = os.path.join(REPO_ROOT, "packaging", "k-method-studio.spec")
        self.assertTrue(os.path.exists(spec_path), "packaging/k-method-studio.spec must exist")

        with open(spec_path, "r", encoding="utf-8") as f:
            spec_content = f.read()
        self.assertIn("k-method-studio", spec_content)
        self.assertIn('"static"', spec_content)

        build_script = os.path.join(REPO_ROOT, "scripts", "build", "build-exe.ps1")
        self.assertTrue(os.path.exists(build_script), "scripts/build/build-exe.ps1 must exist")

        with open(build_script, "r", encoding="utf-8") as f:
            script_content = f.read()
        self.assertIn("pyinstaller", script_content.lower())
        self.assertIn("dist/k-method-studio.exe", script_content)


if __name__ == "__main__":
    unittest.main()
