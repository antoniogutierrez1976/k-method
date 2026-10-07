"""
Intent Classifier & Task Router for k-method SDLC Engine.
Distinguishes between Queries (Q&A), Features (full SDLC with spec.md),
Bugfixes (forensic triage & regression), and Chores (routine maintenance).
"""
import json
import re
from enum import Enum
from typing import Tuple, Optional
from scripts.harness.providers.base import BaseAgentProvider


class TaskIntent(Enum):
    QUERY = "query"       # Questions, repository inspection, Q&A
    FEATURE = "feature"   # New features, enhancements, architecture changes
    BUGFIX = "bugfix"     # Fixing bugs, handling regressions
    CHORE = "chore"       # Routine maintenance, formatting, dependencies


INTENT_CLASSIFICATION_PROMPT = """You are the k-method SDLC Intent Classifier.
Evaluate the user's input and classify it into exactly ONE of the following task categories:

1. QUERY: The user is asking a question, seeking information, asking what the project is or contains, requesting an explanation, or asking about architecture/code. No code changes or specs should be generated.
   Examples:
   - "en que consiste el proyecto"
   - "¿qué hace la skill k-verifier?"
   - "explícame cómo funciona el stash shield"
   - "dónde se guardan los specs"
   - "what does this repo do?"
   - "dime los ADRs vigentes"

2. FEATURE: The user wants to build, add, develop, or implement a new feature or capability that requires an SDLC cycle with specification (spec.md) and TDD.
   Examples:
   - "implementar endpoint de métricas"
   - "añadir soporte para ollama"
   - "crear interfaz de exportación a PDF"
   - "desarrollar componente de login"

3. BUGFIX: The user is reporting an error, defect, or broken behavior to fix.
   Examples:
   - "corregir error 500 al refrescar"
   - "el parser de frontmatter falla con valores nulos"
   - "fix broken link in wiki"

4. CHORE: Routine maintenance, dependency updates, formatting, or cleanup.
   Examples:
   - "actualizar dependencias"
   - "limpiar archivos temporales"
   - "formatear código con black"

Respond ONLY with valid JSON in this exact structure:
{"intent": "QUERY" | "FEATURE" | "BUGFIX" | "CHORE", "reason": "brief explanation in Spanish"}
"""


def heuristic_classify_intent(user_input: str) -> TaskIntent:
    """
    Fast rule-based intent classification for instant response.
    """
    text = user_input.strip().lower()

    # Question and informational patterns
    question_prefixes = (
        "en que ", "en qué ", "¿", "que ", "qué ", "cómo ", "como ",
        "donde ", "dónde ", "cuál ", "cual ", "cuáles ", "quién ",
        "explica", "cuéntame", "dime", "muéstrame", "what ", "how ",
        "where ", "why ", "explain ", "tell me ", "show me "
    )
    if any(text.startswith(p) for p in question_prefixes) or text.endswith("?"):
        return TaskIntent.QUERY

    if any(k in text for k in (
        "consiste", "para qué sirve", "de qué trata", "qué contiene",
        "que contiene", "como funciona", "cómo funciona"
    )):
        return TaskIntent.QUERY

    # Bugfix patterns
    if any(text.startswith(p) for p in ("fix", "corregir", "arreglar", "solucionar", "reparar", "bug")):
        return TaskIntent.BUGFIX

    # Chore patterns
    if any(text.startswith(p) for p in ("chore", "actualizar", "limpiar", "formatear", "update deps")):
        return TaskIntent.CHORE

    # Default to FEATURE
    return TaskIntent.FEATURE


async def classify_task_intent(
    user_input: str,
    provider: Optional[BaseAgentProvider] = None
) -> Tuple[TaskIntent, str]:
    """
    Evaluates user input using heuristics first, then LLM if ambiguous.
    """
    # 1. Fast heuristic check for obvious inquiries
    heuristic = heuristic_classify_intent(user_input)
    if heuristic == TaskIntent.QUERY:
        return TaskIntent.QUERY, "Consulta informativa o pregunta sobre el proyecto detectada."

    # 2. If provider is available, use LLM for nuanced classification
    if provider is not None:
        try:
            response = await provider.chat_atomic(
                prompt=f"User input to classify: {user_input}",
                system_prompt=INTENT_CLASSIFICATION_PROMPT
            )
            content = response.content.strip()
            json_match = re.search(r"\{.*?\}", content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                intent_str = str(data.get("intent", "")).upper()
                reason = data.get("reason", "")
                if intent_str == "QUERY":
                    return TaskIntent.QUERY, reason
                elif intent_str == "BUGFIX":
                    return TaskIntent.BUGFIX, reason
                elif intent_str == "CHORE":
                    return TaskIntent.CHORE, reason
                elif intent_str == "FEATURE":
                    return TaskIntent.FEATURE, reason
        except Exception:
            pass

    return heuristic, "Clasificación de tarea por reglas de intención."
