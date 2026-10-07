import os
import sys
import unittest
import subprocess

SCRIPTS_DIR = "scripts"
RUNNER_PATH = os.path.join(SCRIPTS_DIR, "verify-all.py")

class TestVerifyAllRunner(unittest.TestCase):
    """Verifies AC-1: Universal quality gates runner script."""

    def test_AC_1_runner_file_exists(self):
        """scripts/verify-all.py must exist."""
        self.assertTrue(os.path.exists(RUNNER_PATH), f"Runner script {RUNNER_PATH} does not exist")

    def test_AC_1_runner_executes_successfully(self):
        """scripts/verify-all.py must exit with code 0 when repository is clean and valid."""
        if os.environ.get("K_METHOD_RUNNER_ACTIVE") == "1":
            self.skipTest("Preventing recursive execution when already under scripts/verify-all.py")

        child_env = os.environ.copy()
        child_env["K_METHOD_RUNNER_ACTIVE"] = "1"
        res = subprocess.run(
            [sys.executable, RUNNER_PATH, "--skip-git-diff"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=child_env,
            timeout=30
        )
        self.assertEqual(res.returncode, 0, f"Runner failed with exit code {res.returncode}:\n{res.stdout}\n{res.stderr}")
        self.assertIn("RESUMEN DE VERIFICACIÓN", res.stdout)
        self.assertIn("TODO CORRECTO", res.stdout)

    def test_AC_1_runner_fails_on_broken_check(self):
        """Runner must return code 1 if a subprocess gate fails."""
        import importlib.util
        if not os.path.exists(RUNNER_PATH):
            self.fail(f"{RUNNER_PATH} does not exist")

        spec = importlib.util.spec_from_file_location("verify_all", RUNNER_PATH)
        verify_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verify_mod)

        # Execute gate with invalid command
        code = verify_mod.run_command(["python", "-c", "import sys; sys.exit(1)"], "Simulated Failure")
        self.assertEqual(code, 1)

if __name__ == "__main__":
    unittest.main()
