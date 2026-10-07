import unittest
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from scripts.harness.engine.intent_classifier import (
    TaskIntent,
    heuristic_classify_intent,
    classify_task_intent,
)
from scripts.harness.providers.mock_provider import MockProvider


class TestIntentClassifier(unittest.IsolatedAsyncioTestCase):
    """
    Tests for intent classification and task routing.
    """

    def test_heuristic_queries(self):
        queries = [
            "en que consiste el proyecto",
            "¿qué hace la skill k-verifier?",
            "cómo funciona el stash shield",
            "dónde se guardan los specs?",
            "cuéntame sobre la arquitectura",
            "what does this repo do?",
            "explain Karpathy v0",
            "para qué sirve el orchestrator",
        ]
        for q in queries:
            intent = heuristic_classify_intent(q)
            self.assertEqual(intent, TaskIntent.QUERY, f"Failed on: {q}")

    def test_heuristic_features(self):
        features = [
            "implementar endpoint de métricas",
            "añadir soporte para ollama",
            "crear interfaz de exportación a PDF",
            "desarrollar componente de autenticación",
        ]
        for f in features:
            intent = heuristic_classify_intent(f)
            self.assertEqual(intent, TaskIntent.FEATURE, f"Failed on: {f}")

    def test_heuristic_bugfixes(self):
        fixes = [
            "fix broken link in wiki",
            "corregir error 500 al refrescar",
            "arreglar fallo de frontmatter",
            "solucionar bug de WebSocket",
        ]
        for fix in fixes:
            intent = heuristic_classify_intent(fix)
            self.assertEqual(intent, TaskIntent.BUGFIX, f"Failed on: {fix}")

    def test_heuristic_chores(self):
        chores = [
            "chore: update dependencies",
            "actualizar dependencias de pip",
            "limpiar archivos temporales",
            "formatear código con black",
        ]
        for c in chores:
            intent = heuristic_classify_intent(c)
            self.assertEqual(intent, TaskIntent.CHORE, f"Failed on: {c}")

    async def test_llm_classification_with_mock(self):
        # When provider returns JSON intent
        mock_resp = '{"intent": "QUERY", "reason": "Usuario pregunta sobre el proyecto"}'
        provider = MockProvider(mock_responses=[mock_resp])

        # Input that might be ambiguous without LLM
        intent, reason = await classify_task_intent("detalles sobre el repositorio", provider=provider)
        self.assertEqual(intent, TaskIntent.QUERY)
        self.assertIn("Usuario pregunta", reason)


if __name__ == "__main__":
    unittest.main()
