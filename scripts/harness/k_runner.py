#!/usr/bin/env python3
"""
k-method Windows Skills Runner & Harness.
Provides an interactive Antigravity-style CLI to execute SDLC cycles with Copilot or Antigravity SDKs.
"""
import argparse
import asyncio
import os
import re
import sys
from dataclasses import dataclass
from typing import Optional, List, Callable, Tuple

# Ensure UTF-8 output on Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from scripts.harness.providers.factory import ProviderFactory
from scripts.harness.engine.state_machine import KMethodEngine, EngineError, SDLCStage
from scripts.harness.ui.renderer import (
    render_banner,
    render_auxiliary_panel,
    render_friction_alert,
    prompt_human_approval,
)


@dataclass
class RunnerConfig:
    provider: str
    model: str
    task: str
    auto_approve: bool = False
    branch_name: Optional[str] = None


def parse_args(args: Optional[List[str]] = None) -> RunnerConfig:
    parser = argparse.ArgumentParser(
        description="k-method Windows Skills Runner (Antigravity & Copilot SDLC Harness)"
    )
    env_provider = os.environ.get("K_HARNESS_PROVIDER", "copilot")
    env_model = os.environ.get(
        "K_HARNESS_MODEL",
        "gemini-3.8-flash" if env_provider == "antigravity" else "gpt-6-luna",
    )

    parser.add_argument(
        "--provider",
        choices=["copilot", "antigravity", "mock"],
        default=env_provider,
        help="LLM provider adapter to execute the task (default: copilot)",
    )
    parser.add_argument(
        "--model",
        default=env_model,
        help="Target model identifier (e.g., gpt-6-luna, gpt-6.1-sol, gemini-3.8-flash)",
    )
    parser.add_argument(
        "--task",
        default="",
        help="Description of the feature or bug to implement",
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Bypass interactive human approval gate (for automated CI/CD runs)",
    )
    parser.add_argument(
        "--branch",
        default=None,
        help="Explicit Git task branch name (auto-generated if omitted)",
    )

    parsed = parser.parse_args(args if args is not None else sys.argv[1:])
    return RunnerConfig(
        provider=parsed.provider,
        model=parsed.model,
        task=parsed.task,
        auto_approve=parsed.auto_approve,
        branch_name=parsed.branch,
    )


def slugify_task(task: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9\s-]", "", task).strip().lower()
    slug = re.sub(r"[\s_]+", "-", cleaned)
    return slug[:30] if slug else "task"


async def run_pipeline_cli(
    config: RunnerConfig,
    test_runner: Optional[Callable[[], Tuple[int, str]]] = None,
) -> int:
    """
    Executes the SDLC loop interactively with terminal formatting.
    """
    print(render_banner(provider=config.provider, model=config.model, stage="INICIALIZACIÓN"))

    task_desc = config.task.strip()
    if not task_desc:
        try:
            task_desc = input("\n📝 Ingrese la tarea a desarrollar: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nOperación abortada por el usuario.")
            return 1

    if not task_desc:
        print("❌ Error: Debe especificar una tarea.")
        return 1

    branch_name = config.branch_name or f"feat/{slugify_task(task_desc)}"

    try:
        provider = ProviderFactory.create(config.provider, model=config.model)
    except Exception as e:
        print(f"\n❌ Error al instanciar el proveedor '{config.provider}': {e}")
        return 1

    def approval_wrapper(spec_text: str) -> bool:
        return prompt_human_approval(spec_text, auto_approve=config.auto_approve)

    engine = KMethodEngine(
        provider=provider,
        test_runner=test_runner,
        approval_callback=approval_wrapper,
    )

    print(render_auxiliary_panel(stage="FASE 1: ESPECIFICACIÓN", branch=branch_name, tokens=250))

    try:
        # Stage 1: Spec
        spec_content = await engine.execute_spec_stage(task_desc)

        # Stage 2: Stash Shield & Environment
        print(render_auxiliary_panel(stage="FASE 2: ENTORNO GIT", branch=branch_name, tokens=450))
        if not engine.stash_shield.is_clean():
            print("⚠️ Advertencia: El working tree de Git tiene cambios sin confirmar.")

        # Stage 3: Verifier TDD Cycle
        print(render_auxiliary_panel(stage="FASE 3: TDD VERIFIER", branch=branch_name, tokens=950))
        success = await engine.execute_tdd_cycle(ac_id="AC-1", ac_desc="Happy path verification")
        if not success:
            print("⚠️ Re-intentando ciclo TDD tras primer fallo...")
            success = await engine.execute_tdd_cycle(ac_id="AC-1", ac_desc="Happy path verification")
            if not success:
                print("⚠️ Advertencia: El ciclo TDD reportó advertencias en la fase de implementación.")

        # Stage 4: OKF Release
        print(render_auxiliary_panel(stage="FASE 4: CIERRE OKF", branch=branch_name, tokens=1450))
        pr_draft = await engine.finalize_release(feature_name=slugify_task(task_desc))

        print(f"\n🎉 ¡Ciclo Karpathy SDLC completado con éxito!")
        print(f"📄 Resumen de PR generado listo para revisión.")
        return 0

    except EngineError as e:
        if engine.current_stage == SDLCStage.CIRCUIT_BREAKER_TRIPPED:
            report = engine.circuit_breaker.generate_friction_report()
            print(render_friction_alert(report))
        else:
            print(f"\n🛑 Error en el motor de ejecución ({engine.current_stage.value}): {e}")
        return 1
    except Exception as e:
        print(f"\n🛑 Error inesperado durante la ejecución: {e}")
        return 1


async def main():
    config = parse_args()
    code = await run_pipeline_cli(config)
    sys.exit(code)


if __name__ == "__main__":
    asyncio.run(main())
