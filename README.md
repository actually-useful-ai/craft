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

The repository includes the Codex manifest and discovers all 16 skills from
`skills/`.

The equivalent CLI flow is:

```sh
codex plugin marketplace add actually-useful-ai/craft
codex plugin add craft@lukeslp-craft
codex plugin list --json
```

For local development, point the marketplace at an absolute checkout path:

```sh
codex plugin marketplace add /absolute/path/to/craft
codex plugin add craft@lukeslp-craft
```

Open a fresh Codex thread after installation so skill discovery reloads. Once
the plugin is active, back up and retire old top-level symlinks that point
directly into `craft/skills/`; leaving both discovery paths active can make the
selected source ambiguous.

## Portable package format

Craft also ships a root `plugin.json` for Agent Plugins 1.0. The portable core
is the immediate `skills/` tree; Craft has no MCP server, so it does not ship an
empty `mcp.json`. The existing Claude, Codex, and Cursor manifests remain in
place for client-specific installation and presentation.

## Install in Claude Code

From a Claude Code session, add the repository as a marketplace and install Craft:

```text
/plugin marketplace add actually-useful-ai/craft
/plugin install craft@lukeslp-craft
```

## Install in Cursor

```sh
cursor-agent plugin marketplace add https://github.com/actually-useful-ai/craft
cursor-agent
```

In the interactive agent, open `/plugin` and install Craft at user scope. That
account-scoped installation is available to both the IDE and CLI.

## Install in Claude Desktop

Download the release source archive. In Claude Desktop, open **Customize →
Plugins**, choose the custom-plugin upload option, and select the zipped Craft
plugin directory. Its skills are then available in Desktop chat.

## Usage

```bash
/craft:activate "Add OAuth to the API and choose the right approach"
/craft:ask anthropic "Challenge this migration plan"      # outside opinion
/craft:horizon "What am I missing in this product direction?" # adjacent options
/craft:impress critique path/to/artifact                  # quality diagnosis
/craft:swarm --size jillion "Scout this decision"        # 32 bounded Luna scouts
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
- 7 bundled capabilities (`ask`, `chefs-choice`, `horizon`, `impress`, `skill-auditor`, `skill-creator`, `swarm`)
- 14 optional helper profiles for deliberation, quality, implementation, delivery, and project maintenance
- 19 scripts, including deterministic consultation, durable bounded Swarm
  orchestration, fleet verification, skill auditing, and packaging tools. They
  need no third-party packages on Python 3.11+; `fleet.py` accepts `tomli` on
  older controller interpreters.

## Capability routing

Craft is the front door. State the goal and, when useful, the desired ambition:

```text
$craft:activate Chef's choice—impress me with this onboarding flow.
```

Craft selects the smallest useful stack and preserves ownership. Chef's Choice
selects resources; Impress sets the quality bar; the most-specific domain skill
owns implementation; optional providers retain authority in their domains.
Craft reports a material
selection in one concise line instead of requiring the person to remember a
catalog of skill names.

| Optional provider | Craft uses it for |
|---|---|
| Chaos | An explicitly requested playful constraint or remix, never generic ambition |
| Platforms | Platform delivery through one top-level executor and its own sub-routing |
| Intentional UX | Task paths, state transitions, recovery, and outcome evidence |
| Accessibility | Semantics, keyboard and assistive-technology behavior, and access verification |
| Mobile | Viewport, touch, motion, responsive layout, and measured performance evidence |
| Humanize | Meaning-preserving review of user-facing prose |

Each provider is independently installed and versioned. Installing Craft does
not install them. When a provider is absent, Craft names the evidence limitation
and uses a bounded fallback instead of impersonating that provider.

Reviews that cross at least two of task path, accessibility, mobile
implementation, and documentation use one Experience Review record. Specialist
provenance, manual-check ownership, unresolved dissent, and evidence strength
remain intact; Craft produces no aggregate score or conformance claim.

Horizon opens the option space before a decision. Impress can also critique an
existing artifact under `Merely competent`, `Exemplar opportunities`, and
`Performative sophistication` without revising it. Reconsider owns correctness,
first-principles rebuilds, and blast radius. Ask obtains exactly one outside
opinion. Swarm runs many stateless Luna scouts only after explicit paid-call
authorization; generic parallel work remains the job of native agents or the
independent Fanout skill.

The bundled capability-maintenance paths are `/craft:compose skill` for creating
or revising skills and `/craft:distill --skills` for read-only package and fleet
audits.

The five core workflow phases carry one evidence envelope. Measured, observed,
inferred, planned, and unavailable claims stay distinct through the final
`Done`, `Partial`, or `Blocked` handoff.

## Why modal commands

The core stays centered on five verbs. Variants such as quick research, planning, visual work, focused fixes, and publishing live behind modes so the workflow stays easy to remember.

## What it doesn't do

- Pitch a codebase as a product: that's [team](https://github.com/actually-useful-ai/team).
- Code refinement at depth or council-style debate: that's [elegance](https://github.com/actually-useful-ai/elegance).
- Rewrite user-facing prose: Craft routes that work to [humanize](https://github.com/actually-useful-ai/humanize) when installed.
- Perform dedicated accessibility reviews: Craft routes supported web work to [Accessibility Devkit](https://github.com/actually-useful-ai/accessibility-devkit) when installed.

Specialist products remain independently versioned. Craft discovers and
composes them without absorbing their source or weakening their authority.

## Outside-model consultations (optional)

`/craft:ask` is the portable, explicit consultation path. It labels the actual
provider and model, never silently falls back, and requires authorization before
sending a bounded brief outside the current runtime. Its `--list` and `--status`
modes make no inference calls.

The versioned route table is exposed by `scripts/ask.sh --list`; documentation
and command projections do not carry separate model labels. The four routes
use native Claude Code, Grok, Ollama, and Claude Code configured separately for
Z.ai. No route falls back to an API or gateway. Configure executable paths and
model choices in the private `${XDG_CONFIG_HOME:-~/.config}/craft/ask.env`.
See [CLI setup](skills/ask/references/cli-routes.md) for credentials, model
provenance, and runtime requirements. The legacy `scripts/llm-query.py` entry
point delegates to these routes.

Nothing in Craft depends on a configured outside provider. The workflow entry
points work on their own and report a missing route as a limitation.

`/craft:swarm` retains the `luna` route in `scripts/ask-legacy.sh`; it is separate
from native CLI consultations. Presets run 4, 8, 16, or 32 scouts; a hard ceiling of 64,
short per-scout responses, no retries, a global deadline, and explicit partial
status keep the deliberately extravagant mode bounded. Dry runs make no
inference calls. Paid runs persist private atomic result envelopes under
`~/craft/logs/swarm/`, so lost terminal output cannot turn an incomplete run
into an inferred result or an accidental retry.

## Fleet parity

`fleet.toml` is the public bill of materials for Craft, Team, Intentional UX,
Accessibility, and Humanize. `scripts/fleet.py` checks immutable checkout refs,
manifest versions, logical content hashes, expected runtime activation, and
broken top-level skill links across locally configured hosts. Machine topology
stays in `~/.config/craft/fleet-hosts.toml`. The public BOM declares no
legacy-link retirement targets because replacement activation and link
ownership are host-local facts. See [Plugin fleet control](docs/plugin-parity.md).

The fleet records Chaos, Platforms, Mobile, and Pi as release blockers until
their canonical repositories publish immutable version tags. Craft does not
present them as audited fleet packages before that evidence exists.

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
