#!/usr/bin/env sh
set -eu

usage() {
  cat <<'EOF'
Usage:
  ./scripts/install-skill.sh <skill-name|all> [claude|codex|copilot|gemini|all] [workspace-root]

Examples:
  ./scripts/install-skill.sh all all
  ./scripts/install-skill.sh triage codex .
  ./scripts/install-skill.sh lite-spec copilot /path/to/workspace
  ./scripts/install-skill.sh metaplan gemini /path/to/workspace
  ./scripts/install-skill.sh handoff-prompt all /path/to/workspace
EOF
}

if [ "${1:-}" = "" ] || [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

SKILL_NAME_INPUT="$1"
TARGET_KIND_INPUT="${2:-codex}"
WORKSPACE_ROOT="${3:-.}"

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
SKILLS_DIR="$REPO_ROOT/skills"

if [ ! -d "$SKILLS_DIR" ]; then
  echo "Skills directory not found: $SKILLS_DIR" >&2
  exit 1
fi

copy_skill() {
  skill_name="$1"
  target_base_dir="$2"
  source_dir="$SKILLS_DIR/$skill_name"
  target_dir="$target_base_dir/$skill_name"

  if [ ! -d "$source_dir" ]; then
    echo "Skill not found: $skill_name" >&2
    exit 1
  fi

  if [ ! -f "$source_dir/SKILL.md" ]; then
    echo "Invalid skill '$skill_name': missing $source_dir/SKILL.md" >&2
    exit 1
  fi

  mkdir -p "$target_base_dir"
  rm -rf "$target_dir"
  cp -R "$source_dir" "$target_dir"
  echo "Installed $skill_name -> $target_dir"
}

install_to_kind() {
  skill_name="$1"
  kind="$2"

  case "$kind" in
    claude)
      copy_skill "$skill_name" "$WORKSPACE_ROOT/.claude/skills"
      ;;
    codex)
      copy_skill "$skill_name" "$WORKSPACE_ROOT/.agents/skills"
      ;;
    copilot)
      copy_skill "$skill_name" "$WORKSPACE_ROOT/.github/skills"
      ;;
    gemini)
      copy_skill "$skill_name" "$WORKSPACE_ROOT/.agents/skills"
      ;;
    all)
      copy_skill "$skill_name" "$WORKSPACE_ROOT/.claude/skills"
      copy_skill "$skill_name" "$WORKSPACE_ROOT/.agents/skills"
      copy_skill "$skill_name" "$WORKSPACE_ROOT/.github/skills"
      ;;
    *)
      echo "Invalid target: $kind" >&2
      usage >&2
      exit 1
      ;;
  esac
}

# Validate skill name input (prevent path traversal)
case "$SKILL_NAME_INPUT" in
  all)
    ;;
  .*|*/*|*\\*|*".."*|*[^A-Za-z0-9._-]*)
    echo "Invalid skill name: $SKILL_NAME_INPUT" >&2
    exit 1
    ;;
esac

if [ "$SKILL_NAME_INPUT" = "all" ]; then
  count=0
  # Iterate over all directories in skills/
  for skill_path in "$SKILLS_DIR"/*; do
    if [ -d "$skill_path" ]; then
      # Skip non-skill directories (must contain SKILL.md)
      if [ ! -f "$skill_path/SKILL.md" ]; then continue; fi

      skill_name=$(basename "$skill_path")
      install_to_kind "$skill_name" "$TARGET_KIND_INPUT"
      count=$((count + 1))
    fi
  done
  
  if [ "$count" -eq 0 ]; then
    echo "No valid skills found in $SKILLS_DIR" >&2
    exit 1
  fi
else
  install_to_kind "$SKILL_NAME_INPUT" "$TARGET_KIND_INPUT"
fi
