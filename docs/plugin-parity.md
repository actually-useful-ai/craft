# Plugin fleet control

`fleet.toml` is the public bill of materials for the reviewed plugin fleet:

| Package | Origin | Ref | Version |
|---|---|---|---|
| Craft | `actually-useful-ai/craft` | `v0.8.1` | `0.8.1` |
| Team | `actually-useful-ai/team` | `v0.1.4` | `0.1.4` |
| Intentional UX | `actually-useful-ai/intentional-ux` | `v0.2.2` | `0.2.2` |
| Accessibility | `actually-useful-ai/accessibility-devkit` | `v1.1.2` | `1.1.2` |
| Humanize | `actually-useful-ai/humanize` | `v1.2.1` | `1.2.1` |

The BOM also declares each package's logical content, supported runtime
manifests, runtime-specific installation IDs, runtime skill roots, and any
reviewed legacy links eligible for retirement. Keep hostnames, SSH routing, and
machine-specific checkout paths out of this file.

This table is the last reviewed release snapshot, not the current development
manifest. A working branch may declare a newer package version; advance the
Craft row only when its matching immutable tag exists.

Keep three claims distinct:

- **Portable package support:** the repository has a conforming Agent Plugins
  root `plugin.json`, immediate `skills/` children, and root `mcp.json` when it
  owns MCP servers.
- **Vendor manifest support:** the repository ships the declared Claude, Codex,
  Cursor, or Grok-compatible manifest.
- **Runtime activation:** a host inventory observes that exact package version
  as installed and enabled.

The first two are package structure. The third is host evidence. None implies
another.

## Release blockers

Routed providers without immutable reviewed releases remain outside active
`[[packages]]` entries:

| Provider | Intended version | Blocker |
|---|---:|---|
| Chaos | `1.0.0` | Missing immutable release |
| Platforms | `0.3.0` | Missing immutable release |
| Mobile | `1.0.0` | Missing immutable release |
| Pi | `1.0.0` | Missing immutable release |

`[[blocked_packages]]` exposes these gaps in human and JSON audit output but
does not audit checkout, manifest, or activation state. Move a provider into
the active BOM only after its canonical `v<version>` tag exists and the package
declares its actual runtime subset.

## Audit

With no personal host configuration, the controller audits only the local
machine and uses `~/plugins` as its checkout root:

```sh
scripts/fleet.py audit
scripts/fleet.py audit --json
```

The controller needs Python 3.11+ or `tomli` on an older interpreter. Streamed
remote probes do not parse TOML and remain compatible with Python 3.9.

The controller checks each package for:

- the declared Git origin;
- `HEAD` at the declared immutable ref;
- a clean worktree, including untracked files;
- every expected runtime manifest and its package identity;
- the declared version in every expected runtime manifest;
- whether each package is active at the declared version in every runtime the
  host expects;
- a stable logical hash over the BOM's declared content paths.

Manifest support and runtime activation are separate results. Claude activation
comes from `claude plugin list --json`; Codex activation comes from
`codex plugin list --json`; Grok activation requires `grok inspect --json` to
show the imported Claude package path and version; Cursor activation comes from
`.cursor-plugin/plugin.json` files under configured installed-cache roots.

The reference host's logical hash is marked `REF`. Other hosts must match it.
A runtime the host does not expect is `N/A`, even when the package supports it.
An unavailable expected runtime probe, missing active package, disabled package,
or wrong active version is `FAIL`. A missing configured skill root is `FAIL`
when that runtime is expected and `N/A` otherwise; a broken top-level symlink is
always `FAIL`. Any failure returns a nonzero status.

`scripts/plugin-parity.sh` remains as a compatibility wrapper around
`scripts/fleet.py audit`.

## Codex installation smoke test

Install a released Craft package through the configured marketplace and verify
the registry separately from the cached payload:

```sh
codex plugin marketplace add actually-useful-ai/craft
codex plugin add craft@lukeslp-craft
codex plugin list --json
```

For an unpublished branch, use the checkout's absolute path as the marketplace
source. A successful registry entry is runtime-activation evidence; confirm the
cache contains all 16 `skills/*/SKILL.md` files before treating package content
as verified.

A local marketplace installation copies the declared version into Codex's
plugin cache. If source changes without a version change, remove and reinstall
the local plugin before claiming cache parity. Start a fresh thread after any
install or repair so discovery reloads.

Do not leave direct top-level skill links active beside the installed plugin.
Before retiring one, resolve its target and confirm it points into the intended
Craft checkout. Move the link itself to a dated backup; do not delete the skill
directory it references.

## Personal host configuration

Put machine topology in `~/.config/craft/fleet-hosts.toml`, or pass another file
with `--hosts`. For example:

```toml
[settings]
ssh_bin = "ssh"
connect_timeout = 10
ssh_args = []

[[hosts]]
name = "workstation"
transport = "local"
reference = true
checkout_root = "~/plugins"
expected_runtimes = ["claude", "codex", "cursor", "grok"]
backup_root = "~/.local/state/craft/fleet-backups"

[hosts.paths]
craft = "~/src/craft"

[hosts.runtime_roots]
codex = ["~/.agents/skills", "~/.codex/skills"]

[hosts.installed_roots]
cursor = ["~/.cursor/plugins/cache"]

[[hosts]]
name = "build-host"
transport = "ssh"
target = "build-host"
checkout_root = "~/plugins"
expected_runtimes = ["claude", "codex", "cursor", "grok"]

[[hosts]]
name = "nested-host"
transport = "ssh"
target = "nested-host"
jump = "build-host"
checkout_root = "~/plugins"
expected_runtimes = ["codex"]
```

The default local host detects expected runtimes from available commands.
Every SSH host must declare `expected_runtimes`; an empty list explicitly means
none. Host `runtime_roots` and `installed_roots` entries replace that runtime's
public default, including an explicit `[]` replacement.

SSH probes stream the controller over standard input and run it with `python3`;
they do not install or write a helper on the remote host. Use repeated `--host`
options to audit a subset:

```sh
scripts/fleet.py audit --host workstation --host build-host
```

## Declared legacy-link retirement

The public BOM declares no default retirement targets. A link is safe to retire
only after the replacement plugin is observed as active and the link target is
confirmed to belong to the superseded checkout. Add targets only to a reviewed
BOM copy for that migration.

Repair is a dry-run unless `--apply` is explicit:

```sh
scripts/fleet.py repair
scripts/fleet.py repair --json
scripts/fleet.py repair --apply
```

Only `[[legacy_links]]` entries in `fleet.toml` are eligible. Missing paths are
idempotent no-ops. For a declared symlink, `--apply` moves the link itself to:

```text
~/.local/state/craft/fleet-backups/<timestamp>/<runtime-or-root>/<name>
```

The original path remains absent; the controller never recreates a direct skill
link. It refuses to move regular files or directories and never touches an
undeclared path. A host may override the central backup root with `backup_root`.
Broken undeclared links remain audit findings.

After an applied repair, start a fresh runtime session so skill discovery
reloads the corrected links.
