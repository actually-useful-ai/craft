# craft

A portable workflow for deliberate planning, focused building, careful refinement, validation, and delivery.

```
discuss → compose → distill → reconsider → present
 think      build    refine    challenge     ship
```

## Install in Codex

Open the Codex app's **Plugin Directory**, choose the option to import a plugin, and use:

```text
https://github.com/actually-useful-ai/craft
```

The repository includes the Codex manifest and discovers all nine workflow entry points from `skills/`.

## Install in Claude Code

From a Claude Code session, add the repository as a marketplace and install Craft:

```text
/plugin marketplace add actually-useful-ai/craft
/plugin install craft@lukeslp-craft
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

## What's included

- 9 workflow entry points (`activate`, `board`, `compose`, `context`, `discuss`, `distill`, `enhance`, `present`, `reconsider`)
- 14 optional helper profiles for deliberation, quality, implementation, delivery, and project maintenance
- 9 stdlib scripts (multi-LLM query, data fetching, code analysis, kanban board, CLI detection, harvest, session state, nav validation)

## Why modal commands

The core stays centered on five verbs. Variants such as quick research, planning, visual work, focused fixes, and publishing live behind modes so the workflow stays easy to remember.

## What it doesn't do

- Pitch a codebase as a product: that's [team](https://github.com/actually-useful-ai/team).
- Code refinement at depth or council-style debate: that's [elegance](https://github.com/actually-useful-ai/elegance).
- Strip robot language from prose: that's [humanize](https://github.com/actually-useful-ai/humanize).
- WCAG audits: that's [Accessibility Devkit](https://github.com/actually-useful-ai/accessibility-devkit).

Craft does the workflow, not the specialized analysis.

## Multi-model second opinions (optional)

Several scripts can ask installed command-line tools such as Codex, Gemini, Aider, or Cursor for a second opinion. If none are available, Craft continues with the current model.

For richer multi-provider access, install `geepers-kernel` (`pip install geepers-kernel`): `scripts/llm-query.py` will use the bundled `ProviderFactory` for unified access to 12 LLM providers.

Nothing in Craft depends on these optional integrations. The workflow entry points work on their own.

## Fleet parity

`scripts/plugin-parity.sh` compares the installed Craft, Intentional UX, Accessibility, and Humanize versions on the current Mac, Beast, and Drummer. It hashes skill sources without copying credentials, caches, sessions, or machine settings. See [Plugin parity](docs/plugin-parity.md) for version-pinned installation, verification, and rollback commands.

## Output

Everything goes under `~/craft/`:

```
~/craft/
├── reports/by-date/YYYY-MM-DD/      discuss summaries, distill findings
├── recommendations/by-project/      accumulated, append-only
├── status/                          session work logs
├── snippets/                        internal harvest staging
├── logs/                            execution logs
└── board.json                       kanban state
```

Board HTML at `~/html/craft/board/index.html` if you serve it via Caddy.

## Author

Luke Steuber · luke@lukesteuber.com · [lukesteuber.com](https://lukesteuber.com)

MIT.
