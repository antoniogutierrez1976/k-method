import re
import sys
from typing import Optional

# ANSI Color and Styling constants for Windows Terminal and PowerShell
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# Regex stripping dangerous OSC (Operating System Command) escape sequences while keeping safe formatting
OSC_ESCAPE_REGEX = re.compile(r"\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)")
CONTROL_CHARS_REGEX = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1a]")


def sanitize_terminal_output(text: str) -> str:
    """
    Strips dangerous OSC escape sequences and unprintable control characters to prevent terminal injection.
    """
    if not isinstance(text, str):
        return str(text)
    sanitized = OSC_ESCAPE_REGEX.sub("", text)
    sanitized = CONTROL_CHARS_REGEX.sub("", sanitized)
    return sanitized


def render_banner(provider: str, model: str, stage: str = "INIT") -> str:
    """
    Renders an Antigravity 2.0-style header banner.
    """
    line = "═" * 68
    banner = f"""
{CYAN}{BOLD}╔{line}╗
║                    🚀 ANTIGRAVITY SKILLS RUNNER                    ║
║                   k-method Karpathy SDLC Engine                    ║
╠{line}╣{RESET}
║  {BOLD}PROVEEDOR:{RESET} {provider.ljust(15)} │ {BOLD}MODELO:{RESET} {model.ljust(22)} ║
║  {BOLD}FASE ACTIVA:{RESET} {YELLOW}{stage.ljust(13)}{RESET} │ {BOLD}SISTEMA:{RESET} Windows (PowerShell/Terminal) ║
{CYAN}{BOLD}╚{line}╝{RESET}
"""
    return banner.strip()


def render_auxiliary_panel(stage: str, branch: str, tokens: int = 0) -> str:
    """
    Renders the Antigravity auxiliary status panel displaying stage, git branch and token telemetry.
    """
    panel = f"""
{DIM}┌── [ PANEL AUXILIAR DE ESTADO ] ───────────────────────────────────┐
│ • Etapa Actual:    {GREEN}{stage}{RESET}{DIM}
│ • Rama de Tarea:   {MAGENTA}{branch}{RESET}{DIM}
│ • Tokens Est.:     {YELLOW}{tokens}{RESET}{DIM}
└────────────────────────────────────────────────────────────────────┘{RESET}
"""
    return panel.strip()


def render_friction_alert(diff_report: str) -> str:
    """
    Renders a highlighted friction alert box when the Circuit Breaker trips.
    """
    safe_report = sanitize_terminal_output(diff_report)
    alert = f"""
{RED}{BOLD}╔════════════════════════════════════════════════════════════════════╗
║                   🛑 DISYUNTOR ACTIVADO (DEADLOCK)                 ║
║                2 Fallos Idénticos Consecutivos Detectados          ║
╚════════════════════════════════════════════════════════════════════╝{RESET}
{safe_report}
"""
    return alert.strip()


def prompt_human_approval(spec_content: str, auto_approve: bool = False) -> bool:
    """
    Displays the specification preview and prompts the operator for approval.
    Bypasses interactively if auto_approve is True.
    """
    if auto_approve:
        print(f"\n{YELLOW}[AUTO-APPROVE ACTIVADO]{RESET} Especificación aprobada automáticamente.")
        return True

    print(f"\n{CYAN}{BOLD}═══ [ VISTA PREVIA DE LA ESPECIFICACIÓN (k-spec) ] ══════════════════{RESET}")
    print(sanitize_terminal_output(spec_content))
    print(f"{CYAN}{BOLD}═════════════════════════════════════════════════════════════════════{RESET}")
    
    try:
        choice = input(f"\n{BOLD}¿Aprobar especificación e iniciar ciclo TDD? (s/n) [S]: {RESET}").strip().lower()
        if choice in ("", "s", "si", "y", "yes"):
            print(f"{GREEN}✅ Especificación aprobada por el operador.{RESET}")
            return True
        else:
            print(f"{RED}❌ Especificación rechazada por el operador.{RESET}")
            return False
    except (EOFError, KeyboardInterrupt):
        print(f"\n{RED}Operación cancelada.{RESET}")
        return False
