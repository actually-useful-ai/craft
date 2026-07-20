---
name: present
description: "Save, ship, publish, open a PR, or wrap the session. The shipping phase of craft. Replaces /quicksave, /shipit, /pushit, /wrap."
allowed-tools: Read, Grep, Glob, Bash, Agent
---

# /craft:present

Ship the work. The phase where things become real (`discuss → compose → distill → reconsider → present`).

## Modes

| Mode | When to use |
|------|-------------|
| `save` (default) | Mid-session checkpoint: verify state, commit, push. (formerly /quicksave) |
| `ship` | Release/deploy: preflight, deploy, postflight, verify. (formerly /shipit) |
| `publish` | Repository or package publish: PyPI, npm, marketplace. (formerly /pushit) |
| `pr` | Open a pull request from the current branch. |
| `wrap` | Session end: commit, harvest, next-steps, final report. (formerly /wrap) |

## Procedure

Use the [helper-profile fallback](../helper-profiles.md) when the host does not
expose `craft-canary` as a named profile.

### `save` (mid-session checkpoint)
1. **Verify state**: `git log --oneline -3`, `git diff --stat`, `git status`. Surprise commits from parallel agents are a stop condition.
2. **Stage by name**: never `git add -A` or `git add -u` (the project hook blocks them; use explicit paths).
3. **Commit**: use a conventional commit message; never add a model as co-author.
4. **Push**: origin only; never force-push to main.
5. **Verify**: confirm `git status` is clean.

### `ship` (release/deploy)
1. **Preflight**: `craft-canary` checks that git is clean, tests pass, CI is green, and the version changed.
2. **Release**: tag, build artifacts, and generate release notes.
3. **Deploy**: use the environment-specific, idempotent process.
4. **Postflight**: `craft-canary` rechecks service health, smoke tests, and error monitoring.
5. **Checkpoint**: record what went out, when, by whom, and where.

### `publish` (repo/package publish)
1. **Verify metadata**: confirm the version changed, the README is current, and a license exists.
2. **Build**: run `python -m build`, `npm run build`, or the project's equivalent. Use `~/build-venv` for Python publishes (system twine is broken).
3. **Check**: run `twine check dist/*` or `npm pack --dry-run`.
4. **Upload**: use `twine upload`, `npm publish`, or `gh repo create / push`.
5. **Verify**: fetch the published version's metadata.

### `pr` (open pull request)
1. **Branch check**: confirm the current branch is not main.
2. **Push if needed**: `git push -u origin HEAD`.
3. **PR draft**: write a title under 70 characters and a body with a summary and test plan.
4. **Open**: run `gh pr create` with the drafted body.
5. **Return URL**.

### `wrap` (session end)
Equivalent to `/craft:distill --conclude`. Use `wrap` here when you want explicit ship intent (commit + push), not just hygiene (which `--conclude` may skip if state is dirty).

## Anti-patterns

- `save` without verifying git state first (parallel agents may have committed).
- `ship` without a preflight; deploys go wrong silently.
- `publish` without `twine check` (PyPI README rendering bugs are common).
- `pr` while still on main (most projects forbid).

## Handoffs

After `wrap`, the session is done. After `ship`/`publish`, the cycle restarts at `/craft:discuss` for the next thing.
