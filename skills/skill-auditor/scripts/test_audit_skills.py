#!/usr/bin/env python3
"""Regression tests for the deterministic skill auditor."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


AUDITOR = Path(__file__).with_name("audit_skills.py")


class AuditorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.external_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()
        self.external_directory.cleanup()

    def write_skill(
        self,
        directory: str,
        *,
        name: str,
        description: str = "Inspect a fixture. Use when testing the skill auditor.",
        body: str = "# Fixture\n",
    ) -> Path:
        skill_directory = self.root / directory
        skill_directory.mkdir(parents=True, exist_ok=True)
        path = skill_directory / "SKILL.md"
        path.write_text(
            f"---\nname: {name}\ndescription: {description}\n---\n\n{body}",
            encoding="utf-8",
        )
        return path

    def audit(self, *extra: str) -> tuple[int, dict]:
        result = subprocess.run(
            [
                sys.executable,
                str(AUDITOR),
                str(self.root),
                "--format",
                "json",
                *extra,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        return result.returncode, json.loads(result.stdout)

    def codes(self, report: dict) -> list[str]:
        return [finding["code"] for finding in report["findings"]]

    def test_clean_skill_is_deterministic(self) -> None:
        self.write_skill(
            "clean",
            name="clean-skill",
            body="# Clean\n\n[Reference](reference.md)\n\n```md\n[Example](missing.md)\n```\n",
        )
        (self.root / "clean/reference.md").write_text("# Reference\n", encoding="utf-8")

        first_status, first = self.audit()
        second_status, second = self.audit()

        self.assertEqual(first_status, 0)
        self.assertEqual(first, second)
        self.assertEqual(first["findings"], [])

    def test_inline_markdown_example_is_not_a_link(self) -> None:
        self.write_skill(
            "inline",
            name="inline-example",
            body="# Inline example\n\nDo not report `[link](path)` as a file reference.\n",
        )

        status, report = self.audit()

        self.assertEqual(status, 0)
        self.assertNotIn("R001", self.codes(report))

    def test_follows_skill_directory_symlinks_once(self) -> None:
        source = Path(self.external_directory.name) / "source"
        source.mkdir(parents=True)
        (source / "SKILL.md").write_text(
            "---\nname: linked-skill\ndescription: Follow this skill when auditing linked installs.\n---\n",
            encoding="utf-8",
        )
        install = self.root / "catalog"
        install.mkdir()
        (install / "linked-skill").symlink_to(source, target_is_directory=True)

        status, report = self.audit()

        self.assertEqual(status, 0)
        self.assertEqual(report["skills"], 1)

    def test_broken_markdown_link_is_high(self) -> None:
        self.write_skill("broken", name="broken-link", body="# Broken\n\n[Missing](missing.md)\n")

        status, report = self.audit()

        self.assertEqual(status, 1)
        self.assertIn("R001", self.codes(report))

    def test_duplicate_names_are_high(self) -> None:
        self.write_skill("one", name="duplicate-name")
        self.write_skill("two", name="duplicate-name")

        status, report = self.audit()

        self.assertEqual(status, 1)
        self.assertEqual(self.codes(report).count("S003"), 2)

    def test_absolute_path_depends_on_profile(self) -> None:
        self.write_skill("portable", name="portable-test", body="# Portable\n\nUse /Users/example/private/data.\n")

        claude_status, claude = self.audit("--profile", "claude")
        cross_status, cross = self.audit("--profile", "cross-runtime")

        self.assertEqual(claude_status, 0)
        self.assertNotIn("X001", self.codes(claude))
        self.assertEqual(cross_status, 0)
        self.assertIn("X001", self.codes(cross))

    def test_manifest_identity_mismatch_is_high(self) -> None:
        self.write_skill("skills/example", name="manifest-example")
        for runtime, version in ((".claude-plugin", "1.0.0"), (".codex-plugin", "2.0.0")):
            directory = self.root / runtime
            directory.mkdir()
            (directory / "plugin.json").write_text(
                json.dumps(
                    {
                        "name": "fixture",
                        "version": version,
                        "repository": "https://example.com/fixture",
                        "skills": "./skills",
                    }
                ),
                encoding="utf-8",
            )

        status, report = self.audit("--profile", "cross-runtime")

        self.assertEqual(status, 1)
        self.assertIn("P003", self.codes(report))

    def test_discovers_nested_plugin_manifests(self) -> None:
        self.write_skill("packages/example/skills/example", name="nested-plugin")
        manifest_directory = self.root / "packages/example/.codex-plugin"
        manifest_directory.mkdir(parents=True)
        (manifest_directory / "plugin.json").write_text(
            json.dumps(
                {
                    "name": "nested-plugin",
                    "version": "1.0.0",
                    "repository": "https://example.com/nested-plugin",
                    "skills": "./skills",
                }
            ),
            encoding="utf-8",
        )

        status, report = self.audit("--profile", "codex")

        self.assertEqual(status, 0)
        self.assertEqual(report["plugin_manifests"], 1)

    def test_agents_marketplace_source_resolves_from_marketplace_root(self) -> None:
        self.write_skill("plugins/example/skills/example", name="marketplace-example")
        manifest_directory = self.root / ".agents/plugins"
        manifest_directory.mkdir(parents=True)
        (manifest_directory / "marketplace.json").write_text(
            json.dumps(
                {
                    "name": "fixture",
                    "plugins": [
                        {
                            "name": "example",
                            "source": {"source": "local", "path": "./plugins/example"},
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        status, report = self.audit("--profile", "codex")

        self.assertEqual(status, 0)
        self.assertNotIn("P002", self.codes(report))


if __name__ == "__main__":
    unittest.main()
