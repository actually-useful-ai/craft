# Runtime profiles

## Universal Agent Skills core

Require:

- a directory containing `SKILL.md`;
- YAML frontmatter beginning on line one;
- a unique lowercase kebab-case `name`;
- a non-empty `description` that explains both capability and triggering context;
- a readable Markdown body.

Treat `scripts/`, `references/`, and `assets/` as conventional optional resources. Prefer direct references from `SKILL.md` and progressive disclosure.

Do not universally require `allowed-tools`, a body activation heading, an H1/name slug match, emoji examples, or one particular output template.

## Codex profile

- Apply the universal core.
- Treat `agents/openai.yaml` as optional presentation and policy metadata when used by the current package surface.
- Validate `.codex-plugin/plugin.json` as JSON when present.
- Resolve its `skills` path relative to the repository root.
- Treat legacy tool vocabularies as portability warnings, not schema errors.
- Do not inspect or edit managed `.system` skills or plugin caches as source.

## Claude Code profile

- Apply the universal core.
- Allow Claude-specific frontmatter and tool names when the package explicitly targets Claude Code.
- Validate `.claude-plugin/plugin.json` and marketplace metadata when present.
- Do not flag Claude-only agents, commands, or hooks merely because Codex cannot use them.
- If the package claims cross-runtime support, require a fallback or separate runtime projection for Claude-only behavior.

## Cross-runtime profile

- Apply the universal core once.
- Interpret runtime-specific fields only under the matching runtime.
- Require identical package identity where two manifests describe the same plugin: name, version, repository, and skills root.
- Allow different interface metadata and tool declarations where the runtimes differ.
- Flag absolute host paths, unavailable named dependencies, and copied provider/model tables unless a portability contract explains them.

## Repository policy overlay

A repository may add stricter house rules. Report them separately as `Policy`, not universal errors. Policy must be discoverable in repository guidance or auditor configuration; do not infer it from historical consistency alone.
