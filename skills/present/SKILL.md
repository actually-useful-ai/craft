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

### `save` (mid-session checkpoint)
1. **Verify state** — `git log --oneline -3`, `git diff --stat`, `git status`. Surprise commits from parallel agents are a stop condition.
2. **Stage by name** — never `git add -A` or `git add -u` (the project hook blocks them; use explicit paths).
3. **Commit** — conventional commit message; never `Co-Authored-By` Claude/AI.
4. **Push** — origin only; never force-push to main.
5. **Verify** — `git status` clean.

### `ship` (release/deploy)
1. **Preflight** — `craft-canary` agent: check git is clean, tests pass, CI green, version bumped.
2. **Release** — tag, build artifacts, generate release notes.
3. **Deploy** — environment-specific. Idempotent.
4. **Postflight** — `craft-canary` re-checks: service health, smoke tests, monitor for errors.
5. **Checkpoint** — record what was deployed, when, by whom, to where.

### `publish` (repo/package publish)
1. **Verify metadata** — version bumped, README current, license present.
2. **Build** — `python -m build` or `npm run build` etc. Use `~/build-venv` for Python publishes (system twine is broken).
3. **Check** — `twine check dist/*` or `npm pack --dry-run`.
4. **Upload** — `twine upload`, `npm publish`, or `gh repo create / push`.
5. **Verify** — fetch the published version's metadata to confirm.

### `pr` (open pull request)
1. **Branch check** — current branch, not main.
2. **Push if needed** — `git push -u origin HEAD`.
3. **PR draft** — title (under 70 chars), body with summary + test plan.
4. **Open** — `gh pr create` with the drafted body.
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
