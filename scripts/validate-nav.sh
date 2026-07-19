#!/usr/bin/env bash
# validate-nav.sh — Validate the CLAUDE.md hierarchy in a project tree.
# Checks: every CLAUDE.md is reachable from root; cross-references resolve;
# no broken markdown links to local files; parent links exist where appropriate.
# Usage: bash validate-nav.sh [path]

set -euo pipefail

if ! command -v python3 >/dev/null 2>&1; then
    echo "validate-nav.sh requires python3 for Markdown link parsing" >&2
    exit 2
fi

ROOT="${1:-.}"
ROOT=$(cd "$ROOT" && pwd)

cd "$ROOT"

echo "## validating CLAUDE.md hierarchy under $ROOT"
echo ""

# Find every CLAUDE.md. NUL delimiters preserve spaces and newlines in names.
CLAUDE_FILES=()
while IFS= read -r -d '' file; do
    CLAUDE_FILES+=("$file")
done < <(find . -maxdepth 4 -name "CLAUDE.md" -not -path "./.git/*" -not -path "*/node_modules/*" -print0 2>/dev/null)

if [[ ${#CLAUDE_FILES[@]} -eq 0 ]]; then
    echo "no CLAUDE.md files found under $ROOT"
    exit 0
fi

echo "found ${#CLAUDE_FILES[@]} CLAUDE.md files:"
for f in "${CLAUDE_FILES[@]}"; do
    echo "  $f"
done
echo ""

# Track findings
ISSUES=0

# Emit NUL-delimited inline-link destinations. The scanner balances nested
# parentheses and removes an optional CommonMark-style title.
extract_link_destinations() {
    python3 - "$1" <<'PY'
import re
import sys
from urllib.parse import unquote


TITLE = re.compile(
    r'''\s+(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\((?:\\.|[^)\\])*\))\s*$''',
    re.DOTALL,
)
ESCAPED_PUNCTUATION = re.compile(r"\\([!\"#$%&'()*+,./:;<=>?@\[\\\]^_`{|}~-])")


def destinations(text):
    offset = 0
    while True:
        opening = text.find("](", offset)
        if opening < 0:
            return

        start = opening + 2
        cursor = start
        depth = 1
        escaped = False
        while cursor < len(text):
            char = text[cursor]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    break
            cursor += 1

        if depth != 0:
            offset = start
            continue

        raw = text[start:cursor].strip()
        title = TITLE.search(raw)
        if title:
            raw = raw[: title.start()].rstrip()
        if raw.startswith("<") and raw.endswith(">"):
            raw = raw[1:-1]
        raw = ESCAPED_PUNCTUATION.sub(r"\1", raw)
        yield unquote(raw)
        offset = cursor + 1


with open(sys.argv[1], encoding="utf-8") as handle:
    markdown = handle.read()
for destination in destinations(markdown):
    sys.stdout.buffer.write(destination.encode("utf-8") + b"\0")
PY
}

# Check 1: every CLAUDE.md has a top-level title
echo "## check 1: every CLAUDE.md has a top-level heading"
for f in "${CLAUDE_FILES[@]}"; do
    if ! head -1 "$f" | grep -qE "^#"; then
        echo "  ISSUE: $f does not start with a markdown heading"
        ISSUES=$((ISSUES + 1))
    fi
done
echo "  done"
echo ""

# Check 2: markdown links to local files actually resolve
echo "## check 2: local markdown links resolve"
for f in "${CLAUDE_FILES[@]}"; do
    dir=$(dirname "$f")
    # Process substitution keeps issue increments in this shell, not a pipeline subshell.
    while IFS= read -r -d '' path; do
        # Skip URLs and anchors
        case "$path" in
            "#"*|//*|*://*|mailto:*|tel:*|data:*) continue ;;
        esac
        # Strip anchor from path
        path_only="${path%%#*}"
        # Relative paths resolve only beside the containing file. A leading
        # slash explicitly means project-root-relative.
        if [[ "$path_only" == /* ]]; then
            target="$ROOT/${path_only#/}"
        else
            target="$dir/$path_only"
        fi
        if [[ -n "$path_only" && ! -e "$target" ]]; then
            echo "  BROKEN: $f → $path"
            ISSUES=$((ISSUES + 1))
        fi
    done < <(extract_link_destinations "$f")
done
echo "  done"
echo ""

# Check 3: subdirectory CLAUDE.md files reference back to root
echo "## check 3: nested CLAUDE.md files mention parent or root"
for f in "${CLAUDE_FILES[@]}"; do
    if [[ "$f" == "./CLAUDE.md" ]]; then
        continue
    fi
    # Check for ~/CLAUDE.md, ../CLAUDE.md, /CLAUDE.md, project root, parent
    if ! grep -qE "(~/CLAUDE.md|\.\./CLAUDE.md|root CLAUDE|parent|monorepo)" "$f" 2>/dev/null; then
        echo "  WEAK: $f does not reference parent CLAUDE.md (cosmetic)"
    fi
done
echo "  done"
echo ""

echo "## summary"
echo "  ${#CLAUDE_FILES[@]} CLAUDE.md files checked, $ISSUES issues found"

if [[ $ISSUES -gt 0 ]]; then
    exit 1
fi
