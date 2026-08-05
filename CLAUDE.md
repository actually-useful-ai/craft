# craft v0.7

Portable workflow and capability-routing package for Codex and Claude Code.
Five modal commands plus activation, board, context, prior-art research, and
seven bundled workflow capabilities are organized around the work cycle:

```
discuss → compose → distill → reconsider → present
 think      build    refine    challenge     ship
```

## Commands

| Command | Purpose | Modes |
|---|---|---|
| `/craft:discuss` | Deliberate, debate, plan, research | `--quick`, `--debate`, `--plan`, `--research` |
| `/craft:compose` | Build viz, frontends, docs, flows, games, skills, surgical fixes | `viz`, `frontend`, `docs`, `flow`, `game`, `skill`, `surgical` |
| `/craft:distill` | Hygiene: harvest, code/skill audits, session begin/end | `--full`, `--audit`, `--skills`, `--begin`, `--conclude` |
| `/craft:reconsider` | Validate, rebuild from first principles, blast-radius analysis | `--validate`, `--rebuild`, `--blast` |
| `/craft:present` | Save, ship, publish, PR, wrap | `save`, `ship`, `publish`, `pr`, `wrap` |
| `/craft:board` | Kanban for tracking work | `add`, `done`, `show` |
| `/craft:context` | Deep CLAUDE.md hierarchy refresh | (none) |
| `/craft:activate` | Start a focused session with repository context | (none) |
| `/craft:enhance` | Research local and current prior art before building | (none) |
| `/craft:ask` | Obtain one explicitly authorized outside-model opinion | (none) |
| `/craft:chefs-choice` | Select useful capabilities for an ambitious delegated approach | (none) |
| `/craft:impress` | Set an exceptional quality target without performative complexity | (none) |
| `/craft:horizon` | Surface consequential pre-commit ideas and blind spots | (none) |
| `/craft:skill-auditor` | Audit skills, plugins, and installations without editing them | (none) |
| `/craft:skill-creator` | Create or revise portable, tested skills and plugins | (none) |
| `/craft:swarm` | Run an explicitly authorized bounded Luna scout swarm | (none) |

## Architecture

**Self-contained, no build step.** Skills are Markdown with stdlib helper scripts.

- 9 workflow entry points and 7 bundled capability skills in `skills/<name>/SKILL.md`
- 14 helper profiles in `agents/`
- 14 root stdlib scripts plus 5 bundled skill-auditing and creation scripts

**No hard dependency** on another plugin. Craft discovers optional providers and
degrades with an explicit limitation. Where second-opinion or data-fetching
capability matters, scripts try configured CLI tools and provider surfaces, then
continue with the current runtime when none is available.

## Helper profiles

All prefixed `craft-`:

| Group | Agents |
|---|---|
| Deliberation | `craft-critic`, `craft-scout`, `craft-planner`, `craft-searcher`, `craft-fetcher` |
| Quality | `craft-a11y`, `craft-perf`, `craft-security`, `craft-validator` |
| Build/Ship | `craft-design`, `craft-repo`, `craft-janitor` |
| Utility | `craft-canary`, `craft-diag` |

## Scripts

All in `scripts/`, called from skills after resolving `CRAFT_PLUGIN_ROOT` with
`skills/script-paths.md`:

| Script | Purpose |
|---|---|
| `ask.sh` | Canonical outside-model consultation with explicit model provenance |
| `swarm.py` | Bounded concurrent Luna scout orchestration through `ask.sh` |
| `fleet.py` | Manifest-driven cross-host package, runtime, hash, and legacy-link verification |
| `llm-query.py` | Compatibility wrapper that delegates to `ask.sh` |
| `data-fetch.py` | 17 data sources (uses `~/shared/data_fetching` if present) |
| `analyze.py` | Code complexity, duplication detection (stdlib only) |
| `generate-board.py` | Kanban board HTML generator (stdlib only) |
| `cli-detect.sh` | Detect available CLI tools (codex, gemini, aider, cursor-agent) |
| `cli-invoke.sh` | Safe invocation of detected CLIs with timeouts and fallthrough |
| `harvest.sh` | Capture reusable snippets to `~/SNIPPETS/` |
| `session-state.sh` | Snapshot git state, dirty files, branch info at session boundaries |
| `validate-nav.sh` | Validate CLAUDE.md hierarchy: parent links, cross-refs, broken paths |

## Output paths

All under `~/craft/`:

- `reports/by-date/YYYY-MM-DD/`: discuss summaries, distill findings, reconsider analyses
- `recommendations/by-project/<project>.md`: accumulated recommendations (append-only)
- `status/`: session work logs
- `snippets/`: internal harvest staging (canonical archive remains `~/SNIPPETS/`)
- `logs/`: agent execution logs
- `board.json`: kanban state

Board HTML: `~/html/craft/board/index.html` (served via Caddy if configured).

## Conventions

- Agent IDs prefixed `craft-` (no collision with team's seats or elegance's agents)
- Use specific terms such as language model, model, or provider in output.
- Credit Luke Steuber, never a model or tool.
- Use "I" not "we" in generated content
- No `Co-Authored-By` in commits
- Keep entry skills concise; put detailed criteria and variants in one-level `references/` directories
- Capability roles are explicit: one executor, justified overlays/governors, and read-only auditors
- `skills/capability-routing.md` owns shared composition and fallback behavior
- All scripts try-then-degrade; nothing hard-depends on optional infrastructure

## Multi-model strategy

| Environment | How second opinions work |
|---|---|
| CLI shell with codex/gemini/aider installed | `cli-invoke.sh` |
| Configured outside provider or gateway | `/craft:ask` through `scripts/ask.sh` |
| Standalone client | Continue with the current model and note the missing second opinion |

## Relationship to other plugins

- `team`: council-style codebase-to-pitch. Different scope; team is for product/business pitches with adversarial review. Cross-link: `/craft:discuss --debate` is lighter-weight; `/team` is the heavyweight version.
- `elegance`: code refinement and decision council. `/craft:reconsider --validate` for routine checks; `/elegance` for deep refinement with the 14-agent council.
- `intentional-ux`: independently versioned provider for task paths, interaction cost, recovery, and experience evidence. Craft routes relevant work to it when installed.
- `humanize`: independently versioned provider for meaning-preserving prose edits. Craft routes publishing prose to it when installed.
- `accessibility`: owns `/accessibility`, the dedicated WCAG plugin. `craft-a11y` agent does internal a11y checks during `compose` and `reconsider`; full audits go to `/accessibility`.

## Bundled capability ownership

- `chefs-choice`: governor for resource selection and ambition.
- `ask`: executor for an outside-model answer or an advisory evidence provider after explicit authorization.
- `horizon`: deliberative executor for a compact pre-commit option set or a hypothesis provider to Discuss.
- `swarm`: executor for an explicitly authorized homogeneous Luna exploration or an advisory evidence provider.
- `impress`: overlay for the quality target and anti-performance filter.
- `skill-auditor`: read-only auditor behind `/craft:distill --skills`.
- `skill-creator`: executor behind `/craft:compose skill`.

These seven skills are canonical in Craft as of 0.7. Do not maintain editable
copies in another active plugin. Accessibility, Intentional UX, Humanize, Team,
and platform/domain skills remain independent providers.

## Development

The package has no build step. Edit the Markdown files directly and run `python3 tests/test_manifests.py` plus the shell validators before release. Banner script (`scripts/banner.sh`) uses `pyfiglet`, `toilet`, or `figlet` when available and falls back to plain text.
