import os
import sys
import unittest
import importlib.util

# Dynamically import okf-lint module from .agents/skills/k-wiki/scripts/okf-lint.py
LINT_SCRIPT_PATH = os.path.join(".agents", "skills", "k-wiki", "scripts", "okf-lint.py")
spec = importlib.util.spec_from_file_location("okf_lint", LINT_SCRIPT_PATH)
okf_lint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(okf_lint)

class TestOKFCompiler(unittest.TestCase):
    """Verifies OKF graph linter, parser, and compilation logic."""

    def test_parse_frontmatter_edge_cases(self):
        """Frontmatter parser must handle null, lists, and inline arrays without crashing."""
        sample_yaml = """---
okf_version: "1.0"
node_type: concept
id: "test-node"
status: active
domain: "test-domain"
governed_by: ["[[ADR-001]]"]
dependencies:
  - dep-1
  - dep-2
supersedes: null
superseded_by: ~
updated_at: "2026-10-07"
---
# Content Body with [[ADR-001]] link.
"""
        meta, body = okf_lint.parse_frontmatter(sample_yaml)
        self.assertIsNotNone(meta)
        self.assertEqual(meta.get("okf_version"), "1.0")
        self.assertEqual(meta.get("id"), "test-node")
        self.assertEqual(meta.get("status"), "active")
        self.assertEqual(meta.get("domain"), "test-domain")
        self.assertEqual(meta.get("governed_by"), ["[[ADR-001]]"])
        self.assertEqual(meta.get("dependencies"), ["dep-1", "dep-2"])
        self.assertIsNone(meta.get("supersedes"))
        self.assertIsNone(meta.get("superseded_by"))
        self.assertIn("Content Body with [[ADR-001]] link.", body)

    def test_current_knowledge_base_integrity(self):
        """The real knowledge-base/wiki graph must pass lint with zero errors."""
        exit_code = okf_lint.run_lint(auto_compile=False)
        self.assertEqual(exit_code, 0, "OKF lint detected errors in knowledge-base/wiki graph")

    def test_find_wikilinks(self):
        """Wikilinks extractor must extract bracketed names."""
        text = "Relates to [[spec-driven-development]] and [[environment-governor]]."
        links = okf_lint.find_wikilinks(text)
        self.assertEqual(links, ["spec-driven-development", "environment-governor"])

if __name__ == "__main__":
    unittest.main()
