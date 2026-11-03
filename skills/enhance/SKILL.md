---
name: enhance
description: Use when prior art, reusable code, package selection, established patterns, comparable products, or current authoritative guidance could change a non-trivial decision, including store listings, product copy and other outward-facing text whose claims must match the product.
---

# Enhance

Read-only reconnaissance before construction. Find what is already proven,
separate it from novelty, and leave an evidence trail that makes the next build
decision reversible.

## Use for

- Requests to find prior art, libraries, comparable implementations, or
  standards.
- A non-trivial decision that might duplicate project or shared code.
- Package or interaction choices where remembered patterns could be stale.
- Outward-facing text, such as a store listing, product page, release note or
  tagline, where comparable pages and the platform's own rules should shape
  the wording and every claim must match what the product does.

Do not use it for implementation. Do not edit files, install packages, change
configuration, or make a selection irreversible. Hand construction to
`/craft:compose` after reporting findings.

## Reconnaissance

1. State the decision, constraints, and what reuse would mean.
2. Search local project code, tests, documentation, and configured shared-code
   locations for implementations, usages, and conventions. Discover shared-code
   roots from project instructions, configuration, environment references, and documentation;
   never assume a personal directory or machine layout.
3. Search current primary sources appropriate to the decision: package
   registries, upstream repositories, canonical documentation, and relevant
   formal standards. Use secondary sources only as leads, then verify the
   claim at its primary source.
4. Compare viable candidates. For each relevant candidate, record source and
   evidence date, then verify:
   - license and its fit for the project;
   - maintenance signals, such as recent releases or upstream activity;
   - compatibility with the target runtime, version, framework, and project
     constraints;
   - accessibility evidence and applicable formal guidance for user-facing or
     interactive work.

5. For outward-facing text, list every factual claim the text and its
   metadata make: features, controls and inputs, platforms, accessibility,
   licenses, credits and disclosures. Check each against the product's source,
   tests or a running build, and record it as confirmed, contradicted or
   unverified, with where you looked. A contradicted claim is a finding even
   when the wording is otherwise good. Comparable live pages and the
   platform's published listing rules replace package registries as the
   primary sources; the license, maintenance and compatibility checks become
   `not applicable` unless a dependency is in question.

Mark a check `not applicable` with a reason rather than implying it happened.
If a source cannot be verified, treat it as a lead—not a recommendation.

## Frame the result

Lead with the decision, then use every section below, including an explicit
empty result where needed.

### Reuse now

Local code or a verified dependency that fits. Name the location or package,
how it applies, and the evidence date.

### Learn from

Comparable code, documentation, or standards that should shape the approach
without being copied wholesale. State the lesson and source.

### Conventional vs niche

Label the established, broadly supported choice separately from a less common
or specialized alternative. Base the label on observed maintenance, adoption,
and authoritative guidance—not familiarity or search ranking.

### Considered and skipped

List meaningful candidates that were rejected, with the specific evidence-based
reason. Silence is not evidence that an alternative was considered.

### Gap

State what does not exist or remain uncertain, the smallest construction still
needed, and the assumption that must be validated. For outward-facing text,
list each contradicted or unverified claim here with the smallest correction,
and keep the owner's own wording wherever it is accurate.

## Boundaries and handoff

Keep findings factual and traceable; separate evidence from recommendation.
For a user-facing choice, offer the findings as input to a dedicated
accessibility or intentional-ux review when deeper evaluation is needed. Do
not duplicate either review's evaluation framework here.

End with the recommended next step for `/craft:compose`, including the selected
reuse target or gap and any validation still required. Text meant for a public
page goes back to its owner for approval before `/craft:present` publishes it.
