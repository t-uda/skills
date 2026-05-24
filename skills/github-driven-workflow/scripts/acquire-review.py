#!/usr/bin/env python3
"""Bundled review acquisition for github-driven-workflow §7.

Picks reviewer-neutrally between {copilot, codex} when kind is omitted, or
honors an explicit kind. Prints ``route: <kind> (dispatched)`` on success.

Project override: set ``REVIEW_ACQUIRE_SCRIPT`` to a project-specific
implementation; this script execs it with the same arguments after unsetting
the env var so re-invocations do not recurse. See this skill's README.md for
the override contract.

Usage: scripts/acquire-review.py <OWNER>/<REPO> <PR_NUMBER> [kind]
  kind: optional, one of {copilot, codex, augment}. Omitted = uniform random
        pick from {copilot, codex}. ``augment`` is never in the random pool;
        it must be requested explicitly.

        ``augment`` requires the repo owner to be listed in the
        ``AUGMENT_REVIEW_ENABLED_OWNERS`` environment variable (comma-separated
        list of owner names, e.g. ``t-uda``). If the env var is missing/empty
        or the owner is not listed, the script exits 1 before calling ``gh``.

Exit codes:
  0   route succeeded (printed: "route: <kind> (dispatched)")
  1   dispatch failed or availability guard rejected; record an authorized
      bypass per SKILL.md §7
  64  usage error
  127 precondition error (e.g. ``gh`` CLI missing)
"""

import os
import random
import shutil
import subprocess
import sys

KINDS = ("copilot", "codex")
AUGMENT_TRIGGER = "auggie review"


def usage(msg=""):
    print(
        f"Usage: {os.path.basename(sys.argv[0])} <OWNER>/<REPO> <PR_NUMBER> [kind]",
        file=sys.stderr,
    )
    print(
        f"  kind: one of {{{', '.join((*KINDS, 'augment'))}}}; omit for random pick from {{{', '.join(KINDS)}}}",
        file=sys.stderr,
    )
    if msg:
        print(msg, file=sys.stderr)
    sys.exit(64)


def maybe_delegate_override():
    override = os.environ.get("REVIEW_ACQUIRE_SCRIPT")
    if not override:
        return
    env = os.environ.copy()
    env.pop("REVIEW_ACQUIRE_SCRIPT", None)
    os.execvpe(override, [override, *sys.argv[1:]], env)


def dispatch_copilot(repo, pr):
    return subprocess.run(
        [
            "gh", "api",
            f"repos/{repo}/pulls/{pr}/requested_reviewers",
            "-X", "POST",
            "--input", "-",
        ],
        input='{"reviewers":["copilot-pull-request-reviewer[bot]"]}',
        text=True,
        capture_output=True,
    ).returncode == 0


def dispatch_codex(repo, pr):
    return subprocess.run(
        [
            "gh", "api",
            f"repos/{repo}/issues/{pr}/comments",
            "-X", "POST",
            "-f", "body=@codex please review this PR",
        ],
        capture_output=True,
        text=True,
    ).returncode == 0


def check_augment_availability(owner):
    """Return True if augment is enabled for the given owner, False otherwise.

    Reads AUGMENT_REVIEW_ENABLED_OWNERS (comma-separated owner list). Returns
    False when the env var is missing, empty, or the owner is not listed.
    """
    raw = os.environ.get("AUGMENT_REVIEW_ENABLED_OWNERS", "")
    enabled_owners = {o.strip() for o in raw.split(",") if o.strip()}
    return owner in enabled_owners


class AugmentUnavailable(Exception):
    """Raised when the augment availability guard rejects the request."""


def dispatch_augment(repo, pr):
    owner = repo.split("/")[0]
    if not check_augment_availability(owner):
        raise AugmentUnavailable(owner)
    return subprocess.run(
        [
            "gh", "api",
            f"repos/{repo}/issues/{pr}/comments",
            "-X", "POST",
            "-f", f"body={AUGMENT_TRIGGER}",
        ],
        capture_output=True,
        text=True,
    ).returncode == 0


DISPATCHERS = {"copilot": dispatch_copilot, "codex": dispatch_codex, "augment": dispatch_augment}


def main(argv):
    if len(argv) < 3:
        usage("missing required positional arguments")

    maybe_delegate_override()

    if len(argv) > 4:
        usage("too many arguments")

    repo, pr = argv[1], argv[2]
    kind = argv[3] if len(argv) == 4 else random.choice(KINDS)

    all_kinds = (*KINDS, "augment")
    if kind not in DISPATCHERS:
        usage(f"unknown kind: {kind!r} (allowed: {', '.join(all_kinds)})")

    if kind == "augment":
        owner = repo.split("/")[0]
        if not check_augment_availability(owner):
            print(
                f"ERROR: reviewer_not_available: augment is not enabled for owner {owner}",
                file=sys.stderr,
            )
            return 1

    if shutil.which("gh") is None:
        print("ERROR: gh not found on PATH", file=sys.stderr)
        return 127

    try:
        dispatched = DISPATCHERS[kind](repo, pr)
    except AugmentUnavailable as exc:
        owner = str(exc)
        print(
            f"ERROR: reviewer_not_available: augment is not enabled for owner {owner}",
            file=sys.stderr,
        )
        return 1

    if dispatched:
        print(f"route: {kind} (dispatched)")
        return 0

    print(
        "ERROR: review dispatch failed; record authorized bypass per SKILL.md §7",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
