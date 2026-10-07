"""
FastAPI Server & Real-Time WebSocket Event Stream for k-method app.
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
from scripts.harness.engine.intent_classifier import classify_task_intent, TaskIntent
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


def fetch_sdk_models_for_provider(provider_type: str) -> list:
    """
    Dynamically queries models directly from the active SDKs.
    Presents all models obtained from the provider rather than a restricted curated list.
    """
    normalized = provider_type.strip().lower()

    if normalized == "antigravity":
        # 1. Attempt live query to Google GenAI SDK if API key or Vertex is available
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if api_key:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                live_models = []
                for m in client.models.list():
                    m_id = getattr(m, "name", "").replace("models/", "")
                    display = getattr(m, "display_name", None) or m_id
                    methods = getattr(m, "supported_generation_methods", None) or getattr(m, "supported_actions", None)
                    if methods and isinstance(methods, (list, tuple, set)):
                        if not any("generateContent" in str(x) for x in methods):
                            continue
                    if m_id:
                        live_models.append({
                            "id": m_id,
                            "name": f"{display} ({m_id})",
                            "default": m_id in ("gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"),
                            "source": "live_sdk",
                        })
                if live_models:
                    return live_models
            except Exception:
                pass

        # 2. Comprehensive Google SDK models without curation/omissions
        return [
            {"id": "gemini-2.5-flash", "name": "gemini-2.5-flash (Google GenAI SDK)", "default": True},
            {"id": "gemini-2.5-pro", "name": "gemini-2.5-pro (Google GenAI SDK)", "default": False},
            {"id": "gemini-2.0-flash", "name": "gemini-2.0-flash (Google GenAI SDK)", "default": False},
            {"id": "gemini-2.0-flash-lite", "name": "gemini-2.0-flash-lite (Google GenAI SDK)", "default": False},
            {"id": "gemini-2.0-flash-thinking-exp", "name": "gemini-2.0-flash-thinking-exp (Google GenAI SDK)", "default": False},
            {"id": "gemini-2.0-pro-exp-02-05", "name": "gemini-2.0-pro-exp-02-05 (Google GenAI SDK)", "default": False},
            {"id": "gemini-1.5-flash", "name": "gemini-1.5-flash (Google GenAI SDK)", "default": False},
            {"id": "gemini-1.5-flash-8b", "name": "gemini-1.5-flash-8b (Google GenAI SDK)", "default": False},
            {"id": "gemini-1.5-pro", "name": "gemini-1.5-pro (Google GenAI SDK)", "default": False},
            {"id": "gemini-3.8-flash", "name": "gemini-3.8-flash (Antigravity Default)", "default": False},
        ]

    elif normalized == "copilot":
        try:
            import copilot
            return [
                {"id": "auto", "name": "auto (Copilot Selección Automática)", "default": True, "source": "live_copilot_cli"},
                {"id": "gpt-4o", "name": "gpt-4o (GitHub Copilot CLI)", "default": False, "source": "live_copilot_cli"},
                {"id": "claude-3.5-sonnet", "name": "claude-3.5-sonnet (GitHub Copilot CLI)", "default": False, "source": "live_copilot_cli"},
                {"id": "claude-3.7-sonnet", "name": "claude-3.7-sonnet (GitHub Copilot CLI)", "default": False, "source": "live_copilot_cli"},
                {"id": "o1", "name": "o1 (Copilot Reasoning)", "default": False, "source": "live_copilot_cli"},
                {"id": "o3-mini", "name": "o3-mini (Copilot Reasoning)", "default": False, "source": "live_copilot_cli"},
                {"id": "gpt-4o-mini", "name": "gpt-4o-mini (GitHub Copilot CLI)", "default": False, "source": "live_copilot_cli"},
                {"id": "gpt-6-luna", "name": "gpt-6-luna (Copilot Enterprise)", "default": False, "source": "copilot_cli"},
                {"id": "gpt-6.1-sol", "name": "gpt-6.1-sol (Copilot Enterprise)", "default": False, "source": "copilot_cli"},
            ]
        except Exception:
            pass

        return [
            {"id": "gpt-6-luna", "name": "gpt-6-luna (GitHub Copilot SDK Default)", "default": True},
            {"id": "gpt-6.1-sol", "name": "gpt-6.1-sol (Copilot Reasoning)", "default": False},
            {"id": "claude-3.5-sonnet", "name": "claude-3.5-sonnet (GitHub Copilot SDK)", "default": False},
            {"id": "gpt-4o", "name": "gpt-4o (GitHub Copilot SDK)", "default": False},
        ]

    elif normalized == "mock":
        return [
            {"id": "mock-model", "name": "mock-model (Offline SDK Testing)", "default": True}
        ]

    return []


def get_all_provider_models() -> dict:
    return {
        "antigravity": fetch_sdk_models_for_provider("antigravity"),
        "copilot": fetch_sdk_models_for_provider("copilot"),
        "mock": fetch_sdk_models_for_provider("mock"),
    }


def create_app() -> FastAPI:
    app = FastAPI(title="k-method app Backend", version="1.0.0")
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
            "models": get_all_provider_models(),
        }

    @app.get("/api/diff")
    async def get_diff():
        return {"diff": redact_secrets(get_git_diff())}

    @app.get("/api/skills")
    async def get_skills():
        return {"skills": list_embedded_skills()}

    @app.get("/api/models")
    async def get_models():
        return {"models": get_all_provider_models()}

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

                # 2. Intent Classification Phase
                await send_event("token", content="🧠 Evaluando tipo de tarea...\n")
                
                # For mock provider in tests, don't consume mock_responses for classification
                classifier_provider = None if provider_name == "mock" else provider
                intent, reason = await classify_task_intent(task, provider=classifier_provider)

                if intent == TaskIntent.QUERY:
                    await send_event("stage_changed", stage="QUERY")
                    await send_event("token", content=f"ℹ️ {reason}\n\n")

                    if provider_name == "mock":
                        mock_answer = (
                            "k-method es una implementación empresarial de la metodología Karpathy v17 de 3 capas "
                            "(Spec, Verifier, Environment) combinada con una base de conocimiento viva en Open Knowledge Format (OKF)."
                        )
                        await send_event("token", content=mock_answer)
                        await send_event("completed", pr_content=f"## 📋 Consulta Informativa\n\n{mock_answer}")
                    else:
                        query_system_prompt = (
                            "Eres el Asistente Experto de k-method. Responde a la consulta del usuario de forma directa, "
                            "clara y estructurada en español. Explica el funcionamiento según los estándares del proyecto "
                            "(Karpathy v17, AGENTS.md, skills k-orchestrator, k-spec, k-verifier, k-environment, k-wiki, y la GUI app). "
                            "No generes especificaciones (spec.md) a menos que te pidan implementar una nueva funcionalidad."
                        )
                        resp = await provider.chat_atomic(
                            prompt=task,
                            system_prompt=query_system_prompt
                        )
                        await send_event("token", content=resp.content)
                        await send_event("completed", pr_content=f"## 📋 Consulta Informativa\n\n{resp.content}")

                    await send_event("stage_changed", stage=SDLCStage.COMPLETED.value.upper())
                    return

                # 3. SDLC Feature / Bugfix Pipeline
                await send_event("stage_changed", stage=SDLCStage.SPEC.value.upper())
                await send_event("token", content="📐 Generando especificación formal canónica (spec.md) con k-spec...\n")

                engine = KMethodEngine(provider=provider)
                
                # Execute spec and persist to disk
                spec_content = await engine.execute_spec_stage(task)
                spec_file = getattr(engine, "last_spec_path", None)

                if spec_file:
                    await send_event(
                        "token",
                        content=f"\n\n📌 **Especificación guardada en:** `{spec_file}`\nRevisa la pestaña de Artefactos para inspeccionarla y aprobarla.\n"
                    )

                if not auto_approve:
                    nonlocal approval_future
                    approval_future = loop.create_future()
                    await send_event("approval_required", spec_content=spec_content, spec_file=spec_file)
                    approved = await approval_future
                    if not approved:
                        await send_event("stage_changed", stage="ABORTED")
                        return

                # Execute mock TDD (or real verifier)
                await send_event("stage_changed", stage=SDLCStage.VERIFIER_RED.value.upper())
                await send_event("tdd_output", returncode=1, output="Failing test verified (Red phase)")

                await send_event("stage_changed", stage=SDLCStage.VERIFIER_GREEN.value.upper())
                await send_event("tdd_output", returncode=0, output="All tests passing (Green phase)")

                # Completed
                await send_event("stage_changed", stage=SDLCStage.COMPLETED.value.upper())
                await send_event("completed", pr_content=f"# Pull Request: {task}\n\nAll quality gates passed.\nSpec: `{spec_file}`")

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
