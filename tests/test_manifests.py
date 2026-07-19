#!/usr/bin/env python3
"""Keep Craft's plugin metadata aligned with the shipped package."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.2.0"
PLUGIN_NAME = "craft"
SKILL_COUNT = 9
HELPER_COUNT = 14
SKILL_NAMES = {
    "activate",
    "board",
    "compose",
    "context",
    "discuss",
    "distill",
    "enhance",
    "present",
    "reconsider",
}


def load_json(relative_path: str) -> dict:
    with (ROOT / relative_path).open(encoding="utf-8") as handle:
        return json.load(handle)


class ManifestTests(unittest.TestCase):
    def test_plugin_identity_and_version_agree(self) -> None:
        codex = load_json(".codex-plugin/plugin.json")
        claude = load_json(".claude-plugin/plugin.json")
        marketplace = load_json(".claude-plugin/marketplace.json")
        listing = marketplace["plugins"][0]

        for manifest in (codex, claude, listing):
            self.assertEqual(manifest["name"], PLUGIN_NAME)
            self.assertEqual(manifest["version"], VERSION)

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
        self.assertIn("9 user-facing skills", claude)
        self.assertIn("14 helper profiles", claude)

    def test_public_installation_guidance_is_accurate(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Plugin Directory", readme)
        self.assertIn("/plugin marketplace add", readme)
        self.assertIn("/plugin install", readme)
        self.assertNotIn("codex plugin", readme.lower())


if __name__ == "__main__":
    unittest.main()
