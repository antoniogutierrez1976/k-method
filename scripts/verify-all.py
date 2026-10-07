#!/usr/bin/env python3
"""
k-method Universal Quality Gates Runner.
Runs unit tests, OKF graph lint/compilation, and git stash shield checks.
Platform-agnostic entrypoint for Bitbucket, Azure DevOps, GitHub Actions, and Local Git Hooks.
"""
import os
import sys
import subprocess
import argparse

# Ensure UTF-8 output on Windows PowerShell / cmd
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def run_command(cmd, step_name, env=None):
    """Executes a subprocess command and streams its output, returning exit code."""
    print(f"\n=======================================================")
    print(f"▶ EJECUTANDO: {step_name}")
    print(f"  Comando: {' '.join(cmd)}")
    print(f"=======================================================")
    res = subprocess.run(cmd, env=env)
    if res.returncode != 0:
        print(f"❌ FALLÓ: {step_name} (Código de salida: {res.returncode})")
        return res.returncode
    print(f"✅ COMPLETADO: {step_name}")
    return 0

def run_all_gates(skip_git_diff=False):
    """Runs all quality gates sequentially."""
    results = {}
    python_bin = sys.executable

    # Gate 1: Automated Unit Test Suite (Tests Integrity & Dry Compliance)
    test_cmd = [python_bin, "-m", "unittest", "discover", "-s", "tests", "-v"]
    sub_env = os.environ.copy()
    sub_env["K_METHOD_RUNNER_ACTIVE"] = "1"
    code_tests = run_command(test_cmd, "Suite de Pruebas Unitarias (unittest)", env=sub_env)
    results["Suite de Pruebas Unitarias"] = (code_tests == 0)
    if code_tests != 0:
        return 1, results

    # Gate 2: OKF Graph Integrity & Index Recompilation
    lint_script = os.path.join(".agents", "skills", "k-wiki", "scripts", "okf-lint.py")
    lint_cmd = [python_bin, lint_script, "--compile-index"]
    code_lint = run_command(lint_cmd, "OKF Knowledge Graph Linter & Compiler")
    results["OKF Knowledge Graph"] = (code_lint == 0)
    if code_lint != 0:
        return 1, results

    # Gate 3: Git Working Tree Derivation Check (Stash Shield)
    if not skip_git_diff:
        git_cmd = ["git", "diff", "--exit-code"]
        code_git = run_command(git_cmd, "Stash Shield / Verificación de Deriva Git")
        results["Stash Shield (git diff)"] = (code_git == 0)
        if code_git != 0:
            return 1, results
    else:
        results["Stash Shield (git diff)"] = True

    return 0, results

def main():
    parser = argparse.ArgumentParser(description="k-method Universal Quality Gates Runner")
    parser.add_argument("--skip-git-diff", action="store_true", help="Omit git diff exit-code verification")
    args = parser.parse_args()

    print("═══════════════════════════════════════════════════════")
    print("       k-method: UNIVERSAL QUALITY GATES RUNNER        ")
    print("═══════════════════════════════════════════════════════")

    exit_code, results = run_all_gates(skip_git_diff=args.skip_git_diff)

    print("\n═══════════════════════════════════════════════════════")
    print("               RESUMEN DE VERIFICACIÓN                 ")
    print("═══════════════════════════════════════════════════════")
    for gate, passed in results.items():
        status = "✅ PASÓ" if passed else "❌ FALLÓ"
        print(f"  - {gate.ljust(35)}: {status}")

    if exit_code == 0:
        print("\n🎉 TODO CORRECTO: Todas las puertas de calidad de k-method superadas.")
    else:
        print("\n🛑 VERIFICACIÓN RECHAZADA: Una o más compuertas de calidad no se cumplieron.")

    return exit_code

if __name__ == "__main__":
    sys.exit(main())
