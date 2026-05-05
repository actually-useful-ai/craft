---
name: context
description: "Deep project memory refresh: walk every CLAUDE.md, audit nav, flag staleness, and rebuild a coherent picture of the project before acting."
allowed-tools: Read, Grep, Glob, Bash
---

# /craft:context

Refresh the model's understanding of a project by walking the full CLAUDE.md hierarchy, validating navigation, and surfacing stale references.

Different from `/craft:distill --begin` (which produces a session briefing) and from Claude Code's built-in `/init` (which generates a CLAUDE.md from a fresh codebase). This is for projects that already have CLAUDE.md hierarchies and need them audited and absorbed.

## When to use

- Starting a long task in a project you haven't touched recently.
- After major refactors that may have broken cross-CLAUDE.md links.
- When you suspect the model's context is out of date.
- Before publishing or refactoring shared infrastructure.

## Procedure

1. **Find every CLAUDE.md**:
   ```
   find . -maxdepth 4 -name "CLAUDE.md" -not -path "./.git/*"
   ```

2. **Read them all** — root → subdirectories. Note the hierarchy.

3. **Validate navigation** via `bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate-nav.sh`:
   - Every CLAUDE.md links to its parent (if any) and major children.
   - Cross-references resolve to existing files.
   - No broken `[link](path)` paths.

4. **Audit staleness**:
   - Recent commits affecting files mentioned in CLAUDE.md.
   - Files referenced in CLAUDE.md that no longer exist.
   - Sections describing behavior that has clearly changed (heuristic — flag, don't auto-fix).

5. **Walk public surfaces** — for each entry point (CLI, HTTP, library exports), confirm the CLAUDE.md describes it accurately.

6. **Summarize** — produce a concise memory bundle:
   - Project purpose (one sentence).
   - Architecture (one paragraph).
   - Key files and what they do.
   - Open issues / TODOs / known broken bits.
   - Stale CLAUDE.md sections that need rewriting (with line numbers).

## Output

Stdout: the memory bundle. Optional archive at `~/craft/reports/by-date/YYYY-MM-DD/context-<project>.md`.

For very large projects (>100 source files), the output is a hierarchical summary, not a full enumeration. Use `--deep` flag if you want the full enumeration.

## Anti-patterns

- Running on a tiny project where reading the README is sufficient.
- Treating the staleness flags as auto-fixable — they need human review.
- Replacing `/craft:distill --begin` with this for routine session start; `/context` is heavier and slower.

## Handoffs

`/craft:discuss --plan` after a context refresh. `/craft:reconsider --blast` if the audit revealed risky shared code. `/craft:distill --audit` to act on stale CLAUDE.md sections.
