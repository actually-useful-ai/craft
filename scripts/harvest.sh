#!/usr/bin/env bash
# harvest.sh — Capture reusable code snippets from the working tree to ~/SNIPPETS/.
# Usage: bash harvest.sh [--dry-run] [path]

set -euo pipefail

DRY_RUN=0
TARGET="."

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN=1; shift ;;
        *) TARGET="$1"; shift ;;
    esac
done

ARCHIVE="${HOME}/SNIPPETS"
TODAY=$(date +%Y-%m-%d)

if [[ $DRY_RUN -eq 0 ]]; then
    mkdir -p "$ARCHIVE/by-date/$TODAY"
fi

# Heuristic: harvest files that look like reusable utilities.
# - Single-purpose Python files under 300 lines with no project-specific imports
# - Single-purpose shell scripts under 200 lines
# - SQL fragments, regex patterns, config templates

SHARED_PY="${HOME}/shared"

echo "## harvest scan in $TARGET"
echo ""

# Python utilities
find "$TARGET" -maxdepth 3 -name "*.py" -size -10k 2>/dev/null | while read -r f; do
    # Skip if it imports project-specific paths
    if grep -qE "from \. import|from \.\.|sys\.path\.insert" "$f" 2>/dev/null; then
        continue
    fi
    # Has a docstring or top-of-file comment?
    if head -5 "$f" | grep -qE '^"""|^#' 2>/dev/null; then
        echo "  candidate: $f ($(wc -l < "$f") lines)"
        if [[ $DRY_RUN -eq 0 ]]; then
            base=$(basename "$f")
            cp "$f" "$ARCHIVE/by-date/$TODAY/$base"
        fi
    fi
done

echo ""
if [[ $DRY_RUN -eq 0 ]]; then
    echo "harvest written to $ARCHIVE/by-date/$TODAY/"
    echo "review and promote useful files to $ARCHIVE/by-pattern/<category>/"
else
    echo "(dry run — no files written)"
fi
