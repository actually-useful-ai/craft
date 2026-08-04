---
name: reconsider
description: "Challenge assumptions, validate correctness, rebuild a plan from first principles, or assess blast radius. Use after a consequential decision or implementation needs independent scrutiny."
allowed-tools: Read, Grep, Glob, Bash, Agent, WebSearch
---

# /craft:reconsider

Challenge what was just decided or built. The phase that earns the others (`discuss → compose → distill → reconsider → present`).

## Modes

| Mode | When to use |
|------|-------------|
| `--validate` (default) | Verify correctness: tests, types, config, integration. (formerly /doublecheck) |
| `--rebuild` | Reconsider from first principles. Discard the current frame. (formerly /thinkagain) |
| `--blast` | Map blast radius before changing shared code. Trace imports, configs, CLAUDE.md refs. (formerly /foresight) |

## How it picks

If "is this correct?" → `--validate`. If "should we have done it differently?" → `--rebuild`. If "what breaks if we change this?" → `--blast`.

## Procedure

Use the [helper-profile fallback](../helper-profiles.md) for each named review
role the host does not expose directly.
Use the [capability routing contract](../capability-routing.md) to challenge
whether the selected executor, overlays, and fallbacks still match the goal.

### `--validate` (correctness check)
1. **Run tests**: execute relevant tests when the project configures a test runner.
2. **Type-check**: run the type checker for typed languages.
3. **Audit**: `craft-validator` reviews type errors, broken contracts, missing edge cases, and config drift.
4. **Critic pass**: `craft-critic` looks for UX and architecture issues.
5. **Composition check**: verify capability ownership, active source/version,
   authorization boundaries, and missing-provider fallbacks when applicable.
6. Output findings prioritized by severity (fatal/wounding/uncomfortable/cosmetic).

### `--rebuild` (first-principles reconsider)
1. **Discard the frame**: list the current approach's assumptions.
2. **Re-derive**: `craft-planner` builds the plan from scratch without the existing implementation.
3. **Compare**: diff the rebuilt approach against the current one. Note where they agree and diverge.
4. **Recommend**: keep the current approach, rewrite part of it, or rebuild it, with reasoning.

### `--blast` (impact analysis)
1. **Find the surface**: identify all imports, call sites, and references for the named symbol, file, or module.
2. **Trace configs**: find environment-variable, config-file, and CLAUDE.md references.
3. **Map dependents**: list every module that would need to change with this surface.
4. **Score severity**: rate the proposed change's impact on each downstream caller.
5. **Output**: write a blast-radius report with dependents sorted by severity.

## Output

Report to `~/craft/reports/by-date/YYYY-MM-DD/reconsider-<topic>.md`. Severity-sorted findings inline.

## Handoffs

`/craft:compose --surgical` for targeted fixes after `--validate`. `/craft:discuss --plan` for full rebuilds after `--rebuild`. `/craft:distill --conclude` if reconsider closes the loop.

## Anti-patterns

- Running `--validate` without tests existing — that's an audit, not a validation.
- `--rebuild` without genuine reasons to discard the frame; cheap iteration is /craft:discuss.
- `--blast` on a non-shared change; pure overhead.
