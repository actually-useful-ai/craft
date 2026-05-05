---
name: distill
description: "Refine code, audit quality, capture reusable patterns. Hygiene phase of craft. Replaces /harvest, /janitor, plus session begin/end."
allowed-tools: Read, Grep, Glob, Bash, Edit, Agent
---

# /craft:distill

Refine and clean. This is the hygiene phase (`discuss → compose → distill → reconsider → present`).

## Modes

| Mode | When to use |
|------|-------------|
| `--full` (default) | Full hygiene pass: harvest reusable patterns, clean cruft, audit code, organize. |
| `--audit` | Quality audit only — identify issues, don't fix them. |
| `--begin` | Session start: git state, recon, CLAUDE.md audit, briefing. |
| `--conclude` | Session end: commit, harvest, document next steps, final report. |

## Procedure

### `--begin` (session start)
1. Run `bash scripts/session-state.sh start` to capture git state.
2. Launch `craft-scout` to recon recent changes and project context.
3. Read project `CLAUDE.md` if present; flag staleness.
4. Produce a session briefing: what's open, what's blocked, what to do first.

### `--full` (default hygiene pass)
1. **Harvest** — `bash scripts/harvest.sh` to capture reusable snippets and patterns to `~/SNIPPETS/`.
2. **Janitor** — `craft-janitor` agent: detect agent-generated cruft (CRITIC.md, REPO_AUDIT.md, *_STATUS.md, .aider.*), unused dependencies, dead code branches.
3. **Audit** — `craft-validator` agent: surface code quality issues (long functions, duplicate logic, missing tests).
4. Output findings, propose fixes, apply with confirmation.

### `--audit` (read-only)
Skip steps 1 and 4. Findings only.

### `--conclude` (session end)
1. Verify state — run `bash scripts/session-state.sh end`.
2. Harvest new snippets generated this session.
3. Document next steps to `~/craft/status/<project>-next-YYYY-MM-DD.md`.
4. Update accumulated recommendations at `~/craft/recommendations/by-project/<project>.md` (append, never delete).
5. Commit if there are uncommitted changes (per git safety protocol — verify state first).

## Output paths

- Reports: `~/craft/reports/by-date/YYYY-MM-DD/distill-<project>.md`
- Recommendations: `~/craft/recommendations/by-project/<project>.md` (append-only)
- Status: `~/craft/status/<project>-<phase>-YYYY-MM-DD.md`
- Snippets: `~/SNIPPETS/` (the cross-project archive)

## Handoffs

`/craft:reconsider` to challenge findings. `/craft:present` after `--conclude`.

## Anti-patterns

- Running `--full` on a dirty working tree without committing first.
- Treating `--audit` findings as actionable without follow-up.
- Forgetting `--conclude` at session end; recommendations get lost.
