"""
UI rendering package for k-method Windows harness.
Provides Antigravity-style ANSI terminal formatting and auxiliary panels.
"""
from .renderer import (
    sanitize_terminal_output,
    render_banner,
    render_auxiliary_panel,
    render_friction_alert,
    prompt_human_approval,
)

__all__ = [
    "sanitize_terminal_output",
    "render_banner",
    "render_auxiliary_panel",
    "render_friction_alert",
    "prompt_human_approval",
]
