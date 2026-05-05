#!/usr/bin/env bash
# session-state.sh — Snapshot git state at session start/end.
# Usage: bash session-state.sh start | end | diff
#   start: capture current state to /tmp/craft-session-start.txt
#   end: compare against start snapshot, report changes
#   diff: just show what changed since last start

set -euo pipefail

MODE="${1:-start}"
SNAPSHOT="/tmp/craft-session-start-${USER:-default}.txt"

snapshot() {
    {
        echo "# craft session snapshot — $(date -Iseconds)"
        echo "## working directory"
        pwd
        echo ""
        echo "## branch"
        git branch --show-current 2>/dev/null || echo "(not a git repo)"
        echo ""
        echo "## last commit"
        git log --oneline -1 2>/dev/null || echo "(none)"
        echo ""
        echo "## status"
        git status --short 2>/dev/null | head -50 || echo "(no git)"
        echo ""
        echo "## untracked count"
        git status --short 2>/dev/null | grep -c "^??" || echo 0
    }
}

case "$MODE" in
    start)
        snapshot > "$SNAPSHOT"
        echo "snapshot written to $SNAPSHOT"
        cat "$SNAPSHOT"
        ;;
    end|diff)
        if [[ ! -f "$SNAPSHOT" ]]; then
            echo "no session start snapshot found at $SNAPSHOT" >&2
            exit 1
        fi
        echo "## changes since session start"
        echo "(snapshot at: $(stat -c %y "$SNAPSHOT" 2>/dev/null || stat -f %Sm "$SNAPSHOT"))"
        echo ""
        snapshot > /tmp/craft-session-now.txt
        diff "$SNAPSHOT" /tmp/craft-session-now.txt || true
        ;;
    *)
        echo "usage: bash session-state.sh start|end|diff" >&2
        exit 2
        ;;
esac
