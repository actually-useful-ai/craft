#!/usr/bin/env python3
"""Regression coverage for Craft's standalone utility scripts."""

from __future__ import annotations

import html
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Dict, Optional
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run_script(script: str, *args: str, cwd: Path, env: Optional[Dict[str, str]] = None) -> subprocess.CompletedProcess:
    process_env = os.environ.copy()
    if env:
        process_env.update(env)
    return subprocess.run(
        [str(SCRIPTS / script), *args],
        cwd=cwd,
        env=process_env,
        text=True,
        capture_output=True,
        check=False,
    )


class BoardTests(unittest.TestCase):
    def test_all_board_text_is_html_escaped(self) -> None:
        payload = '<img src=x onerror="alert(1)">&\''
        with tempfile.TemporaryDirectory() as temporary_home:
            home = Path(temporary_home)
            board_path = home / "craft" / "board.json"
            board_path.parent.mkdir(parents=True)
            board_path.write_text(
                json.dumps(
                    {
                        "backlog": [
                            {
                                "title": payload,
                                "project": payload,
                                "created": payload,
                                "notes": payload,
                            }
                        ],
                        "doing": [],
                        "done": [],
                    }
                ),
                encoding="utf-8",
            )

            result = run_script(
                "generate-board.py",
                cwd=ROOT,
                env={"HOME": temporary_home},
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            rendered = (home / "html" / "craft" / "board" / "index.html").read_text(encoding="utf-8")
            self.assertNotIn(payload, rendered)
            escaped_payload = html.escape(payload)
            escaped_date = html.escape(payload[:10])
            self.assertEqual(rendered.count(escaped_payload), 3)
            self.assertIn(f"{escaped_payload} · {escaped_date}</div>", rendered)

    def test_column_label_is_html_escaped(self) -> None:
        module_path = SCRIPTS / "generate-board.py"
        spec = importlib.util.spec_from_file_location("craft_generate_board", module_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        label = "<script>alert(1)</script>"
        rendered = module.render_column(label, [])
        self.assertNotIn(label, rendered)
        self.assertIn(html.escape(label), rendered)


class NavigationTests(unittest.TestCase):
    def test_broken_link_is_counted_and_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            project = Path(temporary_dir)
            (project / "CLAUDE.md").write_text(
                "# Project\n\n[missing](does-not-exist.md)\n",
                encoding="utf-8",
            )

            result = run_script("validate-nav.sh", str(project), cwd=ROOT)

            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("BROKEN:", result.stdout)
            self.assertRegex(result.stdout, r"1 CLAUDE\.md files checked, 1 issues found")

    def test_runs_on_bash_3_and_handles_paths_with_spaces(self) -> None:
        source = (SCRIPTS / "validate-nav.sh").read_text(encoding="utf-8")
        self.assertNotRegex(source, re.compile(r"\bmapfile\b|\breadarray\b"))

        with tempfile.TemporaryDirectory() as temporary_dir:
            project = Path(temporary_dir)
            nested = project / "docs with spaces"
            nested.mkdir()
            (project / "CLAUDE.md").write_text(
                "# Project\n\n[guide](docs with spaces/guide.md)\n",
                encoding="utf-8",
            )
            (nested / "guide.md").write_text("# Guide\n", encoding="utf-8")
            (nested / "CLAUDE.md").write_text(
                "# Nested\n\nSee the parent CLAUDE file.\n",
                encoding="utf-8",
            )

            result = run_script("validate-nav.sh", str(project), cwd=ROOT)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("2 CLAUDE.md files checked, 0 issues found", result.stdout)

    def test_balanced_parentheses_in_destination_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            project = Path(temporary_dir)
            (project / "guide_(v2).md").write_text("# Guide\n", encoding="utf-8")
            (project / "CLAUDE.md").write_text(
                "# Project\n\n[guide](guide_(v2).md)\n",
                encoding="utf-8",
            )

            result = run_script("validate-nav.sh", str(project), cwd=ROOT)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("1 CLAUDE.md files checked, 0 issues found", result.stdout)

    def test_optional_markdown_link_title_is_not_part_of_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            project = Path(temporary_dir)
            (project / "guide_(v2).md").write_text("# Guide\n", encoding="utf-8")
            (project / "CLAUDE.md").write_text(
                '# Project\n\n[guide](guide_(v2).md "Guide (new)")\n',
                encoding="utf-8",
            )

            result = run_script("validate-nav.sh", str(project), cwd=ROOT)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("1 CLAUDE.md files checked, 0 issues found", result.stdout)

    def test_nested_relative_link_does_not_fall_back_to_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            project = Path(temporary_dir)
            nested = project / "nested"
            nested.mkdir()
            (project / "shared.md").write_text("# Coincidental root file\n", encoding="utf-8")
            (project / "CLAUDE.md").write_text("# Project\n", encoding="utf-8")
            (nested / "CLAUDE.md").write_text(
                "# Nested\n\nSee the parent instructions.\n\n[missing here](shared.md)\n",
                encoding="utf-8",
            )

            result = run_script("validate-nav.sh", str(project), cwd=ROOT)

            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("BROKEN: ./nested/CLAUDE.md", result.stdout)
            self.assertIn("2 CLAUDE.md files checked, 1 issues found", result.stdout)


class SessionStateTests(unittest.TestCase):
    def test_snapshot_paths_are_checkout_isolated_and_use_tmpdir(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            base = Path(temporary_dir)
            temp_root = base / "tmp"
            first = base / "first checkout"
            second = base / "second checkout"
            temp_root.mkdir()
            first.mkdir()
            second.mkdir()
            env = {"TMPDIR": str(temp_root), "USER": "same-user"}

            first_result = run_script("session-state.sh", "start", cwd=first, env=env)
            second_result = run_script("session-state.sh", "start", cwd=second, env=env)

            self.assertEqual(first_result.returncode, 0, first_result.stderr)
            self.assertEqual(second_result.returncode, 0, second_result.stderr)
            first_path = Path(first_result.stdout.splitlines()[0].removeprefix("snapshot written to "))
            second_path = Path(second_result.stdout.splitlines()[0].removeprefix("snapshot written to "))
            self.assertNotEqual(first_path, second_path)
            self.assertEqual(first_path.parent, temp_root)
            self.assertEqual(second_path.parent, temp_root)
            self.assertTrue(first_path.is_file())
            self.assertTrue(second_path.is_file())

    def test_diff_avoids_shared_now_file_and_reports_snapshot_time(self) -> None:
        source = (SCRIPTS / "session-state.sh").read_text(encoding="utf-8")
        self.assertNotIn("/tmp/craft-session-now.txt", source)

        with tempfile.TemporaryDirectory() as temporary_dir:
            project = Path(temporary_dir) / "checkout"
            temp_root = Path(temporary_dir) / "tmp"
            project.mkdir()
            temp_root.mkdir()
            env = {"TMPDIR": str(temp_root), "USER": "portable-user"}
            start = run_script("session-state.sh", "start", cwd=project, env=env)
            self.assertEqual(start.returncode, 0, start.stderr)

            result = run_script("session-state.sh", "diff", cwd=project, env=env)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("(snapshot at:", result.stdout)
            self.assertFalse((temp_root / "craft-session-now.txt").exists())

    def test_same_checkout_supports_overlapping_named_sessions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            project = Path(temporary_dir) / "checkout"
            temp_root = Path(temporary_dir) / "tmp"
            project.mkdir()
            temp_root.mkdir()
            env = {"TMPDIR": str(temp_root), "USER": "same-user"}

            first = run_script("session-state.sh", "start", "first/session", cwd=project, env=env)
            second_env = dict(env, CRAFT_SESSION_ID="second session")
            second = run_script("session-state.sh", "start", cwd=project, env=second_env)

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            first_path = Path(first.stdout.splitlines()[0].removeprefix("snapshot written to "))
            second_path = Path(second.stdout.splitlines()[0].removeprefix("snapshot written to "))
            self.assertNotEqual(first_path, second_path)
            self.assertTrue(first_path.is_file())
            self.assertTrue(second_path.is_file())
            self.assertNotIn("/", first_path.name)

            first_diff = run_script("session-state.sh", "diff", "first/session", cwd=project, env=env)
            second_diff = run_script("session-state.sh", "diff", cwd=project, env=second_env)
            self.assertEqual(first_diff.returncode, 0, first_diff.stdout + first_diff.stderr)
            self.assertEqual(second_diff.returncode, 0, second_diff.stdout + second_diff.stderr)

            source = (SCRIPTS / "session-state.sh").read_text(encoding="utf-8")
            self.assertIn("mktemp", source)
            self.assertNotIn('SNAPSHOT}.tmp', source)


if __name__ == "__main__":
    unittest.main()
