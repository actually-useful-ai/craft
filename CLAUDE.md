# craft v0.1

Workflow toolbelt for Claude Code. Five modal commands plus board and context, organized around the work cycle:

```
discuss → compose → distill → reconsider → present
 think      build    refine    challenge     ship
```

## Commands

| Command | Purpose | Modes |
|---|---|---|
| `/craft:discuss` | Deliberate, debate, plan, research | `--quick`, `--debate`, `--plan`, `--research` |
| `/craft:compose` | Build viz, frontends, docs, flows, games, surgical fixes | `viz`, `frontend`, `docs`, `flow`, `game`, `surgical` |
| `/craft:distill` | Hygiene: harvest, audit, session begin/end | `--full`, `--audit`, `--begin`, `--conclude` |
| `/craft:reconsider` | Validate, rebuild from first principles, blast-radius analysis | `--validate`, `--rebuild`, `--blast` |
| `/craft:present` | Save, ship, publish, PR, wrap | `save`, `ship`, `publish`, `pr`, `wrap` |
| `/craft:board` | Kanban for tracking work | `add`, `done`, `show` |
| `/craft:context` | Deep CLAUDE.md hierarchy refresh | (none) |

## Architecture

**Self-contained, pure markdown.** No build step. No Python package. Edit `.md` files directly.

- 7 commands (entry points in `commands/`)
- 7 skills (one per command in `skills/<name>/SKILL.md`)
- 14 specialized agents in `agents/`
- 9 stdlib scripts in `scripts/`

**No dependency** on any other plugin. Where second-opinion or data-fetching capability matters, scripts try CLI tools (codex, gemini, aider), fall through to MCP servers (`etiquette-providers` if installed), then to direct API calls, then degrade to Claude-only with a graceful note.

## Agents

All prefixed `craft-`:

| Group | Agents |
|---|---|
| Deliberation | `craft-critic`, `craft-scout`, `craft-planner`, `craft-searcher`, `craft-fetcher` |
| Quality | `craft-a11y`, `craft-perf`, `craft-security`, `craft-validator` |
| Build/Ship | `craft-design`, `craft-repo`, `craft-janitor` |
| Utility | `craft-canary`, `craft-diag` |

## Scripts

All in `scripts/`, called from skills via `${CLAUDE_PLUGIN_ROOT}/scripts/`:

| Script | Purpose |
|---|---|
| `llm-query.py` | Multi-LLM second opinions (uses `~/shared/llm_providers` if present) |
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

- `reports/by-date/YYYY-MM-DD/` — discuss summaries, distill findings, reconsider analyses
- `recommendations/by-project/<project>.md` — accumulated recommendations (append-only)
- `status/` — session work logs
- `snippets/` — internal harvest staging (canonical archive remains `~/SNIPPETS/`)
- `logs/` — agent execution logs
- `board.json` — kanban state

Board HTML: `~/html/craft/board/index.html` (served via Caddy if configured).

## Conventions

- Agent IDs prefixed `craft-` (no collision with team's seats or elegance's agents)
- No "AI" terminology in any output (the project's humanize gate applies)
- Credit Luke Steuber, never "Claude" or "AI"
- Use "I" not "we" in generated content
- No `Co-Authored-By` in commits
- Skills under 2,000 tokens; heavy reference material goes in `references/` subdirectories (none yet)
- All scripts try-then-degrade; nothing hard-depends on optional infrastructure

## Multi-LLM strategy

| Environment | How second opinions work |
|---|---|
| CLI shell with codex/gemini/aider installed | `cli-invoke.sh` |
| Geepers-kernel installed | `scripts/llm-query.py` via `Bash` |
| Standalone Claude only | Graceful degradation; Claude-only output with a noted gap |

Optional MCP servers (`.mcp.json`, not yet shipped) would expose:
- `craft-providers` — multi-LLM via `ProviderFactory` from `~/shared/llm_providers`
- `craft-data` — data fetching via `ClientFactory` from `~/shared/data_fetching`

Both require `pip install geepers-kernel`. Not required.

## Relationship to other plugins

- `team` — council-style codebase-to-pitch. Different scope; team is for product/business pitches with adversarial review. Cross-link: `/craft:discuss --debate` is lighter-weight; `/team` is the heavyweight version.
- `elegance` — code refinement and decision council. `/craft:reconsider --validate` for routine checks; `/elegance` for deep refinement with the 14-agent council.
- `humanize` — owns `/humanize`. Craft never bundles its own.
- `accessibility` — owns `/accessibility`, the dedicated WCAG plugin. `craft-a11y` agent does internal a11y checks during `compose` and `reconsider`; full audits go to `/accessibility`.

## Development

Pure-markdown plugin. No build step, no test runner. Edit `.md` files directly. Banner script (`scripts/banner.sh`) requires `pyfiglet`/`toilet`/`figlet` (falls back to plain text).
