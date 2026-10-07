import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add repository root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.harness.providers.mock_provider import MockProvider
from scripts.harness.engine.state_machine import (
    SDLCStage,
    CircuitBreaker,
    StashShield,
    KMethodEngine,
    EngineError,
)


class TestSDLCOrchestrationEngine(unittest.IsolatedAsyncioTestCase):
    """
    Test suite enforcing Layer 2 (Verifier) for Phase 2: SDLC Engine & Circuit Breaker.
    Covers AC-Sec-1 and AC-1 through AC-5.
    """

    def test_AC_Sec_1_no_shell_injection(self):
        """
        AC-Sec-1: Subprocess execution must reject malicious shell metacharacters in branch names.
        """
        shield = StashShield()
        malicious_branch = "feat/test; rm -rf /; echo evil"
        with self.assertRaises(ValueError) as ctx:
            shield.sanitize_branch_name(malicious_branch)
        self.assertIn("Invalid branch name", str(ctx.exception))

    async def test_AC_1_spec_gate_and_ac_limit(self):
        """
        AC-1: Engine rejects specs with > 6 ACs and pauses for human approval.
        """
        # Spec with 7 ACs (exceeding limit of 6)
        invalid_spec = "\n".join([f"- [ ] **AC-{i}**: Criterion {i}" for i in range(1, 8)])
        provider = MockProvider(mock_responses=[invalid_spec])
        
        engine = KMethodEngine(provider=provider)
        with self.assertRaises(EngineError) as ctx:
            await engine.execute_spec_stage("Implement feature")
        self.assertIn("exceeds the 6-AC hard limit", str(ctx.exception))

        # Valid spec with 3 ACs
        valid_spec = "\n".join([f"- [ ] **AC-{i}**: Criterion {i}" for i in range(1, 4)])
        provider_valid = MockProvider(mock_responses=[valid_spec])
        
        approval_mock = MagicMock(return_value=True)
        engine_valid = KMethodEngine(provider=provider_valid, approval_callback=approval_mock)
        spec_result = await engine_valid.execute_spec_stage("Implement feature")
        
        self.assertEqual(spec_result, valid_spec)
        approval_mock.assert_called_once()

    def test_AC_2_stash_shield(self):
        """
        AC-2: StashShield asserts working tree clean state.
        """
        shield = StashShield()
        with patch("subprocess.run") as mock_run:
            # Dirty state
            mock_run.return_value = MagicMock(stdout=" M dirty_file.py\n", returncode=0)
            self.assertFalse(shield.is_clean())

            # Clean state
            mock_run.return_value = MagicMock(stdout="", returncode=0)
            self.assertTrue(shield.is_clean())

    async def test_AC_3_tdd_cycle(self):
        """
        AC-3: TDD cycle enforces Red phase failure before Green implementation.
        """
        # Provider returns test code first, then green implementation
        provider = MockProvider(mock_responses=["// Failing test code", "// Green implementation code"])
        
        runner_mock = MagicMock()
        # First run (Red phase) -> returns exit code 1 (failing)
        # Second run (Green phase) -> returns exit code 0 (passing)
        runner_mock.side_effect = [(1, "AssertionError: expected true but got false"), (0, "All tests passed")]
        
        engine = KMethodEngine(provider=provider, test_runner=runner_mock)
        success = await engine.execute_tdd_cycle(ac_id="AC-1", ac_desc="Should validate input")
        
        self.assertTrue(success)
        self.assertEqual(runner_mock.call_count, 2)

    def test_AC_4_circuit_breaker(self):
        """
        AC-4: CircuitBreaker trips after 2 consecutive identical failure signatures.
        """
        cb = CircuitBreaker(threshold=2)
        
        sig1 = "TypeError: cannot read property 'foo' of undefined at line 42"
        tripped1 = cb.record_failure(sig1)
        self.assertFalse(tripped1, "Circuit breaker should not trip on first failure")
        self.assertEqual(cb.failure_count, 1)
        
        # Second identical failure -> Must trip
        tripped2 = cb.record_failure(sig1)
        self.assertTrue(tripped2, "Circuit breaker MUST trip on 2nd consecutive identical failure")
        self.assertTrue(cb.is_tripped)
        
        # Generates friction report
        report = cb.generate_friction_report(git_diff="--- a/file.ts\n+++ b/file.ts\n@@ -1 +1 @@\n-old\n+new")
        self.assertIn("DEADLOCK CIRCUIT BREAKER TRIPPED", report)
        self.assertIn("Firma del Error", report)

    async def test_AC_5_okf_and_pr_generation(self):
        """
        AC-5: Engine validates OKF graph and generates PR markdown.
        """
        provider = MockProvider(mock_responses=["# Generated PR Description"])
        
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="Graph valid")
            engine = KMethodEngine(provider=provider)
            pr_desc = await engine.finalize_release(feature_name="harness-engine")
            
            self.assertEqual(pr_desc, "# Generated PR Description")

    async def test_spec_rejected_by_operator(self):
        """
        Engine aborts if approval callback returns False.
        """
        valid_spec = "- [ ] **AC-1**: First criterion"
        provider = MockProvider(mock_responses=[valid_spec])
        engine = KMethodEngine(provider=provider, approval_callback=lambda spec: False)
        
        with self.assertRaises(EngineError) as ctx:
            await engine.execute_spec_stage("Task")
        self.assertIn("rejected by operator", str(ctx.exception))
        self.assertEqual(engine.current_stage, SDLCStage.ABORTED)

    async def test_vacuous_test_detection(self):
        """
        Engine raises error if test passes during Red phase without code.
        """
        provider = MockProvider(mock_responses=["// Test"])
        # Test runner returns exit code 0 during Red phase
        runner_mock = MagicMock(return_value=(0, "Passes without implementation"))
        engine = KMethodEngine(provider=provider, test_runner=runner_mock)

        with self.assertRaises(EngineError) as ctx:
            await engine.execute_tdd_cycle("AC-1", "Description")
        self.assertIn("Vacuous test detected", str(ctx.exception))

    async def test_circuit_breaker_trips_in_tdd_loop(self):
        """
        Engine trips circuit breaker after 2 consecutive identical failures during Green phase.
        """
        provider = MockProvider(mock_responses=["// Test", "// Fix 1", "// Fix 2"])
        err_msg = "AssertionError: expected 5 got 0"
        # Cycle 1: Red check (fails), Green check (fails with err_msg)
        # Cycle 2: Red check (fails), Green check (fails with identical err_msg -> trips!)
        runner_mock = MagicMock(side_effect=[
            (1, "Red fail 1"),
            (1, err_msg),
            (1, "Red fail 2"),
            (1, err_msg),
        ])
        engine = KMethodEngine(provider=provider, test_runner=runner_mock)

        # First Green attempt
        success1 = await engine.execute_tdd_cycle("AC-1", "Desc")
        self.assertFalse(success1)
        self.assertEqual(engine.circuit_breaker.failure_count, 1)

        # Second Green attempt with identical error -> trips!
        with self.assertRaises(EngineError) as ctx:
            await engine.execute_tdd_cycle("AC-1", "Desc")
        self.assertIn("circuit breaker tripped", str(ctx.exception))
        self.assertEqual(engine.current_stage, SDLCStage.CIRCUIT_BREAKER_TRIPPED)

    def test_stash_shield_checkout_branch(self):
        """
        StashShield sanitizes and checkouts safe branch.
        """
        shield = StashShield()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            code = shield.checkout_branch("feat/my-task", create=True)
            self.assertEqual(code, 0)
            mock_run.assert_called_once_with(["git", "checkout", "-b", "feat/my-task"], cwd=None, shell=False)

    async def test_finalize_release_okf_failure(self):
        """
        finalize_release raises EngineError if okf linter fails.
        """
        provider = MockProvider()
        engine = KMethodEngine(provider=provider)
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr="Broken link")
            with self.assertRaises(EngineError) as ctx:
                await engine.finalize_release("feat")
            self.assertIn("OKF knowledge graph verification failed", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
