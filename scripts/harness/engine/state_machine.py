import re
import subprocess
import sys
from enum import Enum
from typing import Optional, Callable, List, Tuple
from dataclasses import dataclass

from scripts.harness.providers.base import BaseAgentProvider, AgentResponse
from scripts.harness.engine.embedded_skills import get_embedded_directive


class SDLCStage(Enum):
    INIT = "init"
    SPEC = "spec"
    ENVIRONMENT = "environment"
    VERIFIER_RED = "verifier_red"
    VERIFIER_GREEN = "verifier_green"
    CIRCUIT_BREAKER_TRIPPED = "circuit_breaker_tripped"
    RELEASE_OKF = "release_okf"
    COMPLETED = "completed"
    ABORTED = "aborted"


class EngineError(Exception):
    """Base exception for SDLC engine failures and invariant violations."""
    pass


class StashShield:
    """
    Guards workspace isolation and verifies clean Git working tree state.
    """

    BRANCH_REGEX = re.compile(r"^[a-zA-Z0-9_\-\/]+$")

    def sanitize_branch_name(self, branch_name: str) -> str:
        """
        Validates branch names to strictly forbid command injection.
        """
        cleaned = branch_name.strip()
        if not cleaned or not self.BRANCH_REGEX.match(cleaned):
            raise ValueError(
                f"Invalid branch name: '{branch_name}'. Only alphanumeric, underscores, hyphens, and slashes allowed."
            )
        return cleaned

    def is_clean(self, cwd: Optional[str] = None) -> bool:
        """
        Returns True if `git status --porcelain` is empty.
        """
        res = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
        )
        stdout = res.stdout or ""
        return len(stdout.strip()) == 0

    def checkout_branch(self, branch_name: str, cwd: Optional[str] = None, create: bool = True) -> int:
        safe_branch = self.sanitize_branch_name(branch_name)
        cmd = ["git", "checkout", "-b" if create else "", safe_branch]
        cmd = [arg for arg in cmd if arg]
        res = subprocess.run(cmd, cwd=cwd, shell=False)
        return res.returncode


class CircuitBreaker:
    """
    Prevents infinite speculative edit loops by tripping after N consecutive identical errors.
    """

    def __init__(self, threshold: int = 2):
        self.threshold = threshold
        self.failure_count = 0
        self.last_signature: Optional[str] = None
        self.is_tripped = False

    def record_failure(self, error_signature: str) -> bool:
        normalized_sig = error_signature.strip()
        if self.last_signature == normalized_sig:
            self.failure_count += 1
        else:
            self.last_signature = normalized_sig
            self.failure_count = 1

        if self.failure_count >= self.threshold:
            self.is_tripped = True
            return True
        return False

    def reset(self):
        self.failure_count = 0
        self.last_signature = None
        self.is_tripped = False

    def generate_friction_report(self, git_diff: str = "") -> str:
        return (
            "═══════════════════════════════════════════════════════════════════\n"
            "🛑 DEADLOCK CIRCUIT BREAKER TRIPPED\n"
            "═══════════════════════════════════════════════════════════════════\n"
            f"Firma del Error (x{self.failure_count} consecutivos):\n{self.last_signature}\n\n"
            "Diff actual inspeccionado:\n"
            f"{git_diff or '(sin cambios en working tree)'}\n\n"
            "Acción Requerida:\n"
            "1. Detener ediciones especulativas.\n"
            "2. Escalar a operador humano o modelo superior (ej. GPT-6.1 Sol / Astra).\n"
            "═══════════════════════════════════════════════════════════════════\n"
        )


class KMethodEngine:
    """
    Deterministic Karpathy SDLC Orchestrator Engine.
    """

    AC_REGEX = re.compile(r"(\bAC-(?:Sec-)?\d+\b)")

    def __init__(
        self,
        provider: BaseAgentProvider,
        test_runner: Optional[Callable[[], Tuple[int, str]]] = None,
        approval_callback: Optional[Callable[[str], bool]] = None,
    ):
        self.provider = provider
        self.test_runner = test_runner or self._default_test_runner
        self.approval_callback = approval_callback
        self.circuit_breaker = CircuitBreaker(threshold=2)
        self.stash_shield = StashShield()
        self.current_stage = SDLCStage.INIT

    def _default_test_runner(self) -> Tuple[int, str]:
        res = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
        )
        stdout = res.stdout or ""
        stderr = res.stderr or ""
        output = stdout + "\n" + stderr
        return res.returncode, output

    async def execute_spec_stage(self, task_prompt: str) -> str:
        self.current_stage = SDLCStage.SPEC
        system_prompt = get_embedded_directive("k-spec")
        response: AgentResponse = await self.provider.chat_atomic(
            prompt=task_prompt, system_prompt=system_prompt
        )
        content = response.content

        # Count unique AC matches
        matches = set(self.AC_REGEX.findall(content))
        if len(matches) > 6:
            raise EngineError(
                f"Specification exceeds the 6-AC hard limit ({len(matches)} ACs found: {sorted(matches)}). "
                "Decompose into an epic."
            )

        if self.approval_callback:
            approved = self.approval_callback(content)
            if not approved:
                self.current_stage = SDLCStage.ABORTED
                raise EngineError("Specification rejected by operator.")

        return content

    async def execute_tdd_cycle(self, ac_id: str, ac_desc: str) -> bool:
        self.current_stage = SDLCStage.VERIFIER_RED
        # 1. Ask provider for failing test (Red phase)
        red_prompt = f"Write an automated test for criterion {ac_id}: {ac_desc}. Do not implement domain logic yet."
        verifier_directive = get_embedded_directive("k-verifier")
        await self.provider.chat_atomic(prompt=red_prompt, system_prompt=verifier_directive)

        exit_code, output = self.test_runner()
        if exit_code == 0:
            raise EngineError(
                f"Vacuous test detected for {ac_id}: test suite passed without implementing code."
            )

        # 2. Ask provider for Green implementation
        self.current_stage = SDLCStage.VERIFIER_GREEN
        green_prompt = (
            f"The test for {ac_id} failed with exit code {exit_code}:\n{output}\n"
            "Write the minimal domain implementation to make this test pass."
        )
        await self.provider.chat_atomic(prompt=green_prompt, system_prompt="Act as minimal implementer (Green phase).")

        exit_code_green, output_green = self.test_runner()
        if exit_code_green != 0:
            tripped = self.circuit_breaker.record_failure(output_green)
            if tripped:
                self.current_stage = SDLCStage.CIRCUIT_BREAKER_TRIPPED
                raise EngineError("Deadlock circuit breaker tripped after 2 consecutive identical failures.")
            return False

        self.circuit_breaker.reset()
        return True

    async def finalize_release(self, feature_name: str) -> str:
        self.current_stage = SDLCStage.RELEASE_OKF
        # 1. Assert OKF graph integrity
        linter_script = ".agents/skills/k-wiki/scripts/okf-lint.py"
        res = subprocess.run(
            [sys.executable, linter_script],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
        )
        if res.returncode != 0:
            stderr = res.stderr or ""
            raise EngineError(f"OKF knowledge graph verification failed: {stderr}")

        # 2. Draft PR description
        pr_prompt = f"Draft a Pull Request description for completed feature '{feature_name}' using pull-request.template.md."
        pr_response = await self.provider.chat_atomic(prompt=pr_prompt, system_prompt="Act as release generator.")
        
        self.current_stage = SDLCStage.COMPLETED
        return pr_response.content
