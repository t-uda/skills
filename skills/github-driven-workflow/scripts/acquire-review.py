#!/usr/bin/env python3
"""Bundled review acquisition for github-driven-workflow §7.

Picks reviewer-neutrally between {copilot, codex} when kind is omitted, or
honors an explicit kind. Prints ``route: <kind> (dispatched)`` on success.

Project override: set ``REVIEW_ACQUIRE_SCRIPT`` to a project-specific
implementation; this script execs it with the same arguments after unsetting
the env var so re-invocations do not recurse. See this skill's README.md for
the override contract.

Usage: scripts/acquire-review.py <OWNER>/<REPO> <PR_NUMBER> [kind]
  kind: optional, one of {copilot, codex}. Omitted = uniform random pick.

Exit codes:
  0   route succeeded (printed: "route: <kind> (dispatched)")
  1   dispatch failed; record an authorized bypass per SKILL.md §7
  64  usage error
  127 precondition error (e.g. ``gh`` CLI missing)
"""

import os
import random
import shutil
import subprocess
import sys

KINDS = ("copilot", "codex")


def usage(msg=""):
    print(
        f"Usage: {os.path.basename(sys.argv[0])} <OWNER>/<REPO> <PR_NUMBER> [kind]",
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


DISPATCHERS = {"copilot": dispatch_copilot, "codex": dispatch_codex}


def main(argv):
    if len(argv) < 3:
        usage("missing required positional arguments")

    maybe_delegate_override()

    if len(argv) > 4:
        usage("too many arguments")

    repo, pr = argv[1], argv[2]
    kind = argv[3] if len(argv) == 4 else random.choice(KINDS)

    if kind not in DISPATCHERS:
        usage(f"unknown kind: {kind!r} (allowed: {', '.join(KINDS)})")

    if shutil.which("gh") is None:
        print("ERROR: gh not found on PATH", file=sys.stderr)
        return 127

    if DISPATCHERS[kind](repo, pr):
        print(f"route: {kind} (dispatched)")
        return 0

    print(
        "ERROR: review dispatch failed; record authorized bypass per SKILL.md §7",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
