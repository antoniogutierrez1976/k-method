import os
import unittest
import re

SKILLS_DIR = os.path.join(".agents", "skills")
EXPECTED_SKILLS = [
    "k-orchestrator",
    "k-spec",
    "k-verifier",
    "k-environment",
    "k-wiki"
]

class TestSkillsIntegrity(unittest.TestCase):
    """Verifies that all skills in .agents/skills comply with constitution invariants."""

    def test_expected_skills_exist(self):
        """All 5 core Karpathy skills must exist in .agents/skills."""
        self.assertTrue(os.path.exists(SKILLS_DIR), f"{SKILLS_DIR} directory does not exist")
        actual_dirs = [
            d for d in os.listdir(SKILLS_DIR)
            if os.path.isdir(os.path.join(SKILLS_DIR, d))
        ]
        for skill in EXPECTED_SKILLS:
            self.assertIn(skill, actual_dirs, f"Required skill '{skill}' missing from {SKILLS_DIR}")

    def test_skill_markdown_and_frontmatter(self):
        """Every skill must contain a SKILL.md with valid YAML frontmatter matching directory name."""
        for skill in EXPECTED_SKILLS:
            skill_md_path = os.path.join(SKILLS_DIR, skill, "SKILL.md")
            self.assertTrue(os.path.exists(skill_md_path), f"SKILL.md missing in {skill}")

            with open(skill_md_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertTrue(content.startswith("---"), f"SKILL.md in {skill} must start with YAML frontmatter delimiter (---)")
            parts = content.split("---", 2)
            self.assertGreaterEqual(len(parts), 3, f"SKILL.md in {skill} must have closing YAML delimiter (---)")

            fm = parts[1]
            name_match = re.search(r"^name:\s*([^\r\n]+)", fm, re.MULTILINE)
            desc_match = re.search(r"^description:\s*([^\r\n]+)", fm, re.MULTILINE)

            self.assertIsNotNone(name_match, f"SKILL.md in {skill} must declare 'name' in frontmatter")
            declared_name = name_match.group(1).strip().strip('"').strip("'")
            self.assertEqual(declared_name, skill, f"SKILL.md frontmatter name '{declared_name}' does not match directory '{skill}'")

            self.assertIsNotNone(desc_match, f"SKILL.md in {skill} must declare 'description' in frontmatter")
            desc_val = desc_match.group(1).strip().strip('"').strip("'")
            if desc_val in [">-", ">", "|-", "|", ""]:
                # Multiline YAML block scalar: extract indented lines below
                lines = fm.splitlines()
                desc_idx = next(i for i, l in enumerate(lines) if l.strip().startswith("description:"))
                continuation = []
                for l in lines[desc_idx + 1:]:
                    if l.startswith("  ") or l.startswith("\t"):
                        continuation.append(l.strip())
                    elif l.strip() and not l.startswith("#"):
                        break
                desc_val = " ".join(continuation)

            self.assertGreater(len(desc_val), 10, f"Description in {skill} is too short: '{desc_val}'")

    def test_dry_and_no_duplicate_scripts(self):
        """Enforces DRY: no duplicate helper scripts across skills."""
        script_files = {}
        for root, _, files in os.walk(SKILLS_DIR):
            for file in files:
                if file.endswith((".py", ".sh", ".bash", ".ps1")):
                    rel_path = os.path.relpath(os.path.join(root, file), SKILLS_DIR)
                    self.assertNotIn(file, script_files, f"Duplicate script detected: '{file}' in both {script_files.get(file)} and {rel_path}")
                    script_files[file] = rel_path

if __name__ == "__main__":
    unittest.main()
