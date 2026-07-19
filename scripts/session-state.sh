#!/usr/bin/env bash
# session-state.sh — Snapshot git state at session start/end.
# Usage: bash session-state.sh start | end | diff
#   start: capture current state to a checkout-specific temporary file
#   end: compare against start snapshot, report changes
#   diff: just show what changed since last start

set -euo pipefail

MODE="${1:-start}"
TEMP_ROOT="${TMPDIR:-/tmp}"
CHECKOUT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)
CHECKOUT_KEY=$(printf '%s' "$CHECKOUT_ROOT" | cksum | awk '{print $1}')
USER_KEY=$(printf '%s' "${USER:-default}" | tr -c '[:alnum:]_-' '_')
SNAPSHOT="${TEMP_ROOT%/}/craft-session-start-${USER_KEY}-${CHECKOUT_KEY}.txt"

snapshot_time() {
    case "$(uname -s)" in
        Darwin)
            stat -f "%Sm" -t "%Y-%m-%dT%H:%M:%S%z" "$SNAPSHOT"
            ;;
        Linux)
            stat -c "%y" "$SNAPSHOT"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

snapshot() {
    {
        echo "# craft session snapshot — $(date '+%Y-%m-%dT%H:%M:%S%z')"
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
        echo "(snapshot at: $(snapshot_time))"
        echo ""
        diff "$SNAPSHOT" <(snapshot) || true
        ;;
    *)
        echo "usage: bash session-state.sh start|end|diff" >&2
        exit 2
        ;;
esac
