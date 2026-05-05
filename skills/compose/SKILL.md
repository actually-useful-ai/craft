---
name: compose
description: "Build the thing: viz, frontend, docs, flow, game, or surgical fix. The execution phase of craft."
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent
---

# /craft:compose

Build the thing. This is the execution phase (`discuss → compose → distill → reconsider → present`).

## Modes

| Mode | When to use |
|------|-------------|
| `viz` | Data visualization, charts, dashboards. Routes via `craft-design`. |
| `frontend` | UI components, pages, layouts. Touch accessibility and responsive design baked in. |
| `docs` | Generate or upgrade documentation. README, guides, reference. |
| `flow` | Workflow scaffolding, state machines, orchestration. |
| `game` | Game logic, prototypes, interactive demos. |
| `surgical` | Pinpoint edit on an existing file. Read full file → identify minimal change boundary → edit → verify. |

## How it picks

If input names a UI/component, `frontend`. If it mentions chart/graph/D3/dashboard, `viz`. If it asks for a README or guide, `docs`. If it's "fix this specific thing", `surgical`. If unclear, ask.

## Procedure

1. **Plan if needed** — for non-trivial builds, route through `/craft:discuss --plan` first.
2. **Set up working tree** — confirm git is clean for surgical mode (preflight gate).
3. **Build** — apply the mode-specific approach:
   - `viz`/`frontend`/`docs`/`flow`/`game`: launch `craft-design` for layout/structure, then implement.
   - `surgical`: read the full target file, identify the minimum-blast-radius boundary, make the edit, verify with tests if they exist.
4. **Verify** — run tests, type checks, or smoke checks appropriate to the mode.
5. **Hand off** — to `/craft:distill` for cleanup, or `/craft:reconsider` to challenge the result.

## Surgical mode (formerly /fix)

A protocol, not a vibe:

1. Read the entire target file. No skipping.
2. Identify the **minimum change boundary** — what's the smallest set of lines that make the bug fix or feature work?
3. Edit that boundary, nothing else.
4. Verify by running affected tests, then by reading the diff back.
5. If the diff includes anything outside the original boundary, undo and retry.

This protects against scope creep, accidental refactors, and the "while I'm here" pattern that turns a 3-line fix into a 200-line change.

## Output

Code edits applied to the working tree. For `--plan`-routed work, also a build summary at `~/craft/status/compose-<project>-YYYY-MM-DD.md`.

## Handoffs

`/craft:distill` to clean up the workspace and harvest reusable patterns. `/craft:reconsider --validate` to verify the build holds up. `/craft:present` to ship.

## Anti-patterns

- Using `surgical` mode on code you haven't read fully.
- Adding "while I'm here" changes outside the planned scope.
- Skipping tests because the change "looks obvious."
- Composing without a `/craft:discuss --plan` for non-trivial work.
