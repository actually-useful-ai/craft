#!/usr/bin/env python3
"""generate-board.py — Render ~/craft/board.json as a kanban HTML page.

Reads ~/craft/board.json (creating with empty columns if absent),
writes ~/html/craft/board/index.html.

Usage: python3 generate-board.py
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

BOARD_PATH = Path.home() / "craft" / "board.json"
HTML_PATH = Path.home() / "html" / "craft" / "board" / "index.html"

EMPTY_BOARD = {"backlog": [], "doing": [], "done": []}

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>craft board</title>
<style>
:root {{
  --bg: #0e0e10;
  --fg: #e6e6e6;
  --muted: #888;
  --col-bg: #1a1a1d;
  --card-bg: #2a2a2d;
  --accent: #f5a623;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; padding: 24px; font: 14px/1.4 system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--fg); }}
h1 {{ margin: 0 0 8px; font-size: 24px; }}
.meta {{ color: var(--muted); margin-bottom: 24px; font-size: 12px; }}
.board {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
.column {{ background: var(--col-bg); border-radius: 8px; padding: 12px; min-height: 200px; }}
.column h2 {{ margin: 0 0 12px; font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); }}
.column .count {{ float: right; color: var(--accent); }}
.card {{ background: var(--card-bg); border-radius: 4px; padding: 10px 12px; margin-bottom: 8px; border-left: 3px solid var(--accent); }}
.card .title {{ font-weight: 500; }}
.card .meta {{ font-size: 11px; color: var(--muted); margin-top: 4px; }}
.empty {{ color: var(--muted); font-style: italic; padding: 20px 0; text-align: center; }}
</style>
</head>
<body>
<h1>craft board</h1>
<div class="meta">generated {timestamp}</div>
<div class="board">
{columns}
</div>
</body>
</html>
"""


def render_card(card: dict) -> str:
    title = card.get("title", "(untitled)")
    project = card.get("project", "")
    created = card.get("created", "")
    meta_parts = []
    if project:
        meta_parts.append(project)
    if created:
        meta_parts.append(created[:10])
    meta = " · ".join(meta_parts)
    notes = card.get("notes", "")
    notes_html = f'<div class="meta">{notes}</div>' if notes else ""
    return f'''<div class="card">
        <div class="title">{title}</div>
        <div class="meta">{meta}</div>
        {notes_html}
    </div>'''


def render_column(name: str, cards: list[dict]) -> str:
    cards_html = "".join(render_card(c) for c in cards) if cards else '<div class="empty">empty</div>'
    return f'''<div class="column">
        <h2>{name} <span class="count">{len(cards)}</span></h2>
        {cards_html}
    </div>'''


def main() -> None:
    BOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    HTML_PATH.parent.mkdir(parents=True, exist_ok=True)

    if BOARD_PATH.exists():
        with open(BOARD_PATH) as f:
            board = json.load(f)
    else:
        board = EMPTY_BOARD
        with open(BOARD_PATH, "w") as f:
            json.dump(board, f, indent=2)

    columns_html = "".join(
        render_column(name, board.get(name, []))
        for name in ("backlog", "doing", "done")
    )

    html = HTML_TEMPLATE.format(
        timestamp=datetime.now().isoformat(timespec="seconds"),
        columns=columns_html,
    )

    HTML_PATH.write_text(html, encoding="utf-8")
    print(f"board written to {HTML_PATH}")
    for col, cards in board.items():
        print(f"  {col}: {len(cards)} cards")


if __name__ == "__main__":
    main()
