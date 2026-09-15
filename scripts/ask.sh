#!/usr/bin/env bash
# Stable entry point, including when installed as a symlink.
SCRIPT=$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve().with_name("ask-cli.py"))' "${BASH_SOURCE[0]}") || exit 6
exec python3 "$SCRIPT" "$@"
