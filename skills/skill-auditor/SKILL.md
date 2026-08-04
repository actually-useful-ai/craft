---
name: skill-auditor
description: Audit skill catalogs and plugin packages for structural errors, routing ambiguity, portability problems, broken references, manifest drift, duplicate names, and source/install divergence. Use for skill or plugin audits and bulk-cleanup planning; remain read-only.
license: MIT
---

# Skill Auditor

Audit evidence before proposing changes. Never edit, install, delete, commit, or publish while this skill is active.

## Core rule

Separate invariants from house style. Do not report a field, heading, emoji, H1 wording, or example style as an error unless the selected runtime profile requires it.

Read [references/runtime-profiles.md](references/runtime-profiles.md) before interpreting frontmatter or packaging. Read [references/checks.md](references/checks.md) when explaining a finding or extending the auditor. Use [references/output-format.md](references/output-format.md) for reports.

## Scope

Resolve scope in this order:

1. Explicit skill file or package path.
2. Explicit catalog or plugin repository path.
3. Current repository when it contains skills or plugin manifests.
4. Configured user skill roots when the user requests a fleet audit.

Treat installed caches, generated projections, and vendored catalogs as runtime evidence—not as editable sources. Record their source commit or version when discoverable.

## Process

### 1. Map ownership first

For every root, record:

- canonical repository and remote;
- branch, commit, version, and dirty state;
- installed or projected paths by runtime and host;
- whether the path is source, generated install, cache, symlink, vendor copy, or intentional override.

Do not assume the most active or newest-looking directory is canonical.

### 2. Select runtime profiles

Detect `.codex-plugin`, `.claude-plugin`, and `.agents/plugins` metadata. When the package targets several runtimes, use the cross-runtime profile and evaluate runtime-specific fields only in their own context.

### 3. Run the deterministic audit

Use the bundled script:

```sh
python3 "$CRAFT_PLUGIN_ROOT/skills/skill-auditor/scripts/audit_skills.py" \
  <root> [<root> ...] --profile auto --format markdown
```

The script is read-only. It checks parsed Markdown links rather than treating every bare `*.md` token as a reference.

### 4. Review semantic findings

Inspect the descriptions and bodies for issues that syntax cannot prove reliably:

- trigger descriptions that are broad, ambiguous, or collide with another skill;
- executor, overlay, governor, and auditor roles that are conflated;
- named skills, agents, or tools with no availability check or fallback;
- unconditional overlays or reference loading that pollute every task;
- repeated boilerplate that belongs in one shared overlay;
- actions that exceed the user’s authorization;
- claims of validation without an observable acceptance condition;
- provider/model/version rosters duplicated as prose instead of generated or live-tested data.

### 5. Compare source and installations

Hash logical package contents while excluding managed cache metadata. Report:

- source ahead of installation;
- installation ahead of or divergent from source;
- several active versions of the same plugin;
- duplicate skill names resolved from different roots;
- broken or ambiguous marketplace source paths;
- missing runtime manifests when portability is claimed.

Never “fix” drift by editing a cache or projection.

### 6. Rank findings

- **Critical:** unsafe mutation behavior, secret exposure, unrecoverable source loss, or an invalid canonical package.
- **High:** broken activation or packaging, missing source of truth, broken references, an active stale install, or a name collision.
- **Medium:** portability, routing, maintainability, or reference-loading problem with a clear failure mode.
- **Low:** useful cleanup or a house-style inconsistency that does not block operation.

Suppress false positives and record why. If a rule is profile-specific, name the profile in the finding.

## Boundaries

- Never require `allowed-tools` universally.
- Never require a body activation section; descriptions are the primary trigger contract in current Agent Skills/Codex guidance.
- Never require the H1 slug to equal `name` unless a repository explicitly adopts that convention.
- Never require decorative good/bad markers.
- Keep Apple platform-version checks in an optional domain profile, not the universal core.
- Do not follow references more than one level from `SKILL.md` unless the entry file explicitly directs that load.
- Do not make network calls during a deterministic content audit. Use a separate source/install mapping phase when remote state matters.

## Verification

Run the same command twice and require identical report bodies. Spot-check every Critical/High category, at least five suppressed links, and at least five semantic routing findings before recommending bulk edits.
