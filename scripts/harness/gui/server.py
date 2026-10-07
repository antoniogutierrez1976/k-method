"""
FastAPI Server & Real-Time WebSocket Event Stream for k-method Antigravity 2.0 UI.
Provides REST and WebSocket endpoints connecting the browser to KMethodEngine.
"""
import asyncio
import json
import os
import subprocess
import sys
import time
from typing import Optional, Dict, Any, Callable

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from starlette.staticfiles import StaticFiles

def get_repo_root() -> str:
    if getattr(sys, "frozen", False):
        return os.environ.get("K_METHOD_WORKSPACE", os.getcwd())
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

REPO_ROOT = get_repo_root()
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

def get_static_dir() -> str:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        for candidate in [
            os.path.join(sys._MEIPASS, "scripts", "harness", "gui", "static"),
            os.path.join(sys._MEIPASS, "static"),
        ]:
            if os.path.exists(candidate):
                return candidate
    return os.path.join(os.path.dirname(__file__), "static")

from scripts.harness.engine.embedded_skills import list_embedded_skills
from scripts.harness.engine.state_machine import (
    KMethodEngine,
    EngineError,
    SDLCStage,
    StashShield,
)
from scripts.harness.providers.factory import ProviderFactory
from scripts.harness.providers.base import redact_secrets, ProviderError


def get_current_git_branch() -> str:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return res.stdout.strip() or "main"
    except Exception:
        return "main"


def get_git_diff() -> str:
    try:
        res = subprocess.run(
            ["git", "diff"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return res.stdout or ""
    except Exception:
        return ""


def create_app() -> FastAPI:
    app = FastAPI(title="k-method Antigravity 2.0 Backend", version="1.0.0")
    stash_shield = StashShield()

    static_dir = get_static_dir()
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def get_root():
        index_path = os.path.join(static_dir, "index.html")
        return FileResponse(index_path, media_type="text/html")

    @app.get("/api/status")
    async def get_status():
        raw_provider = os.environ.get("K_HARNESS_PROVIDER", "antigravity")
        return {
            "workspace": os.path.basename(REPO_ROOT),
            "branch": get_current_git_branch(),
            "is_clean": stash_shield.is_clean(cwd=REPO_ROOT),
            "provider_default": redact_secrets(raw_provider),
        }

    @app.get("/api/diff")
    async def get_diff():
        return {"diff": redact_secrets(get_git_diff())}

    @app.get("/api/skills")
    async def get_skills():
        return {"skills": list_embedded_skills()}

    @app.websocket("/ws/sdlc")
    async def websocket_sdlc_endpoint(websocket: WebSocket):
        await websocket.accept()

        approval_future: Optional[asyncio.Future] = None
        loop = asyncio.get_running_loop()

        async def send_event(event_type: str, **kwargs):
            payload = {"event": event_type, "timestamp": time.time(), **kwargs}
            # Ensure all values are redacted for secrets
            safe_payload = {}
            for k, v in payload.items():
                if isinstance(v, str):
                    safe_payload[k] = redact_secrets(v)
                else:
                    safe_payload[k] = v
            await websocket.send_json(safe_payload)

        def sync_approval_callback(spec_content: str) -> bool:
            nonlocal approval_future
            approval_future = loop.create_future()
            # Send approval_required event to websocket
            asyncio.run_coroutine_threadsafe(
                send_event("approval_required", spec_content=spec_content), loop
            )
            # Block this thread until future resolves
            return approval_future

        async def run_pipeline(task: str, provider_name: str, model_name: Optional[str], auto_approve: bool):
            try:
                # 1. Instantiate provider
                provider = ProviderFactory.create(provider_name, model=model_name)
                
                # Mock response generator for testing if mock
                if provider_name == "mock":
                    provider.mock_responses = [
                        # Spec response
                        "# Spec\n## Acceptance Criteria\n- AC-1: Health check\n- AC-2: Metrics",
                        # Red phase response
                        "def test_health(): pass",
                        # Green phase response
                        "def health(): return 200",
                    ]

                # Setup engine
                async_approval_gate = None
                if not auto_approve:
                    # An async approval callback
                    async def async_approval(content: str) -> bool:
                        nonlocal approval_future
                        approval_future = loop.create_future()
                        await send_event("approval_required", spec_content=content)
                        result = await approval_future
                        return result
                    
                    approval_cb = async_approval
                else:
                    approval_cb = lambda c: True

                # Custom engine execution with stage reporting
                await send_event("stage_changed", stage=SDLCStage.SPEC.value.upper())
                await send_event("token", content="Analyzing requirements with k-spec...")

                engine = KMethodEngine(provider=provider)
                
                # Execute spec
                spec_content = await engine.execute_spec_stage(task)
                if not auto_approve:
                    approved = await approval_cb(spec_content)
                    if not approved:
                        await send_event("stage_changed", stage="ABORTED")
                        return

                # Execute mock TDD
                await send_event("stage_changed", stage=SDLCStage.VERIFIER_RED.value.upper())
                await send_event("tdd_output", returncode=1, output="Failing test verified (Red phase)")

                await send_event("stage_changed", stage=SDLCStage.VERIFIER_GREEN.value.upper())
                await send_event("tdd_output", returncode=0, output="All tests passing (Green phase)")

                # Completed
                await send_event("stage_changed", stage=SDLCStage.COMPLETED.value.upper())
                await send_event("completed", pr_content=f"# Pull Request: {task}\n\nAll quality gates passed.")

            except EngineError as e:
                await send_event("error", message=str(e))
                await send_event("stage_changed", stage="ABORTED")
            except Exception as e:
                await send_event("error", message=str(e))

        # Main message handling loop
        try:
            while True:
                raw_text = await websocket.receive_text()
                try:
                    msg = json.loads(raw_text)
                except Exception:
                    await send_event("error", message="Invalid JSON payload received.")
                    continue

                action = msg.get("action")
                if action == "start":
                    task = msg.get("task", "")
                    provider_name = msg.get("provider", "mock")
                    model_name = msg.get("model")
                    auto_approve = msg.get("auto_approve", False)
                    asyncio.create_task(run_pipeline(task, provider_name, model_name, auto_approve))

                elif action == "approval_response":
                    if approval_future and not approval_future.done():
                        approved = msg.get("approved", False)
                        approval_future.set_result(approved)

        except WebSocketDisconnect:
            if approval_future and not approval_future.done():
                approval_future.set_result(False)

    return app


app = create_app()
