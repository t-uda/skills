#!/usr/bin/env bash
# Smoke tests for skills/github-driven-workflow/scripts/acquire-review.py.
#
# Strategy: shadow `gh` with a fake binary on PATH to drive each route
# without touching real GitHub. Verifies usage handling, kind argument
# routing, reviewer-neutral random selection, the dispatch-failed exit
# code, and REVIEW_ACQUIRE_SCRIPT delegation.
set -euo pipefail

# Unset any inherited REVIEW_ACQUIRE_SCRIPT so the bundled-default tests
# do not silently delegate to an installed project override. The override
# delegation path is exercised explicitly by the dedicated cases below.
unset REVIEW_ACQUIRE_SCRIPT

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ACQUIRE="${SCRIPT_DIR}/acquire-review.py"

if [[ ! -x "$ACQUIRE" ]]; then
  echo "FAIL: $ACQUIRE missing or not executable" >&2
  exit 1
fi

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
BIN="${WORK}/bin"
mkdir -p "$BIN"

# Resolve python3 to its real interpreter binary (not a pyenv-style shim
# script) so the hermetic PATH does not need to mirror every helper a shim
# might invoke (grep, sed, tr, awk, sort, cut, …). sys.executable points at
# the underlying binary regardless of how python3 was discovered on $PATH.
PYTHON3_REAL="$(python3 -c 'import sys; print(sys.executable)' 2>/dev/null)"
if [[ -z "$PYTHON3_REAL" || ! -x "$PYTHON3_REAL" ]]; then
  echo "FAIL: could not resolve python3 interpreter binary" >&2
  exit 1
fi
ln -sf "$PYTHON3_REAL" "${BIN}/python3"

for util in mktemp rm cat printf bash sh dirname basename cd echo command; do
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
printf 'argv:%s\n' "\$*" >>"${GH_LOG}"
case "\$*" in
  *requested_reviewers*) exit $1 ;;
  *issues/*comments*)    exit $2 ;;
  *) exit 0 ;;
esac
EOF
  chmod +x "${BIN}/gh"
}

run_acquire() {
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

# --- usage error: no args ---
write_fake_gh 0 0
set +e
PATH="${BIN}" "$ACQUIRE" >/dev/null 2>&1
rc=$?
set -e
check '[[ "$rc" == "64" ]]' "no args ⇒ exit 64"

# --- usage error: too many args ---
set +e
PATH="${BIN}" "$ACQUIRE" owner/repo 1 codex extra >/dev/null 2>&1
rc=$?
set -e
check '[[ "$rc" == "64" ]]' "too many args ⇒ exit 64"

# --- usage error: unknown kind ---
set +e
PATH="${BIN}" "$ACQUIRE" owner/repo 1 nonsense >/dev/null 2>&1
rc=$?
set -e
check '[[ "$rc" == "64" ]]' "unknown kind ⇒ exit 64"

# --- precondition error: gh missing ⇒ exit 127 ---
rm -f "${BIN}/gh"
set +e
PATH="${BIN}" "$ACQUIRE" owner/repo 1 copilot >/dev/null 2>&1
rc=$?
set -e
check '[[ "$rc" == "127" ]]' "gh missing ⇒ exit 127"

# --- explicit kind=copilot succeeds ---
write_fake_gh 0 0
out="$(run_acquire owner/repo 1 copilot)"
check '[[ "$out" == "route: copilot (dispatched)" ]]' "kind=copilot ⇒ route: copilot (dispatched)"
check 'grep -q "argv:.*requested_reviewers" "${GH_LOG}"' "kind=copilot ⇒ requested_reviewers API hit"

# --- explicit kind=codex succeeds ---
write_fake_gh 0 0
out="$(run_acquire owner/repo 1 codex)"
check '[[ "$out" == "route: codex (dispatched)" ]]' "kind=codex ⇒ route: codex (dispatched)"
check 'grep -q "argv:.*issues/.*/comments" "${GH_LOG}"' "kind=codex ⇒ issues comments API hit"

# --- dispatch failure ⇒ exit 1 with bypass hint ---
write_fake_gh 1 1
set +e
out="$(run_acquire owner/repo 1 copilot 2>&1)"
rc=$?
set -e
check '[[ "$rc" == "1" && "$out" == *"record authorized bypass"* ]]' "dispatch failure ⇒ exit 1 with bypass hint"

# --- kind omitted: reviewer-neutral random across {copilot, codex} ---
# Run enough iterations to reliably observe both outcomes. With uniform
# random the probability of seeing only one over 50 trials is ~10^-15.
write_fake_gh 0 0
seen_copilot=0
seen_codex=0
for _ in $(seq 1 50); do
  out="$(run_acquire owner/repo 1)"
  case "$out" in
    "route: copilot (dispatched)") seen_copilot=1 ;;
    "route: codex (dispatched)")   seen_codex=1 ;;
  esac
