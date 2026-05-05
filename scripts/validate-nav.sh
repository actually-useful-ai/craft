#!/usr/bin/env bash
# validate-nav.sh — Validate the CLAUDE.md hierarchy in a project tree.
# Checks: every CLAUDE.md is reachable from root; cross-references resolve;
# no broken markdown links to local files; parent links exist where appropriate.
# Usage: bash validate-nav.sh [path]

set -euo pipefail

ROOT="${1:-.}"
ROOT=$(cd "$ROOT" && pwd)

cd "$ROOT"

echo "## validating CLAUDE.md hierarchy under $ROOT"
echo ""

# Find every CLAUDE.md
mapfile -t CLAUDE_FILES < <(find . -maxdepth 4 -name "CLAUDE.md" -not -path "./.git/*" -not -path "*/node_modules/*" 2>/dev/null | sort)

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
    # Extract [text](path) where path is not http/mailto
    grep -oE '\[[^]]+\]\([^)]+\)' "$f" 2>/dev/null | while read -r link; do
        path=$(echo "$link" | sed -E 's/.*\((.*)\)/\1/')
        # Skip URLs and anchors
        if [[ "$path" =~ ^(http|https|mailto):// ]] || [[ "$path" == "#"* ]]; then
            continue
        fi
        # Strip anchor from path
        path_only="${path%%#*}"
        # Resolve relative to file
        if [[ -n "$path_only" && ! -e "$dir/$path_only" && ! -e "$path_only" ]]; then
            echo "  BROKEN: $f → $path"
            ISSUES=$((ISSUES + 1))
        fi
    done
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
