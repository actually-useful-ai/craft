---
name: activate
description: "Start and route a Craft session from the goal: inspect workspace state, discover relevant installed capabilities, select the smallest useful stack, and hand work to the right phase. Use at the beginning of a task or when the correct workflow or skill is unclear."
allowed-tools: Read, Grep, Glob, Bash, Agent
---

# /craft:activate

Start from the goal. Build enough workspace and capability context to choose the
right method, then continue into the appropriate Craft phase without requiring
the person to remember individual skill names.

Resolve `CRAFT_PLUGIN_ROOT` with [the shared script-path rule](../script-paths.md)
before running a bundled script.
Use the [helper-profile fallback](../helper-profiles.md) when the host does not
expose `craft-scout` as a named profile.
Follow the [capability routing contract](../capability-routing.md) when selecting
bundled skills or optional providers.
Start and carry the shared [evidence envelope](../evidence-envelope.md) across
the selected phases.

## Procedure

1. Run `bash "$CRAFT_PLUGIN_ROOT/scripts/session-state.sh" start` to capture git state.
2. Launch `craft-scout` to recon recent changes and project context.
3. Read project `CLAUDE.md` if present; flag staleness.
4. Inspect the active skill/plugin catalog and resolve relevant capability names,
   versions, and source/install state. Do not treat a cache or source checkout as
   active merely because it exists.
5. Identify the objective, deliverable, audience, constraints, and authorization.
6. Select one primary executor plus only the governors, overlays, auditors, and
   verification providers that materially change the task.
7. State the selected stack and its purpose in one concise line.
8. Produce the evidence-envelope phase handoff: `Done`, `Evidence`, `Open`, and
   `Next`, including which Craft phase should run first. Continue into that
   phase unless the request asks only for a briefing.

## Handoffs

`/craft:context` for a deeper CLAUDE.md hierarchy refresh. `/craft:discuss --plan` to plan the session work. `/craft:compose` to start building. `/craft:distill --skills` for a read-only capability fleet audit. `/craft:present save` for mid-session checkpoint, `/craft:present wrap` at the end.
