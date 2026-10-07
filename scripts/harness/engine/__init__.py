"""
k-method SDLC orchestration engine package.
Enforces Karpathy 3-layer state transitions, circuit breakers, and Git guards.
"""
from .state_machine import (
    SDLCStage,
    CircuitBreaker,
    StashShield,
    KMethodEngine,
    EngineError,
)

__all__ = [
    "SDLCStage",
    "CircuitBreaker",
    "StashShield",
    "KMethodEngine",
    "EngineError",
]