done
check '[[ "$seen_copilot" -eq 1 && "$seen_codex" -eq 1 ]]' "kind omitted ⇒ random across {copilot, codex} (both observed in 50 runs)"

# --- REVIEW_ACQUIRE_SCRIPT delegation ---
OVERRIDE="${WORK}/override.sh"
cat >"${OVERRIDE}" <<'EOF'
#!/usr/bin/env bash
echo "route: project_override (evidence)"
echo "argv:$*"
exit 0
EOF
chmod +x "${OVERRIDE}"
rm -f "${BIN}/gh"
set +e
out="$(PATH="${BIN}" REVIEW_ACQUIRE_SCRIPT="${OVERRIDE}" "$ACQUIRE" owner/repo 7 2>&1)"
rc=$?
set -e
check '[[ "$rc" == "0" ]]' "REVIEW_ACQUIRE_SCRIPT delegation ⇒ exit 0"
check '[[ "$out" == *"route: project_override (evidence)"* ]]' "REVIEW_ACQUIRE_SCRIPT delegation ⇒ override stdout surfaces"
check '[[ "$out" == *"argv:owner/repo 7"* ]]' "REVIEW_ACQUIRE_SCRIPT delegation ⇒ args forwarded"

# --- delegation forwards optional kind arg ---
set +e
out="$(PATH="${BIN}" REVIEW_ACQUIRE_SCRIPT="${OVERRIDE}" "$ACQUIRE" owner/repo 9 codex 2>&1)"
rc=$?
set -e
check '[[ "$rc" == "0" && "$out" == *"argv:owner/repo 9 codex"* ]]' "REVIEW_ACQUIRE_SCRIPT delegation ⇒ kind arg forwarded"

# --- self-reference safety: REVIEW_ACQUIRE_SCRIPT pointing at the script itself ---
# Must not infinitely exec; falls through to built-in routes.
write_fake_gh 0 0
out="$(PATH="${BIN}" REVIEW_ACQUIRE_SCRIPT="${ACQUIRE}" "$ACQUIRE" owner/repo 1 copilot 2>&1)"
check '[[ "$out" == "route: copilot (dispatched)" ]]' "REVIEW_ACQUIRE_SCRIPT pointing at self ⇒ falls through to built-in"

# --- kind=augment with enabled owner → posts trigger comment, exits 0 ---
write_fake_gh 0 0
set +e
out="$(PATH="${BIN}" AUGMENT_REVIEW_ENABLED_OWNERS="t-uda" run_acquire t-uda/myrepo 42 augment)"
rc=$?
set -e
check '[[ "$rc" == "0" ]]' "kind=augment with enabled owner ⇒ exit 0"
check '[[ "$out" == "route: augment (dispatched)" ]]' "kind=augment with enabled owner ⇒ route: augment (dispatched)"
check 'grep -q "argv:.*issues/42/comments" "${GH_LOG}"' "kind=augment with enabled owner ⇒ issues comments API hit"

# --- kind=augment with disabled owner → exits 1, does NOT call gh ---
: >"${GH_LOG}"
set +e
out="$(PATH="${BIN}" AUGMENT_REVIEW_ENABLED_OWNERS="other-owner" run_acquire t-uda/myrepo 42 augment 2>&1)"
rc=$?
set -e
check '[[ "$rc" == "1" ]]' "kind=augment with disabled owner ⇒ exit 1"
check '[[ "$out" == *"reviewer_not_available: augment is not enabled for owner t-uda"* ]]' "kind=augment with disabled owner ⇒ error message on stderr"
check '! grep -q "argv:" "${GH_LOG}"' "kind=augment with disabled owner ⇒ gh not called"

# --- kind omitted → augment is NOT selected (random pool is {copilot, codex} only) ---
write_fake_gh 0 0
seen_augment=0
for _ in $(seq 1 50); do
  out="$(AUGMENT_REVIEW_ENABLED_OWNERS="t-uda" run_acquire t-uda/myrepo 1)"
  case "$out" in
    "route: augment (dispatched)") seen_augment=1 ;;
  esac
done
check '[[ "$seen_augment" -eq 0 ]]' "kind omitted ⇒ augment never selected in 50 runs (not in random pool)"

# --- dispatch success → prints route: augment (dispatched) ---
write_fake_gh 0 0
out="$(PATH="${BIN}" AUGMENT_REVIEW_ENABLED_OWNERS="t-uda" run_acquire t-uda/myrepo 7 augment)"
check '[[ "$out" == "route: augment (dispatched)" ]]' "augment dispatch success ⇒ prints route: augment (dispatched)"

echo
echo "Result: ${pass} passed, ${fail} failed"
[[ "$fail" -eq 0 ]]
