# craft v0.10.1

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

**Self-contained, no build step.** Skills are Markdown. Helper scripts need no
third-party packages on Python 3.11+; `fleet.py` also accepts `tomli` on older
controller interpreters.

- 9 workflow entry points and 7 bundled capability skills in `skills/<name>/SKILL.md`
- 14 helper profiles in `agents/`
- 16 root scripts plus 5 bundled skill-auditing and creation scripts
- Agent Plugins 1.0 portable metadata in root `plugin.json`, alongside the
  existing Claude, Codex, and Cursor projections

**No hard dependency** on another plugin. Craft discovers optional providers and
reports an explicit limitation when they are unavailable. The main workflow can
continue without them. Ask reports missing or failed native CLI routes without
substituting another provider or transport; continuing the workflow does not
count as obtaining the requested outside opinion.

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
| `ask.sh`, `ask-cli.py` | Native CLI consultation with explicit model provenance |
| `ask-legacy.sh` | Explicit OpenAI compatibility transport for Swarm |
| `swarm.py` | Bounded concurrent Luna scouts through the legacy transport |
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
- Keep optional infrastructure failures explicit. Ask never substitutes another
  provider or transport for a failed route; the main workflow remains usable.

## Multi-model strategy

| Environment | How second opinions work |
|---|---|
| CLI shell with codex/gemini/aider installed | `cli-invoke.sh` |
| Native Claude, Grok, Ollama, or Z.ai CLI | `/craft:ask` through `scripts/ask.sh` |
| Standalone client | Continue with the current model and note the missing second opinion |

## Relationship to other plugins

- `team`: council-style codebase assessment, committee reviews, and bounded
  second opinions. `/craft:discuss --debate` supports focused deliberation;
  Team owns its full council protocol and preserves dissent.
- `elegance`: code refinement and decision council. `/craft:reconsider --validate` for routine checks; `/elegance` for deep refinement with the 14-agent council.
- `intentional-ux`: independently versioned provider for task paths, interaction cost, recovery, and experience evidence. Craft routes relevant work to it when installed.
- `humanize`: independently versioned provider for meaning-preserving prose edits. Craft routes publishing prose to it when installed.
- `accessibility`: owns `/accessibility`, the dedicated WCAG plugin. `craft-a11y` agent does internal a11y checks during `compose` and `reconsider`; full audits go to `/accessibility`.
- `chaos`: optional explicit creative constraint or remix provider; selecting it
  never authorizes changes to its external deck.
- `platforms`: optional top-level platform-delivery executor that owns its own
  intake and sub-routing.
- `mobile`: independently versioned source of viewport, touch, motion, layout,
  and measured performance evidence.

Cross-domain reviews use `skills/experience-review.md`. Keep detailed provider
rules in `skills/capability-routing.md`; the phase skills already load that
shared contract and should not duplicate it.

## Bundled capability ownership

- `chefs-choice`: governor for resource selection and ambition.
- `ask`: executor for an outside-model answer or an advisory evidence provider after explicit authorization.
- `horizon`: deliberative executor for a compact pre-commit option set or a hypothesis provider to Discuss.
- `swarm`: executor for an explicitly authorized homogeneous Luna exploration or an advisory evidence provider.
- `impress`: overlay for the quality target and anti-performance filter.
- `skill-auditor`: read-only auditor behind `/craft:distill --skills`.
- `skill-creator`: executor behind `/craft:compose skill`.

These seven skills are canonical in Craft as of 0.10.1. Do not maintain editable
copies in another active plugin. Accessibility, Intentional UX, Humanize, Team,
and platform/domain skills remain independent providers.

## Development

The package has no build step. Run the complete Python suite and the shell
validators before release:

```sh
python3 -B -m unittest discover -s tests -v
bash tests/test_plugin_parity.sh
bash tests/validate-enhance.sh
```

The Python suite covers manifests, capability routing, native CLI consultation,
fleet checks, and utility scripts. These checks do not establish live provider
authentication or installed-runtime activation.

The banner script (`scripts/banner.sh`) uses `pyfiglet`, `toilet`, or `figlet`
when available and falls back to plain text.
