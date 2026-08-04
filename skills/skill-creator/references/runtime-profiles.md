# Runtime profiles

Start with the universal Agent Skills core: one package directory, `SKILL.md`, leading YAML frontmatter, a lowercase kebab-case `name`, a description that covers capability and trigger context, and a Markdown body. Use `scripts/`, `references/`, and `assets/` for progressive disclosure.

## Codex

- Keep `name` and `description` as the discovery contract.
- Add `agents/openai.yaml` only when current Codex presentation or policy metadata is needed.
- Package plugins with `.codex-plugin/plugin.json` and a valid `skills` path.
- Do not place user content under managed `.system` or plugin-cache roots.
- Treat legacy `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `Task`, `WebSearch`, and `WebFetch` vocabulary as non-portable unless the current host defines it.

## Claude Code

- Keep `name` and `description` as the discovery contract.
- Add Claude-specific tool policy, commands, agents, or hooks only where Claude Code owns the behavior.
- Package with `.claude-plugin/plugin.json` and marketplace metadata when distributed as a plugin.
- Provide a separate projection or explicit fallback for Claude-only capabilities when cross-runtime support is claimed.

## Cross-runtime

- Share the core workflow and references.
- Keep runtime manifests aligned on name, version, repository, license, and skills path.
- Allow runtime-specific interfaces and capability adapters.
- Detect optional capabilities before using them.
- Replace hardcoded home directories with discovered roots or host-local configuration.
- Verify each runtime resolves exactly one intended installation at the same source version.
