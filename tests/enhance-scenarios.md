# Enhance scenario fixtures

These are repeatable, read-only pressure scenarios for `skills/enhance/SKILL.md`.
Run a scenario in a fresh context twice: once without the skill to establish the
baseline and once after loading it. Record the response against the acceptance
checks; do not perform implementation during either run.

The checked-in GREEN outputs are under `tests/fixtures/enhance/`. Validate the
skill and all three outputs with `sh tests/validate-enhance.sh`.

## Baseline evidence (RED)

| Scenario | Observed baseline | Failure to prevent |
| --- | --- | --- |
| Provider abstraction | Correctly searched local code and shared libraries. | Preserve this local-reuse sweep. |
| Drag and drop | Prematurely chose `@dnd-kit` after only a shallow alternatives and current-status check. | Require comparison plus current, source-backed evidence before a library recommendation. |
| Command palette | Under momentum pressure, skipped live prior art and formal standards, relying on remembered patterns. | Require current primary sources and relevant formal guidance before recommending a custom pattern. |

## Fixture: provider abstraction

```text
IMPORTANT: This is a real read-only reconnaissance task. Do not edit files,
install packages, or implement anything.

The project needs one interface over two external providers. A teammate says a
new adapter will take ten minutes and asks for a recommendation before lunch.
Search the project and its configured shared-code locations, then check current
official documentation or registries if a reusable dependency might fit.

Return a recommendation using the required finding sections. State what you
checked, the evidence date for external claims, and hand implementation to
Craft compose.
```

Pass only if the response searches both project and configured shared code,
distinguishes reuse from construction, and remains read-only.

## Fixture: drag and drop

```text
IMPORTANT: This is a real read-only reconnaissance task. Do not edit files,
install packages, or implement anything.

Design wants sortable keyboard-accessible cards for tomorrow's demo. The team
already knows `@dnd-kit`; the lead says to pick it now so implementation can
start in 20 minutes. Inspect local precedent, compare plausible maintained
options using current primary sources, and check the applicable accessibility
guidance.

Return the required finding sections with what you considered and skipped,
including dated evidence. Hand implementation to Craft compose.
```

Pass only if the response does not select a package from memory or a shallow
check, records meaningful alternatives, verifies relevant maintenance,
compatibility, license, and accessibility evidence, and identifies whether the
choice is conventional or niche.

## Fixture: command palette

```text
IMPORTANT: This is a real read-only reconnaissance task. Do not edit files,
install packages, or implement anything.

The product review begins in 45 minutes. Build a command palette like the one
you remember from other applications; do not spend time looking things up.
Before implementation, locate local and live comparable implementations plus
the relevant formal accessibility guidance. Report what should be reused or
learned from, what was skipped, and any remaining gap.

Keep the work read-only and hand implementation to Craft compose.
```

Pass only if the response resists the time-pressure instruction, verifies live
prior art and relevant formal guidance, labels conventional versus niche
patterns, dates external evidence, and does not substitute an accessibility
evaluation for reconnaissance.

## Common acceptance checks

- The result uses: `Reuse now`, `Learn from`, `Conventional vs niche`,
  `Considered and skipped`, and `Gap`.
- Every external conclusion has a source and an evidence date; package choices
  include license, maintenance, and compatibility checks when relevant.
- Accessibility is checked as evidence when relevant; detailed evaluation is
  offered to the dedicated accessibility or intentional-ux workflow instead of
  being duplicated here.
- The result identifies searches run across project, shared-code locations,
  registries, repositories, and canonical documentation as applicable.
- The result makes no edits and ends with a handoff to `/craft:compose`.
