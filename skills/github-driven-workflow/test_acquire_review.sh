#!/usr/bin/env bash
# Smoke tests for skills/github-driven-workflow/acquire-review.sh.
#
# Strategy: shadow `gh` and `codex` with fake binaries on PATH to drive
# each route without touching real GitHub. Verifies usage handling, route
# selection, and the all-routes-failed exit code.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ACQUIRE="${SCRIPT_DIR}/acquire-review.sh"

if [[ ! -x "$ACQUIRE" ]]; then
  echo "FAIL: $ACQUIRE missing or not executable" >&2
  exit 1
fi

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
BIN="${WORK}/bin"
mkdir -p "$BIN"

# Provide minimal POSIX utilities the script needs (mktemp, rm, cat, etc).
for util in mktemp rm cat printf bash sh dirname cd echo command; do
  if real="$(command -v "$util")"; then
    ln -sf "$real" "${BIN}/${util}"
  fi
done

GH_LOG="${WORK}/gh.log"

write_fake_gh() {
  # $1: copilot api outcome (0=success, nonzero=failure)
  # $2: codex-mention outcome (0=success, nonzero=failure)
  : >"${GH_LOG}"
  cat >"${BIN}/gh" <<EOF
#!/usr/bin/env bash
{
  printf 'argv:%s\n' "\$*"
  if [[ "\$*" == *"--body-file"* ]]; then
    for arg in "\$@"; do :; done
    # Find the body-file arg and append its contents under a marker.
    while [[ \$# -gt 0 ]]; do
      if [[ "\$1" == "--body-file" ]]; then
        printf 'body-file:\n'
        cat "\$2" 2>/dev/null
        printf 'body-end\n'
        break
      fi
      shift
    done
  fi
} >>"${GH_LOG}"
case "\$*" in
  *requested_reviewers*) exit $1 ;;
  *issues/*comments*)    exit $2 ;;
  *pr*comment*)          exit 0 ;;
  *) exit 0 ;;
esac
EOF
  chmod +x "${BIN}/gh"
}

remove_codex() {
  rm -f "${BIN}/codex"
}

run_acquire() {
  # Hermetic PATH — only what we placed in $BIN — to keep host-installed
  # `codex` from being discovered in the negative test cases.
  PATH="${BIN}" "$ACQUIRE" "$@"
}

pass=0
fail=0
check() {
  if eval "$1"; then
    pass=$((pass + 1))
    echo "ok: $2"
  else
    fail=$((fail + 1))
    echo "FAIL: $2" >&2
  fi
}

# --- usage error ---
write_fake_gh 0 0; remove_codex
set +e
PATH="${BIN}" "$ACQUIRE" >/dev/null 2>&1
rc=$?
set -e
check '[[ "$rc" == "64" ]]' "no args ⇒ exit 64"

# --- precondition error: gh missing ⇒ exit 127 ---
rm -f "${BIN}/gh"; remove_codex
set +e
PATH="${BIN}" "$ACQUIRE" owner/repo 1 >/dev/null 2>&1
rc=$?
set -e
check '[[ "$rc" == "127" ]]' "gh missing ⇒ exit 127"

# --- copilot route succeeds ---
write_fake_gh 0 0; remove_codex
out="$(run_acquire owner/repo 1)"
check '[[ "$out" == *"route: copilot (dispatched)"* ]]' "copilot success ⇒ route: copilot (dispatched)"

# --- copilot fails, codex_mention succeeds ---
write_fake_gh 1 0; remove_codex
out="$(run_acquire owner/repo 1)"
check '[[ "$out" == *"route: codex_mention (dispatched)"* ]]' "copilot 422 ⇒ codex_mention (dispatched)"

# --- both gh routes fail, no codex CLI ⇒ exit 1 ---
write_fake_gh 1 1; remove_codex
set +e
out="$(run_acquire owner/repo 1 2>&1)"
rc=$?
set -e
check '[[ "$rc" == "1" && "$out" == *"all review routes failed"* ]]' "all routes fail ⇒ exit 1 with bypass hint"

# --- both gh routes fail, codex CLI present and succeeds ---
write_fake_gh 1 1
cat >"${BIN}/codex" <<'EOF'
#!/usr/bin/env bash
echo "Codex CLI review artifact"
EOF
chmod +x "${BIN}/codex"
out="$(run_acquire owner/repo 1)"
check '[[ "$out" == *"route: codex_cli (evidence)"* ]]' "codex CLI fallback ⇒ route: codex_cli (evidence)"
check 'grep -q "argv:.*pr comment.*--body-file" "${GH_LOG}"' "codex CLI fallback ⇒ gh pr comment invoked with --body-file"
check 'grep -q "## Codex CLI review" "${GH_LOG}"' "codex CLI body has 'Codex CLI review' header"
check 'grep -q "Reviewed-by: codex-cli" "${GH_LOG}"' "codex CLI body has 'Reviewed-by: codex-cli' line"
check 'grep -q "Codex CLI review artifact" "${GH_LOG}"' "codex CLI body contains the artifact"

echo
echo "Result: ${pass} passed, ${fail} failed"
[[ "$fail" -eq 0 ]]
