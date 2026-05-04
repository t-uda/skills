#!/usr/bin/env bash
# Default review acquisition for github-driven-workflow §7.
# Tries Copilot review → @codex mention → Codex CLI artifact in order.
# Override by setting REVIEW_ACQUIRE_SCRIPT to a project-specific implementation.
#
# Usage: acquire-review.sh <OWNER>/<REPO> <PR_NUMBER>
# Exit codes:
#   0  one route succeeded (printed: "route: <name>")
#   1  all routes failed; record an authorized bypass per SKILL.md §7
#   64 usage error
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <OWNER>/<REPO> <PR_NUMBER>" >&2
  exit 64
fi

REPO="$1"
PR="$2"

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: gh not found on PATH" >&2
  exit 1
fi

route_copilot() {
  gh api "repos/${REPO}/pulls/${PR}/requested_reviewers" \
    -X POST --input - <<<'{"reviewers":["copilot-pull-request-reviewer[bot]"]}'
}

route_codex_mention() {
  gh api "repos/${REPO}/issues/${PR}/comments" \
    -X POST -f body='@codex please review this PR'
}

route_codex_cli() {
  command -v codex >/dev/null 2>&1 || return 1
  local tmp
  tmp="$(mktemp)"
  if codex exec "Review PR #${PR} in ${REPO}. Inspect the diff and report concrete findings." >"$tmp" 2>/dev/null \
     && [[ -s "$tmp" ]] \
     && gh pr comment "${PR}" --repo "${REPO}" --body-file "$tmp" >/dev/null 2>&1; then
    rm -f "$tmp"
    return 0
  fi
  rm -f "$tmp"
  return 1
}

if route_copilot >/dev/null 2>&1; then
  echo "route: copilot"
  exit 0
fi
if route_codex_mention >/dev/null 2>&1; then
  echo "route: codex_mention"
  exit 0
fi
if route_codex_cli; then
  echo "route: codex_cli"
  exit 0
fi

echo "ERROR: all review routes failed; record authorized bypass per SKILL.md §7" >&2
exit 1
