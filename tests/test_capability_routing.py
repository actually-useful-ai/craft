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
            self.assertIn("../evidence-envelope.md", content, name)

    def test_evidence_envelope_preserves_evidence_strength(self) -> None:
        envelope = (ROOT / "skills/evidence-envelope.md").read_text(
            encoding="utf-8"
        )
        for label in (
            "`Measured`",
            "`Observed`",
            "`Inferred`",
            "`Planned`",
            "`Unavailable`",
        ):
            self.assertIn(label, envelope)
        for status in ("`Done`", "`Partial`", "`Blocked`"):
            self.assertIn(status, envelope)
        self.assertIn("Never promote one class into another", envelope)
        for handoff in ("`Done`", "`Evidence`", "`Open`", "`Next`"):
            self.assertIn(handoff, envelope)

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

    def test_exemplar_critique_is_bounded_and_routes_structural_review(self) -> None:
        exemplar = (ROOT / "skills/exemplar/SKILL.md").read_text(encoding="utf-8")
        normalized = " ".join(exemplar.split())

        for heading in (
            "### Merely competent",
            "### Exemplar opportunities",
            "### Performative sophistication",
        ):
            self.assertIn(heading, exemplar)
        self.assertIn("Do not apply the changes", exemplar)
        self.assertIn("one or two smallest changes", normalized)
        for mode in ("`--validate`", "`--rebuild`", "`--blast`"):
            self.assertIn(mode, exemplar)
        self.assertIn("stop before revision unless revision was also authorized", normalized)

    def test_horizon_is_a_ranked_precommit_answer_not_generic_brainstorming(self) -> None:
        horizon = (ROOT / "skills/horizon/SKILL.md").read_text(encoding="utf-8")
        normalized = " ".join(horizon.split())

        self.assertIn("three to five possibilities", normalized)
        self.assertIn("at least one **Opportunity** and one **Blind spot**", normalized)
        self.assertIn("`Observed`", horizon)
        self.assertIn("`Inferred`", horizon)
        self.assertNotIn("`Speculative`", horizon)
        self.assertIn("Start with the ranked set", horizon)
        self.assertIn("End with exactly one experiment and one state-appropriate handoff", normalized)
        for handoff in ("/craft:discuss", "/craft:compose", "/craft:reconsider"):
            self.assertIn(handoff, horizon)
        self.assertIn("do not preface it with a generic restatement", normalized)

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
