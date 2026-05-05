---
name: board
description: "Kanban board for tracking craft work. Add cards, mark done, view the board."
allowed-tools: Read, Grep, Glob, Bash
---

# /craft:board

Lightweight kanban for tracking what's open, doing, and done across craft sessions.

## Modes

| Mode | When to use |
|------|-------------|
| `add` | Add a card to a column. Default column: backlog. |
| `done` | Move a card to done. |
| `show` (default) | Render the board as HTML at `~/html/craft/board/index.html`. |

## Storage

Plain JSON at `~/craft/board.json` with columns: `backlog`, `doing`, `done`. Each card has `id`, `title`, `created`, `column`, optional `notes`, `project`.

## Procedure

### `show`
1. Read `~/craft/board.json` (create with empty columns if absent).
2. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/generate-board.py` to render HTML.
3. Open or report the path: `~/html/craft/board/index.html` (served via Caddy if configured).

### `add <title>`
1. Read board, append card with `column: backlog`, `created: <ISO timestamp>`, `id: <8-char hash>`.
2. Optional flags: `--column doing|done`, `--project <name>`, `--notes "..."`.
3. Re-render board.

### `done <card-id-or-title-prefix>`
1. Find card by id prefix or title prefix.
2. Move to `done` column with `completed: <ISO timestamp>`.
3. Re-render board.

## Output

HTML board at `~/html/craft/board/index.html`. Card data at `~/craft/board.json`.

## Anti-patterns

- Using the board as the only task list — for multi-step in-session work, use TodoWrite.
- Forgetting to mark `done` — the board accumulates noise.
