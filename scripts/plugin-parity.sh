#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)

# Compatibility entry point. Fleet policy and audit behavior live in fleet.toml
# and scripts/fleet.py; keep this filename for existing operator muscle memory.
if [ -n "${FLEET_HOSTS:-}" ]; then
  exec python3 "$ROOT/scripts/fleet.py" audit --hosts "$FLEET_HOSTS" "$@"
fi
exec python3 "$ROOT/scripts/fleet.py" audit "$@"
