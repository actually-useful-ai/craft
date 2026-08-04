#!/usr/bin/env python3
"""Regression coverage for Craft's bundled capability routing."""

from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CapabilityRoutingTests(unittest.TestCase):
    def test_every_work_phase_loads_the_shared_contract(self) -> None:
        for name in ("activate", "discuss", "compose", "distill", "reconsider", "present"):
            content = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("../capability-routing.md", content, name)

    def test_contract_preserves_role_ownership_and_provider_boundaries(self) -> None:
        contract = (ROOT / "skills/capability-routing.md").read_text(encoding="utf-8")
        for role in ("Executor", "Overlay", "Governor", "Auditor"):
            self.assertIn(f"**{role}:**", contract)
        for capability in (
            "ask", "chefs-choice", "exemplar", "horizon", "skill-auditor",
            "skill-creator", "swarm",
        ):
            self.assertIn(f"`{capability}`", contract)
        for provider in ("Intentional UX", "Accessibility", "Humanize"):
            self.assertIn(provider, contract)
        self.assertIn("Use one primary executor", contract)
        self.assertIn("Never stack skills ceremonially", contract)
        self.assertIn("independently versioned", contract)
        self.assertIn("disclosure and spend boundary", contract)
        self.assertIn("does not authorize a call", contract)

    def test_capability_entry_points_are_wired_to_workflow_modes(self) -> None:
        compose = (ROOT / "skills/compose/SKILL.md").read_text(encoding="utf-8")
        distill = (ROOT / "skills/distill/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("| `skill` |", compose)
        self.assertIn("bundled `skill-creator`", compose)
        self.assertIn("| `--skills` |", distill)
        self.assertIn("bundled `skill-auditor`", distill)
        self.assertIn("Do not edit caches", distill)

    def test_exemplar_trigger_boundaries_survive_the_move(self) -> None:
        exemplar = (ROOT / "skills/exemplar/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("impress me", exemplar.lower())
        self.assertIn("do not trigger for routine polish or mechanical edits", exemplar)
        self.assertIn("Chef’s Choice selects useful capabilities", exemplar)
        self.assertIn("Intentional UX owns", exemplar)
        self.assertIn("Humanize owns", exemplar)

    def test_scenario_fixture_covers_activation_composition_and_fallback(self) -> None:
        fixture = (ROOT / "tests/capability-routing-scenarios.md").read_text(
            encoding="utf-8"
        )
        normalized = " ".join(fixture.split())
        for heading in (
            "Positive activation",
            "Negative activation",
            "Composition",
            "Missing provider",
            "External domain boundary",
            "External consultation boundary",
            "Horizon boundary",
            "Swarm boundary",
        ):
            self.assertIn(f"## {heading}", fixture)
        self.assertIn("one primary executor", normalized)
        self.assertIn("does not activate Exemplar", normalized)
        self.assertIn("Accessibility remains independently versioned", normalized)
        self.assertIn("zero outside-model calls", normalized)
        self.assertIn("one bounded call", normalized)
        self.assertIn("exactly four Luna calls", normalized)
        self.assertIn("zero outside calls", normalized)


if __name__ == "__main__":
    unittest.main()
