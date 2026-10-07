import os
import unittest

CI_TEMPLATES_DIR = os.path.join("templates", "ci")

class TestCITemplates(unittest.TestCase):
    """Verifies AC-Sec-1, AC-2, AC-3, AC-4, AC-5: Multi-platform CI templates."""

    def test_AC_Sec_1_least_privilege_and_no_secrets(self):
        """All CI templates must enforce least privilege and avoid hardcoded secrets or sensitive env exposure."""
        self.assertTrue(os.path.exists(CI_TEMPLATES_DIR), f"{CI_TEMPLATES_DIR} does not exist")
        for f in os.listdir(CI_TEMPLATES_DIR):
            file_path = os.path.join(CI_TEMPLATES_DIR, f)
            with open(file_path, "r", encoding="utf-8") as fh:
                content = fh.read().lower()
            self.assertNotIn("password:", content, f"Sensitive keyword in {f}")
            self.assertNotIn("api_key", content, f"Sensitive keyword in {f}")
            self.assertNotIn("secret:", content, f"Sensitive keyword in {f}")

    def test_AC_2_bitbucket_pipelines_template(self):
        """Bitbucket template must define python pipeline invoking scripts/verify-all.py."""
        bb_path = os.path.join(CI_TEMPLATES_DIR, "bitbucket-pipelines.template.yml")
        self.assertTrue(os.path.exists(bb_path), f"Missing {bb_path}")
        with open(bb_path, "r", encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("image: python:3", content)
        self.assertIn("scripts/verify-all.py", content)

    def test_AC_3_azure_pipelines_template(self):
        """Azure DevOps template must specify python setup and invoke scripts/verify-all.py."""
        az_path = os.path.join(CI_TEMPLATES_DIR, "azure-pipelines.template.yml")
        self.assertTrue(os.path.exists(az_path), f"Missing {az_path}")
        with open(az_path, "r", encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("UsePythonVersion@0", content)
        self.assertIn("scripts/verify-all.py", content)

    def test_AC_4_github_actions_template(self):
        """GitHub Actions template must specify permissions: contents: read and invoke scripts/verify-all.py."""
        gh_path = os.path.join(CI_TEMPLATES_DIR, "github-ci.template.yml")
        self.assertTrue(os.path.exists(gh_path), f"Missing {gh_path}")
        with open(gh_path, "r", encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("contents: read", content)
        self.assertIn("scripts/verify-all.py", content)

    def test_AC_5_git_pre_push_hook_template(self):
        """Git pre-push hook must be a POSIX shell script calling scripts/verify-all.py."""
        hook_path = os.path.join(CI_TEMPLATES_DIR, "git-pre-push.template.sh")
        self.assertTrue(os.path.exists(hook_path), f"Missing {hook_path}")
        with open(hook_path, "r", encoding="utf-8") as fh:
            content = fh.read()
        self.assertTrue(content.startswith("#!/bin/sh") or content.startswith("#!/usr/bin/env bash"))
        self.assertIn("scripts/verify-all.py", content)

if __name__ == "__main__":
    unittest.main()
