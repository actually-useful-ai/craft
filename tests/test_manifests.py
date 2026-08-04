#!/usr/bin/env python3
"""Keep Craft's plugin metadata aligned with the shipped package."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.7.0"
PLUGIN_NAME = "craft"
SKILL_COUNT = 16
HELPER_COUNT = 14
SKILL_NAMES = {
    "activate",
    "ask",
    "board",
    "chefs-choice",
    "compose",
    "context",
    "discuss",
    "distill",
    "enhance",
    "exemplar",
    "horizon",
    "present",
    "reconsider",
    "skill-auditor",
    "skill-creator",
    "swarm",
}


def load_json(relative_path: str) -> dict:
    with (ROOT / relative_path).open(encoding="utf-8") as handle:
        return json.load(handle)


class ManifestTests(unittest.TestCase):
    def test_plugin_identity_and_version_agree(self) -> None:
        codex = load_json(".codex-plugin/plugin.json")
        cursor = load_json(".cursor-plugin/plugin.json")
        claude = load_json(".claude-plugin/plugin.json")
        marketplace = load_json(".claude-plugin/marketplace.json")
        listing = marketplace["plugins"][0]

        for manifest in (codex, cursor, claude, listing):
            self.assertEqual(manifest["name"], PLUGIN_NAME)
            self.assertEqual(manifest["version"], VERSION)

        for manifest in (codex, cursor, claude):
            self.assertEqual(manifest["skills"], "./skills/")
            self.assertEqual(manifest["author"]["name"], "Luke Steuber")
            for field in (
                "description",
                "homepage",
                "repository",
                "license",
                "keywords",
            ):
                self.assertEqual(manifest[field], claude[field])

    def test_codex_manifest_declares_skills_and_interface(self) -> None:
        codex = load_json(".codex-plugin/plugin.json")
        self.assertEqual(codex["skills"], "./skills/")

        interface = codex["interface"]
        required = {
            "displayName",
            "shortDescription",
            "longDescription",
            "developerName",
            "category",
            "capabilities",
            "defaultPrompt",
        }
        self.assertTrue(required.issubset(interface))
        self.assertEqual(interface["developerName"], "Luke Steuber")
        self.assertIsInstance(interface["defaultPrompt"], list)
        self.assertGreater(len(interface["defaultPrompt"]), 0)
        self.assertLessEqual(len(interface["defaultPrompt"]), 3)
        self.assertTrue(all(len(prompt) <= 128 for prompt in interface["defaultPrompt"]))

    def test_shipped_component_counts_match_documentation(self) -> None:
        skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
        helpers = sorted((ROOT / "agents").glob("*.md"))
        self.assertEqual(len(skills), SKILL_COUNT)
        self.assertEqual({path.parent.name for path in skills}, SKILL_NAMES)
        self.assertEqual(len(helpers), HELPER_COUNT)

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("9 workflow entry points", readme)
        self.assertIn("14 optional helper profiles", readme)
        self.assertIn("9 workflow entry points and 7 bundled capability skills", claude)
        self.assertIn("14 helper profiles", claude)

    def test_bundled_capability_license_is_declared(self) -> None:
        codex = load_json(".codex-plugin/plugin.json")
        claude = load_json(".claude-plugin/plugin.json")
        self.assertEqual(codex["license"], "MIT AND Apache-2.0")
        self.assertEqual(claude["license"], "MIT AND Apache-2.0")
        self.assertTrue((ROOT / "skills/skill-creator/LICENSE.txt").is_file())

    def test_public_installation_guidance_is_accurate(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Plugin Directory", readme)
        self.assertIn("/plugin marketplace add", readme)
        self.assertIn("/plugin install", readme)
        self.assertNotIn("codex plugin", readme.lower())

    def test_bundled_script_paths_are_host_neutral(self) -> None:
        scripted_skills = ("activate", "ask", "board", "context", "distill", "swarm")
        for skill_name in scripted_skills:
            content = (ROOT / "skills" / skill_name / "SKILL.md").read_text(
                encoding="utf-8"
            )
            self.assertNotIn("${CLAUDE_PLUGIN_ROOT}/scripts", content)
            self.assertIn("CRAFT_PLUGIN_ROOT", content)

        resolver = " ".join(
            (ROOT / "skills" / "script-paths.md").read_text(encoding="utf-8").split()
        )
        self.assertIn("Claude Code", resolver)
        self.assertIn("Codex", resolver)
        self.assertIn("loaded `SKILL.md`", resolver)
        self.assertIn("Do not resolve bundled scripts from the project working directory", resolver)

    def test_validator_profile_has_no_private_host_assumptions(self) -> None:
        validator = (ROOT / "agents" / "craft-validator.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("~/service_manager.py", validator)
        self.assertNotIn("| API_KEY |", validator)
        self.assertNotIn("| DB_URL |", validator)

    def test_helper_profiles_have_a_codex_fallback(self) -> None:
        resolver_path = ROOT / "skills" / "helper-profiles.md"
        self.assertTrue(resolver_path.is_file(), "missing Codex helper-profile fallback")
        resolver = " ".join(resolver_path.read_text(encoding="utf-8").split())
        self.assertIn("Codex", resolver)
        self.assertIn("general subagent", resolver)
        self.assertIn("agents/", resolver)
        self.assertIn("Do not assume", resolver)

        for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
            content = path.read_text(encoding="utf-8")
            if "craft-" in content and path.parent.name != "enhance":
                self.assertIn("../helper-profiles.md", content, path.as_posix())


if __name__ == "__main__":
    unittest.main()
