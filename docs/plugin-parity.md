# Plugin fleet control

`fleet.toml` is the public bill of materials for the reviewed plugin fleet:

| Package | Origin | Ref | Version |
|---|---|---|---|
| Craft | `actually-useful-ai/craft` | `v0.7.2` | `0.7.2` |
| Team | `actually-useful-ai/team` | `v0.1.4` | `0.1.4` |
| Intentional UX | `actually-useful-ai/intentional-ux` | `v0.2.2` | `0.2.2` |
| Accessibility | `actually-useful-ai/accessibility-devkit` | `v1.1.2` | `1.1.2` |
| Humanize | `actually-useful-ai/humanize` | `v1.2.1` | `1.2.1` |

The BOM also declares each package's logical content, supported runtime
manifests, runtime-specific installation IDs, runtime skill roots, and the exact
legacy links eligible for retirement. Keep hostnames, SSH routing, and
machine-specific checkout paths out of this file.

## Audit

With no personal host configuration, the controller audits only the local
machine and uses `~/plugins` as its checkout root:

```sh
scripts/fleet.py audit
scripts/fleet.py audit --json
```

Each package is checked for:

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
