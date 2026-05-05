#!/usr/bin/env python3
"""analyze.py — Code complexity and duplication detection (stdlib only).

Walks a target directory, reports:
- Files over 500 lines (refactor candidates)
- Functions over 50 lines (within Python files)
- Duplicate code blocks (10+ consecutive lines with identical content)
- TODO/FIXME/HACK/XXX counts

Usage: python3 analyze.py [path] [--json]
"""

from __future__ import annotations

import ast
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


def find_long_files(root: Path, threshold: int = 500) -> list[tuple[Path, int]]:
    findings = []
    for path in root.rglob("*.py"):
        if any(part.startswith(".") for part in path.parts):
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").count("\n")
        except OSError:
            continue
        if lines >= threshold:
            findings.append((path, lines))
    return sorted(findings, key=lambda x: -x[1])


def find_long_functions(root: Path, threshold: int = 50) -> list[tuple[Path, str, int]]:
    findings = []
    for path in root.rglob("*.py"):
        if any(part.startswith(".") for part in path.parts):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
        except (SyntaxError, OSError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end = getattr(node, "end_lineno", node.lineno)
                length = end - node.lineno
                if length >= threshold:
                    findings.append((path, node.name, length))
    return sorted(findings, key=lambda x: -x[2])


def find_duplicates(root: Path, block_size: int = 10) -> list[tuple[str, list[Path]]]:
    seen: dict[str, list[Path]] = defaultdict(list)
    for path in root.rglob("*.py"):
        if any(part.startswith(".") for part in path.parts):
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for i in range(len(lines) - block_size):
            block = "\n".join(line.strip() for line in lines[i : i + block_size])
            if not block.strip() or len(block) < 100:
                continue
            seen[block].append(path)
    return [(b, paths) for b, paths in seen.items() if len(set(paths)) >= 2]


def count_todos(root: Path) -> dict[str, int]:
    pattern = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b")
    counts: dict[str, int] = defaultdict(int)
    for path in root.rglob("*"):
        if not path.is_file() or any(part.startswith(".") for part in path.parts):
            continue
        if path.suffix not in {".py", ".js", ".ts", ".tsx", ".jsx", ".sh", ".md"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for match in pattern.finditer(text):
            counts[match.group(1)] += 1
    return dict(counts)


def main() -> None:
    args = sys.argv[1:]
    json_output = "--json" in args
    paths = [a for a in args if a != "--json"]
    root = Path(paths[0] if paths else ".").resolve()

    long_files = find_long_files(root)
    long_funcs = find_long_functions(root)
    duplicates = find_duplicates(root)
    todos = count_todos(root)

    if json_output:
        result = {
            "long_files": [{"path": str(p), "lines": n} for p, n in long_files[:20]],
            "long_functions": [{"path": str(p), "name": name, "lines": n} for p, name, n in long_funcs[:20]],
            "duplicate_blocks": len(duplicates),
            "todos": todos,
        }
        print(json.dumps(result, indent=2))
        return

    print(f"## analyzing {root}")
    print()
    print(f"### long files ({len(long_files)} >= 500 lines)")
    for path, n in long_files[:10]:
        print(f"  {n:5d}  {path}")
    print()
    print(f"### long functions ({len(long_funcs)} >= 50 lines)")
    for path, name, n in long_funcs[:10]:
        print(f"  {n:5d}  {path}::{name}")
    print()
    print(f"### duplicate code blocks: {len(duplicates)}")
    print()
    print("### TODOs")
    for marker, n in sorted(todos.items()):
        print(f"  {marker}: {n}")


if __name__ == "__main__":
    main()
