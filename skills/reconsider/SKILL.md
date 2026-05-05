---
name: reconsider
description: "Challenge assumptions, validate, rebuild from scratch, or assess blast radius. The challenge phase of craft. Replaces /doublecheck, /thinkagain, /foresight."
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

### `--validate` (correctness check)
1. **Run tests** — if a test runner is configured, execute relevant tests.
2. **Type-check** — for typed languages, run the type checker.
3. **Audit** — `craft-validator` reviews for findings-first issues: type errors, broken contracts, missing edge cases, config drift.
4. **Critic pass** — `craft-critic` looks for UX and architecture issues.
5. Output findings prioritized by severity (fatal/wounding/uncomfortable/cosmetic).

### `--rebuild` (first-principles reconsider)
1. **Discard the frame** — explicitly list assumptions of the current approach.
2. **Re-derive** — `craft-planner` builds the plan from scratch, ignoring the existing implementation.
3. **Compare** — diff the rebuilt approach against current. Note where they agree and diverge.
4. **Recommend** — keep current, partial rewrite, or full rebuild, with reasoning.

### `--blast` (impact analysis)
1. **Find the surface** — for the named symbol/file/module, identify all imports, call sites, and references via grep.
2. **Trace configs** — find environment-variable, config-file, and CLAUDE.md references.
3. **Map dependents** — list every module that would need to change if this surface changes.
4. **Score severity** — for each downstream caller, rate the impact of the proposed change.
5. **Output** — a blast radius report with severity-sorted dependent list.

## Output

Report to `~/craft/reports/by-date/YYYY-MM-DD/reconsider-<topic>.md`. Severity-sorted findings inline.

## Handoffs

`/craft:compose --surgical` for targeted fixes after `--validate`. `/craft:discuss --plan` for full rebuilds after `--rebuild`. `/craft:distill --conclude` if reconsider closes the loop.

## Anti-patterns

- Running `--validate` without tests existing — that's an audit, not a validation.
- `--rebuild` without genuine reasons to discard the frame; cheap iteration is /craft:discuss.
- `--blast` on a non-shared change; pure overhead.
