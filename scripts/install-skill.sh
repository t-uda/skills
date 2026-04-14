#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if command -v python3 >/dev/null 2>&1; then
  exec python3 "$SCRIPT_DIR/install_skill.py" "$@"
fi

if command -v uv >/dev/null 2>&1; then
  exec uv run "$SCRIPT_DIR/install_skill.py" "$@"
fi

echo "install-skill.sh requires python3 or uv." >&2
exit 1
