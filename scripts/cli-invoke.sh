#!/usr/bin/env bash
# cli-invoke.sh — Safely invoke an external CLI with a prompt, timeout, and fallthrough.
# Usage: bash cli-invoke.sh <cli> <prompt> [timeout_seconds]
#   cli: codex | gemini | cursor-agent | aider
#   prompt: the prompt text (single argument; quote it)
#   timeout: defaults to 60s

set -euo pipefail

CLI="${1:-}"
PROMPT="${2:-}"
TIMEOUT="${3:-60}"

if [[ -z "$CLI" || -z "$PROMPT" ]]; then
    echo "usage: bash cli-invoke.sh <cli> <prompt> [timeout]" >&2
    exit 2
fi

if ! command -v "$CLI" >/dev/null 2>&1; then
    echo "ERROR: $CLI not on PATH" >&2
    exit 3
fi

case "$CLI" in
    codex)
        timeout "$TIMEOUT" codex exec --skip-git-repo-check -c 'sandbox_mode="read-only"' "$PROMPT" 2>&1
        ;;
    gemini)
        timeout "$TIMEOUT" gemini -m gemini-2.5-pro -p "$PROMPT" 2>&1
        ;;
    cursor-agent)
        timeout "$TIMEOUT" cursor-agent --print --output-format text "$PROMPT" 2>&1
        ;;
    aider)
        # Aider expects a working directory; degrade to chat mode with no file context.
        timeout "$TIMEOUT" aider --no-git --message "$PROMPT" 2>&1
        ;;
    *)
        echo "ERROR: unknown CLI '$CLI'. Supported: codex, gemini, cursor-agent, aider" >&2
        exit 4
        ;;
esac

# Note: standard CLI failure modes (auth expired, quota exhausted) produce non-zero
# exit codes. Callers should check $? and fall through to the next transport.
