# Plugin parity

Keep the same reviewed releases of four plugins on Neo, Beast, and Drummer:

| Plugin | Repository | Release |
|---|---|---|
| Craft | [`actually-useful-ai/craft`](https://github.com/actually-useful-ai/craft) | `v0.5.0` |
| Intentional UX | [`actually-useful-ai/intentional-ux`](https://github.com/actually-useful-ai/intentional-ux) | `v0.2.1` |
| Accessibility | [`actually-useful-ai/accessibility-devkit`](https://github.com/actually-useful-ai/accessibility-devkit) | `v1.0.0` |
| Humanize | [`actually-useful-ai/humanize`](https://github.com/actually-useful-ai/humanize) | `v1.2.0` |

GitHub is the source of truth. Each machine gets reviewed plugin files under `~/plugins`. Do not copy all of `~/.codex`, `~/.claude`, or `~/.agents`; those directories contain machine-specific state and may contain credentials.

## Topology

Run fleet commands from Neo:

```text
Neo → Beast (`ssh beast`) → Drummer (`ssh drummer` from Beast)
```

The Drummer alias belongs to Beast. The verifier follows that route instead of assuming Neo can reach Drummer directly.

## Install a reviewed release

The function below refuses to overwrite an existing path. Run it separately on each machine for a first installation.

```sh
install_plugin_release() {
  repository=$1
  release=$2
  plugin=$3
  destination="$HOME/plugins/$plugin"

  if [ -e "$destination" ] || [ -L "$destination" ]; then
    printf 'Stopped: %s already exists.\n' "$destination" >&2
    return 1
  fi

  mkdir -p "$HOME/plugins"
  git clone --filter=blob:none --branch "$release" --depth 1 \
    "https://github.com/$repository.git" "$destination"
}

install_plugin_release actually-useful-ai/craft v0.5.0 craft
install_plugin_release actually-useful-ai/intentional-ux v0.2.1 intentional-ux
install_plugin_release actually-useful-ai/accessibility-devkit v1.0.0 accessibility
install_plugin_release actually-useful-ai/humanize v1.2.0 humanize
```

On Beast, repeat the four calls in a Beast shell. Then open Drummer from Beast and repeat them there:

```sh
ssh beast
ssh drummer
```

Start a fresh Codex session on each machine after installation so plugin discovery reloads.

## Update or roll back a Git-backed install

Inspect the worktree before switching releases. The command stops if the plugin contains uncommitted changes.

```sh
switch_plugin_release() {
  plugin=$1
  release=$2
  destination="$HOME/plugins/$plugin"

  if [ ! -d "$destination/.git" ]; then
    printf 'Stopped: %s is not a Git-backed install.\n' "$destination" >&2
    return 1
  fi

  if [ -n "$(git -C "$destination" status --porcelain)" ]; then
    printf 'Stopped: %s has uncommitted changes.\n' "$destination" >&2
    return 1
  fi

  git -C "$destination" fetch --tags origin
  git -C "$destination" checkout --detach "$release"
}
```

Use the current release tag to update. Use the previous reviewed tag to roll back. Never use a branch name for a rollback because branch heads move.

Copied installs do not have Git metadata. Replace one only from its canonical checkout after confirming the destination contains no local work; do not mix files from two releases.

## Verify parity

From the Craft checkout on Neo:

```sh
scripts/plugin-parity.sh
```

The verifier reads each `.codex-plugin/plugin.json` version and hashes every
shipped file under `skills/` and `scripts/` in a stable order. This includes
bundled transports and route logic, so a script-only change cannot pass as
parity. It prints one row per host and plugin:

- `REFERENCE`: Neo's installed copy, used as the comparison source;
- `OK`: version and package hash match the local reference;
- `MISSING`: the manifest or skill files are absent;
- `DRIFT`: the version, skill content, or both differ;
- `UNREACHABLE`: the SSH route failed;
- `NO_REFERENCE`: Neo lacks the plugin needed for comparison.

Any result other than `REFERENCE` or `OK` returns a nonzero exit status. Fix the named host and plugin, start a fresh Codex session there, then run the verifier again.

The script accepts SSH alias overrides without editing machine configuration:

```sh
BEAST_HOST=beast DRUMMER_HOST=drummer scripts/plugin-parity.sh
```

For fixture-based testing, use `scripts/plugin-parity.sh --fixture path/to/matrix.tsv`.
The fixture format is tab-separated: host, plugin, version, and package hash.

## Manual acceptance

Hashes prove that the reviewed skill sources match. They do not prove that a running Codex session reloaded them. On every machine, open a fresh session and confirm that these entries appear in the skill picker:

- `craft:compose`
- `craft:chefs-choice`
- `craft:exemplar`
- `craft:skill-auditor`
- `craft:skill-creator`
- `intentional-ux:intentional-ux`
- `accessibility:accessibility`
- `humanize:humanize`

Run one harmless prompt through each entry. Record any discovery failure before changing application state or copying configuration between machines.
