# Plugin release checklist

Use this for `publish` when the package is a skill-bearing plugin, such as
Craft, Team, Humanize, Intentional UX, Chaos, or Platforms. These packages ship
to several runtimes from one checkout, so a release fails quietly when one
manifest or one version string is left behind.

## 1. Find every manifest

Check which of these the repository carries. Not every package has all of them.

| File | Runtime |
|---|---|
| `plugin.json` | Agent Plugins 1.0 portable metadata |
| `.claude-plugin/plugin.json` | Claude Code plugin |
| `.claude-plugin/marketplace.json` | Claude Code marketplace entry |
| `.codex-plugin/plugin.json` | Codex plugin |
| `.cursor-plugin/plugin.json` | Cursor plugin |
| `.cursor-plugin/marketplace.json` | Cursor marketplace entry (metadata and plugin versions) |

When the repository has a declared metadata authority, such as `suite.toml` in
Platforms, change only that source and run its generator. Never hand-edit generated
manifests or lock files such as `dist/manifest.lock.json`.

## 2. Bump the version everywhere

Search for the old version before and after the change:

```sh
grep -rn --exclude-dir=.git 'OLD_VERSION' .
```

Update every version string the search finds: the manifests, the heading of the
project `CLAUDE.md`, and any test that pins the version. The second search must
return nothing. Bump even for a description-only change: installed copies are
projections keyed by version, so an unchanged version may never refresh.

## 3. Keep the shared fields aligned

`name`, `version`, `description`, `author`, `homepage`, `repository`, `license`,
and `keywords` must match across the manifests that carry them. Credit Luke
Steuber as author. Keep counts in `README.md`, `CLAUDE.md`, and the root
`SKILL.md` in step with the actual `skills/*/SKILL.md` inventory.

## 4. Verify

Run the repository's own commands from its `CLAUDE.md` or `AGENTS.md`, for
example `python3 -B -m unittest discover -s tests -v`. Run the bundled
`skill-auditor` against the package root for frontmatter and manifest findings.
A green suite does not establish live provider authentication or that an
installed runtime has picked up the release; report those as unverified.

## 5. Pull requests

Stage files by name. For a stacked pull request in a repository that keeps
merged branches, the child does not retarget on its own after the parent merges:
run `gh pr edit N --base main`, then confirm the diff shrank to the child's
commits.

## 6. Reinstall

Tell the owner which commands refresh each runtime after merge:

```text
Claude Code: /plugin marketplace update <marketplace>  then  /plugin install <name>@<marketplace>
Codex:       codex plugin marketplace add <owner>/<repo>  then  codex plugin add <name>@<marketplace>
Cursor:      reinstall from the Cursor marketplace entry
```

Open a fresh session afterwards so skill discovery reloads.
