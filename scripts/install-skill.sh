#!/usr/bin/env sh
set -eu

usage() {
  cat <<'EOF'
Usage:
  ./scripts/install-skill.sh <skill-name> [claude|codex|both] [workspace-root]

Examples:
  ./scripts/install-skill.sh transfer-prompt
  ./scripts/install-skill.sh transfer-prompt claude .
  ./scripts/install-skill.sh transfer-prompt both /path/to/workspace
EOF
}

if [ "${1:-}" = "" ] || [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

SKILL_NAME="$1"
TARGET_KIND="${2:-both}"
WORKSPACE_ROOT="${3:-.}"

case "$SKILL_NAME" in
  .*|*/*|*\\*|*".."*|*[^A-Za-z0-9._-]*)
    echo "Invalid skill name: $SKILL_NAME" >&2
    exit 1
    ;;
esac

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
SOURCE_DIR="$REPO_ROOT/skills/$SKILL_NAME"

if [ ! -d "$SOURCE_DIR" ]; then
  echo "Skill not found: $SKILL_NAME" >&2
  exit 1
fi

copy_skill() {
  target_root="$1"
  target_dir="$target_root/$SKILL_NAME"
  mkdir -p "$target_root"
  rm -rf "$target_dir"
  cp -R "$SOURCE_DIR" "$target_dir"
  echo "Installed $SKILL_NAME -> $target_dir"
}

case "$TARGET_KIND" in
  claude)
    copy_skill "$WORKSPACE_ROOT/.claude/skills"
    ;;
  codex)
    copy_skill "$WORKSPACE_ROOT/.agents/skills"
    ;;
  both)
    copy_skill "$WORKSPACE_ROOT/.claude/skills"
    copy_skill "$WORKSPACE_ROOT/.agents/skills"
    ;;
  *)
    echo "Invalid target: $TARGET_KIND" >&2
    usage >&2
    exit 1
    ;;
esac
