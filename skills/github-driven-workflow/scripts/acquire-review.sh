#!/usr/bin/env bash
# Bundled review acquisition for github-driven-workflow §7.
# Tries Copilot review → @codex mention → Codex CLI artifact in order.
#
# Project override: set REVIEW_ACQUIRE_SCRIPT to a project-specific
# implementation; this script will exec it with the same arguments,
# and its exit code / stdout surface unchanged. See this skill's
# README.md for the override contract.
#
# Semantics: exit 0 means a route succeeded, but the printed token
# distinguishes whether evidence is already on the PR.
#   - "route: <name> (dispatched)" — async request sent (reviewer
#     assigned or @codex mention posted). No evidence yet on the PR;
#     the §8 merge gate will not pass on this alone. Caller must wait
#     and re-check, switch routes, or record an authorized bypass.
#   - "route: <name> (evidence)" — synchronous artifact comment was
#     posted on the PR (e.g. Codex CLI). Evidence is durably present
#     and the §8 merge gate can match it directly.
# Whether evidence has accrued for dispatched routes is decided by
# the §8 merge gate, not here.
#
# Usage: scripts/acquire-review.sh <OWNER>/<REPO> <PR_NUMBER>
# Exit codes:
#   0   one route succeeded (printed: "route: <name> (dispatched|evidence)")
#   1   all routes failed; record an authorized bypass per SKILL.md §7
#   64  usage error
#   127 precondition error (e.g. `gh` CLI missing)
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <OWNER>/<REPO> <PR_NUMBER>" >&2
  exit 64
fi

# Project override: delegate fully to $REVIEW_ACQUIRE_SCRIPT when set.
# Compare realpaths to avoid self-recursion if the env var points back
# at this very script.
if [[ -n "${REVIEW_ACQUIRE_SCRIPT:-}" ]]; then
  override_real="$(readlink -f "$REVIEW_ACQUIRE_SCRIPT" 2>/dev/null || true)"
  self_real="$(readlink -f "${BASH_SOURCE[0]}" 2>/dev/null || true)"
  if [[ -n "$override_real" && "$override_real" != "$self_real" ]]; then
    exec "$REVIEW_ACQUIRE_SCRIPT" "$@"
  fi
fi

REPO="$1"
PR="$2"

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: gh not found on PATH" >&2
  exit 127
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
  local raw final
  raw="$(mktemp)"
  final="$(mktemp)"
  trap 'rm -f "$raw" "$final"' RETURN
  if codex exec "Review PR #${PR} in ${REPO}. Inspect the diff and report concrete findings." >"$raw" 2>/dev/null \
     && [[ -s "$raw" ]]; then
    {
      printf '## Codex CLI review\n\n'
      printf 'Reviewed-by: codex-cli\n\n'
      cat "$raw"
    } >"$final"
    gh pr comment "${PR}" --repo "${REPO}" --body-file "$final" >/dev/null 2>&1
    return $?
  fi
  return 1
}

if route_copilot >/dev/null 2>&1; then
  echo "route: copilot (dispatched)"
  exit 0
fi
if route_codex_mention >/dev/null 2>&1; then
  echo "route: codex_mention (dispatched)"
  exit 0
fi
if route_codex_cli; then
  echo "route: codex_cli (evidence)"
  exit 0
fi

echo "ERROR: all review routes failed; record authorized bypass per SKILL.md §7" >&2
exit 1
