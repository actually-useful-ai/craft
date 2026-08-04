# craft

A portable workflow that starts from the goal, selects useful capabilities,
preserves clear ownership, and carries work through planning, implementation,
verification, and delivery.

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
/craft:activate "Add OAuth to the API and choose the right approach"
/craft:discuss --plan "Add OAuth to the API"          # plan first
/craft:compose frontend src/components/Login.tsx      # build it
/craft:compose skill skills/example                    # create or revise a skill
/craft:distill --audit                                # check quality
/craft:distill --skills                               # audit skills and installs
/craft:reconsider --validate                          # verify correctness
/craft:present pr                                     # open the PR
```

Every command takes a mode flag and a target. Defaults are sensible: `--quick` for `discuss`, `--full` for `distill`, `--validate` for `reconsider`, `save` for `present`. Modes are listed in each command's `--help`.

## What's included

- 9 workflow entry points (`activate`, `board`, `compose`, `context`, `discuss`, `distill`, `enhance`, `present`, `reconsider`)
- 4 bundled capabilities (`chefs-choice`, `exemplar`, `skill-auditor`, `skill-creator`)
- 14 optional helper profiles for deliberation, quality, implementation, delivery, and project maintenance
- 14 stdlib scripts, including deterministic skill auditing and packaging tools

## Capability routing

Craft is the front door. State the goal and, when useful, the desired ambition:

```text
$craft:activate Chef's choice—impress me with this onboarding flow.
```

Craft selects the smallest useful stack and preserves ownership. Chef's Choice
selects resources; Exemplar sets the quality bar; the most-specific domain skill
owns implementation; optional providers such as Intentional UX, Accessibility,
and Humanize retain authority in their domains. Craft reports a material
selection in one concise line instead of requiring the person to remember a
catalog of skill names.

The bundled capability-maintenance paths are `/craft:compose skill` for creating
or revising skills and `/craft:distill --skills` for read-only package and fleet
audits.

## Why modal commands

The core stays centered on five verbs. Variants such as quick research, planning, visual work, focused fixes, and publishing live behind modes so the workflow stays easy to remember.

## What it doesn't do

- Pitch a codebase as a product: that's [team](https://github.com/actually-useful-ai/team).
- Code refinement at depth or council-style debate: that's [elegance](https://github.com/actually-useful-ai/elegance).
- Rewrite user-facing prose: Craft routes that work to [humanize](https://github.com/actually-useful-ai/humanize) when installed.
- Perform dedicated accessibility reviews: Craft routes supported web work to [Accessibility Devkit](https://github.com/actually-useful-ai/accessibility-devkit) when installed.

Specialist products remain independently versioned. Craft discovers and
composes them without absorbing their source or weakening their authority.

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

MIT, with Apache-2.0 terms for the bundled Skill Creator. See
`skills/skill-creator/LICENSE.txt`.
