import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add repository root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.harness.ui.renderer import (
    sanitize_terminal_output,
    render_banner,
    render_auxiliary_panel,
    render_friction_alert,
    prompt_human_approval,
)
from scripts.harness.k_runner import parse_args, run_pipeline_cli


class TestAppRunner(unittest.IsolatedAsyncioTestCase):
    """
    Test suite enforcing Layer 2 (Verifier) for Phase 3: Windows Antigravity-Style App Runner.
    Covers AC-Sec-1 and AC-1 through AC-5.
    """

    def tearDown(self):
        import shutil
        for d in ["build-adapter", "failing-task", "build-ui", "test-task"]:
            p = os.path.join("specs", d)
            if os.path.exists(p):
                shutil.rmtree(p, ignore_errors=True)

    def test_AC_Sec_1_terminal_escape_sanitization(self):
        """
        AC-Sec-1: Renderer must sanitize dangerous control characters / OSC escape sequences.
        """
        raw_text = "Hello\x1b]0;Evil Window Title\x07World\x1b[2JSafe Content"
        sanitized = sanitize_terminal_output(raw_text)
        
        self.assertNotIn("\x1b]0;", sanitized, "Dangerous OSC escape sequence was not stripped")
        self.assertIn("Hello", sanitized)
        self.assertIn("World", sanitized)
        self.assertIn("Safe Content", sanitized)

    def test_AC_1_cli_arg_resolution(self):
        """
        AC-1: CLI parser resolves flags with fallback to environment variables.
        """
        # Test explicit CLI arguments
        args = ["--provider", "copilot", "--model", "gpt-6-luna", "--task", "Build UI", "--auto-approve"]
        config = parse_args(args)
        
        self.assertEqual(config.provider, "copilot")
        self.assertEqual(config.model, "gpt-6-luna")
        self.assertEqual(config.task, "Build UI")
        self.assertTrue(config.auto_approve)

        # Test fallback to env vars
        with patch.dict(os.environ, {"K_HARNESS_PROVIDER": "antigravity", "K_HARNESS_MODEL": "gemini-3.8-flash"}):
            config_env = parse_args(["--task", "Test Task"])
            self.assertEqual(config_env.provider, "antigravity")
            self.assertEqual(config_env.model, "gemini-3.8-flash")

    def test_AC_2_antigravity_banner_and_panels(self):
        """
        AC-2: Renderer formats stylized Antigravity-like header banner and auxiliary panel.
        """
        banner = render_banner(provider="copilot", model="gpt-6-luna", stage="SPEC")
        self.assertIn("ANTIGRAVITY", banner)
        self.assertIn("copilot", banner)
        self.assertIn("gpt-6-luna", banner)

        panel = render_auxiliary_panel(stage="VERIFIER_TDD", branch="feat/windows-runner", tokens=1250)
        self.assertIn("VERIFIER_TDD", panel)
        self.assertIn("feat/windows-runner", panel)
        self.assertIn("1250", panel)

    def test_AC_3_human_approval_prompt(self):
        """
        AC-3: prompt_human_approval handles affirmative, negative, and auto_approve cases.
        """
        spec = "# Sample Spec\n- [ ] **AC-1**: Test"
        
        # Auto-approve returns True immediately without user input
        self.assertTrue(prompt_human_approval(spec, auto_approve=True))

        # Mock interactive inputs: 's' -> True, 'n' -> False
        with patch("builtins.input", return_value="s"):
            self.assertTrue(prompt_human_approval(spec, auto_approve=False))

        with patch("builtins.input", return_value="n"):
            self.assertFalse(prompt_human_approval(spec, auto_approve=False))

    def test_AC_4_circuit_breaker_alert_rendering(self):
        """
        AC-4: Friction report is rendered in a clear alert box.
        """
        report = "DEADLOCK CIRCUIT BREAKER TRIPPED\nFirma del Error: Assertion failed at line 10"
        rendered = render_friction_alert(report)
        
        self.assertIn("DISYUNTOR ACTIVADO", rendered)
        self.assertIn("Assertion failed at line 10", rendered)

    async def test_AC_5_end_to_end_runner_execution(self):
        """
        AC-5: Full end-to-end execution of k_runner with mock provider returns code 0.
        """
        config = parse_args(["--provider", "mock", "--task", "Build adapter", "--auto-approve"])
        
        # Mock test runner and subcommands
        runner_mock = MagicMock(side_effect=[(1, "Red fail"), (0, "Green pass")])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="Clean")
            exit_code = await run_pipeline_cli(config, test_runner=runner_mock)
            self.assertEqual(exit_code, 0)

    def test_slugify_task(self):
        """
        slugify_task handles punctuation, spaces, and empty strings.
        """
        from scripts.harness.k_runner import slugify_task
        self.assertEqual(slugify_task("Add metrics & telemetry!"), "add-metrics-telemetry")
        self.assertEqual(slugify_task(""), "task")

    async def test_runner_empty_task_cancellation(self):
        """
        Runner returns code 1 if user cancels task input.
        """
        config = parse_args(["--provider", "mock", "--task", ""])
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            code = await run_pipeline_cli(config)
            self.assertEqual(code, 1)

    async def test_runner_invalid_provider_failure(self):
        """
        Runner returns code 1 if provider cannot be instantiated.
        """
        config = parse_args(["--provider", "mock", "--task", "Task"])
        with patch("scripts.harness.providers.factory.ProviderFactory.create", side_effect=ValueError("Bad provider")):
            code = await run_pipeline_cli(config)
            self.assertEqual(code, 1)

    async def test_runner_circuit_breaker_alert_output(self):
        """
        Runner displays friction alert if circuit breaker trips.
        """
        config = parse_args(["--provider", "mock", "--task", "Failing task", "--auto-approve"])
        
        # Test runner fails with identical error consecutively
        err = "AssertionError: expected 1 got 2"
        runner_mock = MagicMock(side_effect=[(1, "Red fail 1"), (1, err), (1, "Red fail 2"), (1, err)])
        
        code = await run_pipeline_cli(config, test_runner=runner_mock)
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
