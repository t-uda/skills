#!/usr/bin/env sh
set -eu

usage() {
  cat <<'EOF'
Usage:
  ./scripts/install-skill.sh <skill-name> [claude|codex|copilot|gemini|both|all] [workspace-root]

Examples:
  ./scripts/install-skill.sh transfer-prompt
  ./scripts/install-skill.sh transfer-prompt codex .
  ./scripts/install-skill.sh transfer-prompt copilot /path/to/workspace
  ./scripts/install-skill.sh transfer-prompt gemini /path/to/workspace
  ./scripts/install-skill.sh transfer-prompt all /path/to/workspace
EOF
}

if [ "${1:-}" = "" ] || [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

SKILL_NAME="$1"
TARGET_KIND="${2:-codex}"
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

install_gemini_compat() {
  gemini_root="$WORKSPACE_ROOT/.gemini"
  gemini_md="$gemini_root/GEMINI.md"
  import_line="@./skills/$SKILL_NAME/SKILL.md"

  copy_skill "$gemini_root/skills"
  mkdir -p "$gemini_root"

  if [ ! -f "$gemini_md" ]; then
    printf '# Gemini project context\n\n%s\n' "$import_line" > "$gemini_md"
    echo "Created $gemini_md"
    return 0
  fi

  if grep -Fqx "$import_line" "$gemini_md"; then
    echo "Gemini import already present in $gemini_md"
    return 0
  fi

  printf '\n%s\n' "$import_line" >> "$gemini_md"
  echo "Updated $gemini_md"
}

case "$TARGET_KIND" in
  claude)
    copy_skill "$WORKSPACE_ROOT/.claude/skills"
    ;;
  codex)
    copy_skill "$WORKSPACE_ROOT/.agents/skills"
    ;;
  copilot)
    copy_skill "$WORKSPACE_ROOT/.github/skills"
    ;;
  gemini)
    install_gemini_compat
    ;;
  both)
    copy_skill "$WORKSPACE_ROOT/.claude/skills"
    copy_skill "$WORKSPACE_ROOT/.agents/skills"
    ;;
  all)
    copy_skill "$WORKSPACE_ROOT/.claude/skills"
    copy_skill "$WORKSPACE_ROOT/.agents/skills"
    copy_skill "$WORKSPACE_ROOT/.github/skills"
    install_gemini_compat
    ;;
  *)
    echo "Invalid target: $TARGET_KIND" >&2
    usage >&2
    exit 1
    ;;
esac
