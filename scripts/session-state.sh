#!/usr/bin/env bash
# session-state.sh — Snapshot git state at session start/end.
# Usage: bash session-state.sh start|end|diff [session-id]
#   start: capture current state to a checkout-specific temporary file
#   end: compare against start snapshot, report changes
#   diff: just show what changed since last start
# Set CRAFT_SESSION_ID instead of the second argument when convenient. Without
# either, the caller's process ID keeps repeated calls from one shell together.

set -euo pipefail

MODE="${1:-start}"
TEMP_ROOT="${TMPDIR:-/tmp}"
CHECKOUT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)
CHECKOUT_KEY=$(printf '%s' "$CHECKOUT_ROOT" | cksum | awk '{print $1}')
USER_KEY=$(printf '%s' "${USER:-default}" | tr -c '[:alnum:]_-' '_')
SESSION_ID="${2:-${CRAFT_SESSION_ID:-${PPID:-default}}}"
SESSION_LABEL=$(printf '%s' "$SESSION_ID" | tr -c '[:alnum:]_-' '_' | cut -c1-32)
SESSION_KEY=$(printf '%s' "$SESSION_ID" | cksum | awk '{print $1}')
SNAPSHOT="${TEMP_ROOT%/}/craft-session-start-${USER_KEY}-${CHECKOUT_KEY}-${SESSION_LABEL}-${SESSION_KEY}.txt"
TEMP_FILE=""

cleanup() {
    if [[ -n "$TEMP_FILE" && -e "$TEMP_FILE" ]]; then
        rm -f "$TEMP_FILE"
    fi
}

trap cleanup EXIT HUP INT TERM

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
        TEMP_FILE=$(mktemp "${TEMP_ROOT%/}/craft-session-start.XXXXXX")
        snapshot > "$TEMP_FILE"
        mv -f "$TEMP_FILE" "$SNAPSHOT"
        TEMP_FILE=""
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
        TEMP_FILE=$(mktemp "${TEMP_ROOT%/}/craft-session-now.XXXXXX")
        snapshot > "$TEMP_FILE"
        diff "$SNAPSHOT" "$TEMP_FILE" || true
        rm -f "$TEMP_FILE"
        TEMP_FILE=""
        ;;
    *)
        echo "usage: bash session-state.sh start|end|diff [session-id]" >&2
        exit 2
        ;;
esac
