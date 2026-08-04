---
name: distill
description: "Refine code, audit quality or skill fleets, capture reusable patterns, and manage session hygiene. Use for cleanup, read-only audits, capability drift, or session begin/end."
allowed-tools: Read, Grep, Glob, Bash, Edit, Agent
---

# /craft:distill

Refine and clean. This is the hygiene phase (`discuss → compose → distill → reconsider → present`).

## Modes

| Mode | When to use |
|------|-------------|
| `--full` (default) | Full hygiene pass: harvest reusable patterns, clean cruft, audit code, organize. |
| `--audit` | Quality audit only — identify issues, don't fix them. |
| `--skills` | Read-only audit of skills, plugins, active versions, routing, and source/install drift. |
| `--begin` | Session start: git state, recon, CLAUDE.md audit, briefing. |
| `--conclude` | Session end: commit, harvest, document next steps, final report. |

## Procedure

Resolve `CRAFT_PLUGIN_ROOT` with [the shared script-path rule](../script-paths.md)
before running a bundled script.
Use the [helper-profile fallback](../helper-profiles.md) for each named review
role the host does not expose directly.
Use the [capability routing contract](../capability-routing.md) when the audit
involves installed capabilities or composition behavior.
Carry the shared [evidence envelope](../evidence-envelope.md); preserve source,
install, and runtime evidence as separate claims.

### `--begin` (session start)
1. Run `bash "$CRAFT_PLUGIN_ROOT/scripts/session-state.sh" start` to capture git state.
2. Launch `craft-scout` to recon recent changes and project context.
3. Read project `CLAUDE.md` if present; flag staleness.
4. Produce a session briefing: what's open, what's blocked, what to do first.

### `--full` (default hygiene pass)
1. **Harvest**: `bash "$CRAFT_PLUGIN_ROOT/scripts/harvest.sh"` captures reusable snippets and patterns in `~/SNIPPETS/`.
2. **Janitor**: `craft-janitor` detects agent-generated cruft (CRITIC.md, REPO_AUDIT.md, *_STATUS.md, .aider.*), unused dependencies, and dead code branches.
3. **Audit**: `craft-validator` surfaces code quality issues such as long functions, duplicate logic, and missing tests.
4. Output findings, propose fixes, apply with confirmation.

### `--audit` (read-only)
Skip steps 1 and 4. Findings only.

### `--skills` (read-only capability audit)
1. Route to the bundled `skill-auditor` skill.
2. Map canonical repositories, active installations, caches, projections,
   symlinks, versions, and hashes before interpreting drift.
3. Audit manifests, references, trigger collisions, role ownership, fallbacks,
   and source/install parity without editing any target.
4. Report the smallest source-level remediation plan. Do not edit caches,
   installations, or source while the auditor is active.

### `--conclude` (session end)
1. Verify state: run `bash "$CRAFT_PLUGIN_ROOT/scripts/session-state.sh" end`.
2. Harvest new snippets generated this session.
3. Document next steps to `~/craft/status/<project>-next-YYYY-MM-DD.md`.
4. Update accumulated recommendations at `~/craft/recommendations/by-project/<project>.md` (append, never delete).
5. If you have uncommitted changes, verify the state and then commit under the git safety protocol.
6. Close with the evidence-envelope handoff (`Done`, `Evidence`, `Open`,
   `Next`) and a truthful `Done`, `Partial`, or `Blocked` status.

## Output paths

- Reports: `~/craft/reports/by-date/YYYY-MM-DD/distill-<project>.md`
- Recommendations: `~/craft/recommendations/by-project/<project>.md` (append-only)
- Status: `~/craft/status/<project>-<phase>-YYYY-MM-DD.md`
- Snippets: `~/SNIPPETS/` (the cross-project archive)

## Handoffs

`/craft:reconsider` to challenge findings. `/craft:compose skill` to act on an
approved skill remediation plan. `/craft:present` after `--conclude`.

## Anti-patterns

- Running `--full` on a dirty working tree without committing first.
- Treating `--audit` findings as actionable without follow-up.
- Forgetting `--conclude` at session end; recommendations get lost.
