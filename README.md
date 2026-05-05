# craft

Workflow toolbelt for Claude Code. Five modal commands organized around the work cycle.

```
discuss → compose → distill → reconsider → present
 think      build    refine    challenge     ship
```

## Install

```bash
claude plugin add actually-useful-ai/craft
```

## Usage

```bash
/craft:discuss --plan "Add OAuth to the API"          # plan first
/craft:compose frontend src/components/Login.tsx      # build it
/craft:distill --audit                                # check quality
/craft:reconsider --validate                          # verify correctness
/craft:present pr                                     # open the PR
```

Every command takes a mode flag and a target. Defaults are sensible: `--quick` for `discuss`, `--full` for `distill`, `--validate` for `reconsider`, `save` for `present`. Modes are listed in each command's `--help`.

## What's in here

- 7 slash commands (`discuss`, `compose`, `distill`, `reconsider`, `present`, `board`, `context`)
- 14 specialized agents (deliberation, quality, build/ship, utility)
- 9 stdlib scripts (multi-LLM query, data fetching, code analysis, kanban board, CLI detection, harvest, session state, nav validation)

## Why modal commands

The earlier swarm approach had 21 discrete slash commands. Most users learn 5 verbs and never touch the rest. The modal design here keeps the 5 verbs as commands and tucks the variants (quick/debate/plan/research, viz/frontend/docs, save/ship/publish, etc.) behind flags. Same coverage, less to memorize.

## What it doesn't do

- Pitch a codebase as a product — that's [team](https://github.com/actually-useful-ai/team).
- Code refinement at depth or 14-agent council debate — that's [elegance](https://github.com/actually-useful-ai/elegance).
- Strip robot language from prose — that's [humanize](https://github.com/actually-useful-ai/humanize).
- WCAG audits — that's [accessibility](https://github.com/actually-useful-ai/accessibility).

Craft does the workflow, not the specialized analysis.

## Multi-LLM second opinions (optional)

Several scripts try to call out to other CLIs (codex, gemini, aider, cursor-agent) for second opinions when those are installed. If none are available, craft degrades gracefully to Claude-only.

For richer multi-provider access, install `geepers-kernel` (`pip install geepers-kernel`) — `scripts/llm-query.py` will use the bundled `ProviderFactory` for unified access to 12 LLM providers.

Nothing in craft is hard-dependent on these. Skills work standalone.

## Output

Everything goes under `~/craft/`:

```
~/craft/
├── reports/by-date/YYYY-MM-DD/      discuss summaries, distill findings
├── recommendations/by-project/      accumulated, append-only
├── status/                          session work logs
├── snippets/                        internal harvest staging
├── logs/                            agent execution logs
└── board.json                       kanban state
```

Board HTML at `~/html/craft/board/index.html` if you serve it via Caddy.

## Author

Luke Steuber · luke@lukesteuber.com · [lukesteuber.com](https://lukesteuber.com)

MIT.
