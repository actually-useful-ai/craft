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
            "ask", "chefs-choice", "impress", "horizon", "skill-auditor",
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

    def test_chaos_has_a_narrow_trigger_and_non_impersonating_fallback(self) -> None:
        contract = (ROOT / "skills/capability-routing.md").read_text(encoding="utf-8")
        normalized = " ".join(contract.split())

        self.assertIn("**Chaos:**", contract)
        self.assertIn("explicitly requested", normalized)
        self.assertIn("deliberately playful constraint or remix", normalized)
        for excluded_trigger in (
            "chef's choice",
            "impress me",
            "ordinary brainstorming",
            "a request that merely contains the word",
        ):
            self.assertIn(excluded_trigger, normalized)
        self.assertIn("one bounded, reversible creative constraint", normalized)
        self.assertIn("must not claim to have invoked Chaos", normalized)

    def test_platforms_owns_delivery_without_stacking_or_overclaiming(self) -> None:
        contract = (ROOT / "skills/capability-routing.md").read_text(encoding="utf-8")
        normalized = " ".join(contract.split())

        self.assertIn("**Platforms:**", contract)
        self.assertIn("platform-delivery work", normalized)
        self.assertIn("top-level Platforms capability", normalized)
        self.assertIn("does not stack a Platforms subskill", normalized)
        self.assertIn("Accessibility remains authoritative", normalized)
        self.assertIn("Intentional UX remains authoritative", normalized)
        self.assertIn("platform-neutral delivery plan", normalized)
        self.assertIn("package-specific validation was unavailable", normalized)
        self.assertIn("ordinary app or website work", normalized)
        self.assertIn("packaging, release, store, device, or channel-delivery lifecycle", normalized)

    def test_provider_selection_never_expands_authorization(self) -> None:
        contract = (ROOT / "skills/capability-routing.md").read_text(encoding="utf-8")
        normalized = " ".join(contract.split())

        self.assertIn("cannot edit, commit, or push the Chaos deck", normalized)
        self.assertIn("separate authorization", normalized)
        self.assertIn("does not authorize an outside call, commit, or push", normalized)
        self.assertIn("does not authorize publishing, deployment, account changes, or store submission", normalized)

    def test_experience_review_contract_preserves_domain_evidence(self) -> None:
        path = ROOT / "skills/experience-review.md"
        self.assertTrue(path.is_file())
        review = path.read_text(encoding="utf-8")
        normalized = " ".join(review.split())

        for owner in ("Intentional UX", "Accessibility", "Mobile", "Humanize", "Craft"):
            self.assertIn(owner, review)
        for field in (
            "task tuple",
            "state transition",
            "input mode",
            "manual check",
            "due date",
            "what would change confidence",
            "dissent",
        ):
            self.assertIn(field, normalized.lower())
        for provenance in ("`Measured`", "`Observed`", "`Assumed`"):
            self.assertIn(provenance, review)
        for handoff in ("`Done`", "`Evidence`", "`Open`", "`Next`"):
            self.assertIn(handoff, review)
        self.assertIn("at least two evidence domains", normalized)
        self.assertIn("IDs must be unique", review)
        self.assertIn("must resolve to an existing task tuple", normalized)
        self.assertIn("declared counts must match", normalized.lower())
        self.assertIn("at least one declared manual check", normalized)
        self.assertIn("portable report record", normalized)
        self.assertIn("persist it as a durable report artifact", normalized)
        self.assertIn("authorized repository path", normalized)
        self.assertIn("mark artifact persistence `Open`", normalized)
        self.assertIn("caller-owned persistence step", normalized)
        self.assertIn("Do not describe the inline record as a durable artifact", normalized)
        self.assertIn("No aggregate score", review)
        self.assertIn("No pass badge", review)
        self.assertIn("No WCAG-conformance verdict", review)
        self.assertIn("No release-readiness claim", review)
        self.assertIn("cannot promote", normalized)
        for required in (
            "accessibility report reference",
            "finding count",
            "manual-check count",
            "owner",
            "environment",
            "status",
            "evidence",
            "not-applicable justification",
            "target route or component",
            "documentation source references",
            "causal evidence",
            "confidence",
            "trade-off",
            "remediation",
            "verification method",
        ):
            self.assertIn(required, normalized.lower())

    def test_capability_entry_points_are_wired_to_workflow_modes(self) -> None:
        compose = (ROOT / "skills/compose/SKILL.md").read_text(encoding="utf-8")
        distill = (ROOT / "skills/distill/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("| `skill` |", compose)
        self.assertIn("bundled `skill-creator`", compose)
        self.assertIn("| `--skills` |", distill)
        self.assertIn("bundled `skill-auditor`", distill)
        self.assertIn("Do not edit caches", distill)

    def test_compose_requires_observable_feedback_for_user_visible_work(self) -> None:
        compose = (ROOT / "skills" / "compose" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        normalized = " ".join(compose.split())

        self.assertIn("render or run the user-visible result", normalized)
        self.assertIn("representative viewport and input state", normalized)
        self.assertIn("screenshot or equivalent observable output", normalized)
        self.assertIn("iterate from what was observed", normalized)
        self.assertIn("label visual verification `Unavailable`", normalized)
        self.assertIn("concurrent writers", normalized)
        self.assertIn("isolated worktrees or equivalent isolated checkouts", normalized)
        self.assertIn("low-blast-radius exception", normalized)

    def test_impress_trigger_boundaries_survive_the_move(self) -> None:
        impress = (ROOT / "skills/impress/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("impress me", impress.lower())
        self.assertIn("do not trigger for routine polish or mechanical edits", impress)
        self.assertIn("Chef’s Choice selects useful capabilities", impress)
        self.assertIn("Intentional UX owns", impress)
        self.assertIn("Humanize owns", impress)

    def test_impress_critique_is_bounded_and_routes_structural_review(self) -> None:
        impress = (ROOT / "skills/impress/SKILL.md").read_text(encoding="utf-8")
        normalized = " ".join(impress.split())

        for heading in (
            "### Merely competent",
            "### Exemplar opportunities",
            "### Performative sophistication",
        ):
            self.assertIn(heading, impress)
        self.assertIn("Do not apply the changes", impress)
        self.assertIn("one or two smallest changes", normalized)
        for mode in ("`--validate`", "`--rebuild`", "`--blast`"):
            self.assertIn(mode, impress)
        self.assertIn("begin the response exactly with `### Merely competent`", normalized)
        self.assertIn("Do not add a preface", impress)
        self.assertIn("append at most one final line", normalized)
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
            "Chaos boundary",
            "Platforms boundary",
            "Experience Review boundary",
        ):
            self.assertIn(f"## {heading}", fixture)
        self.assertIn("one primary executor", normalized)
        self.assertIn("does not activate Exemplar", normalized)
        self.assertIn("Accessibility remains independently versioned", normalized)
        self.assertIn("zero outside-model calls", normalized)
        self.assertIn("one bounded call", normalized)
        self.assertIn("exactly four Luna calls", normalized)
        self.assertIn("zero outside calls", normalized)
        self.assertIn("does not authorize editing, committing, or pushing the deck", normalized)
        self.assertIn("does not stack a platform subskill", normalized.lower())
        self.assertIn("does not activate Platforms for ordinary app or website work", normalized)
        self.assertIn(
            "Missing-provider prompt: `Prepare this app for mobile and TV delivery with Platforms.`, with Platforms absent.",
            normalized,
        )
        self.assertIn("no aggregate score", normalized.lower())
        self.assertIn("Semantic predictions remain `Planned`", normalized)


if __name__ == "__main__":
    unittest.main()
