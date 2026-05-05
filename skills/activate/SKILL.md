---
name: activate
description: "Quick session start. Alias for /craft:distill --begin: git state + recon + CLAUDE.md audit + briefing."
allowed-tools: Read, Grep, Glob, Bash, Agent
---

# /craft:activate

Routes to the `distill` skill with `--begin` mode. The fast on-ramp for starting a craft session.

See `skills/distill/SKILL.md` for the full procedure. This skill exists for ergonomics — easier to type and tab-complete than `/craft:distill --begin`.

## Procedure

1. Run `bash ${CLAUDE_PLUGIN_ROOT}/scripts/session-state.sh start` to capture git state.
2. Launch `craft-scout` to recon recent changes and project context.
3. Read project `CLAUDE.md` if present; flag staleness.
4. Produce a session briefing: what's open, what's blocked, what to do first.

## Handoffs

`/craft:context` for a deeper CLAUDE.md hierarchy refresh. `/craft:discuss --plan` to plan the session work. `/craft:compose` to start building. `/craft:present save` for mid-session checkpoint, `/craft:present wrap` at the end.
