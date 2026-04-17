#!/usr/bin/env python3
"""Safely prune merged Git worktrees and local branches."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROTECTED_BRANCHES = {"main", "master", "develop"}


@dataclass
class GitResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


def run_git(args: list[str], cwd: str | Path | None = None) -> GitResult:
    command = ["git", *args]
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd is not None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        errors="surrogateescape",
        check=False,
    )
    return GitResult(command, completed.returncode, completed.stdout, completed.stderr)


def command_text(command: list[str]) -> str:
    return shlex.join(command)


def error_record(
    reason: str,
    command: list[str] | None = None,
    detail: str | None = None,
    target: str | None = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {"reason": reason}
    if target is not None:
        record["target"] = target
    if command is not None:
        record["command"] = command
    if detail:
        record["detail"] = detail.strip()
    return record


def skip_record(
    item_type: str,
    target: str,
    branch: str | None,
    reason: str,
    detail: str | None = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "type": item_type,
        "target": target,
        "branch": branch,
        "reason": reason,
    }
    if detail:
        record["detail"] = detail
    return record


def action_record(
    item_type: str,
    target: str,
    branch: str | None,
    command: list[str],
    reason: str,
    detail: str | None = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "type": item_type,
        "target": target,
        "branch": branch,
        "command": command,
        "reason": reason,
        "status": "planned",
    }
    if detail:
        record["detail"] = detail
    return record


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Safely prune clean merged Git worktrees and merged local branches."
    )
    parser.add_argument("--base", default="origin/main", help="merge target for reachability checks")
    parser.add_argument("--remote", default=None, help="remote used for fetch/prune")
    parser.add_argument("--yes", action="store_true", help="perform cleanup")
    parser.add_argument(
        "--switch-base",
        action="store_true",
        help="switch away from a merged current branch before deleting it",
    )
    parser.add_argument(
        "--include-pattern",
        action="append",
        default=[],
        help="shell-style branch glob to include; repeatable",
    )
    parser.add_argument(
        "--exclude-pattern",
        action="append",
        default=[],
        help="shell-style branch glob to protect; repeatable",
    )
    parser.add_argument("--json", action="store_true", help="print one JSON object")
    parser.add_argument("--no-fetch", action="store_true", help="skip fetch/prune")
    return parser.parse_args(argv)


def base_remote(base: str) -> tuple[str, str] | tuple[None, None]:
    if base.startswith("refs/"):
        return None, None
    remote, sep, branch = base.partition("/")
    if not sep or not remote or not branch:
        return None, None
    return remote, branch


def select_remote(base: str, remote_arg: str | None, repo: str | None = None) -> str:
    remote, _branch = base_remote(base)
    if remote_arg is not None:
        return remote_arg
    if repo is not None and local_branch_exists(repo, base):
        return "origin"
    return remote or "origin"


def discover_repo() -> tuple[str | None, dict[str, Any] | None]:
    result = run_git(["rev-parse", "--show-toplevel"])
    if result.returncode != 0:
        return None, error_record("not_a_git_repo", result.command, result.stderr)
    return result.stdout.strip(), None


def local_branch_exists(repo: str, branch: str) -> bool:
    if not branch:
        return False
    result = run_git(["rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"], repo)
    return result.returncode == 0


def resolve_local_base_branch(repo: str, base: str) -> str | None:
    if base.startswith("refs/heads/"):
        candidate = base.removeprefix("refs/heads/")
        return candidate if local_branch_exists(repo, candidate) else None
    if local_branch_exists(repo, base):
        return base
    _remote, branch = base_remote(base)
    if branch and local_branch_exists(repo, branch):
        return branch
    return None


def resolve_base_commit(repo: str, base: str) -> tuple[str | None, dict[str, Any] | None]:
    result = run_git(["rev-parse", "--verify", f"{base}^{{commit}}"], repo)
    if result.returncode != 0:
        return None, error_record("base_missing", result.command, result.stderr, base)
    return result.stdout.strip(), None


def current_branch(repo: str) -> str | None:
    result = run_git(["branch", "--show-current"], repo)
    if result.returncode != 0:
        return None
    branch = result.stdout.strip()
    return branch or None


def parse_worktrees(output: str) -> list[dict[str, Any]]:
    worktrees: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for token in output.split("\0"):
        if token == "":
            if current is not None:
                worktrees.append(current)
                current = None
            continue

        key, _sep, value = token.partition(" ")
        if key == "worktree":
            if current is not None:
                worktrees.append(current)
            current = {
                "path": value,
                "branch": None,
                "head": None,
                "bare": False,
                "detached": False,
                "locked": False,
                "locked_reason": None,
                "prunable": False,
                "prunable_reason": None,
            }
            continue

        if current is None:
            continue
        if key == "HEAD":
            current["head"] = value
        elif key == "branch":
            current["branch_ref"] = value
            current["branch"] = value.removeprefix("refs/heads/")
        elif key == "bare":
            current["bare"] = True
        elif key == "detached":
            current["detached"] = True
        elif key == "locked":
            current["locked"] = True
            current["locked_reason"] = value or None
        elif key == "prunable":
            current["prunable"] = True
            current["prunable_reason"] = value or None

    if current is not None:
        worktrees.append(current)
    return worktrees


def list_worktrees(repo: str) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    result = run_git(["worktree", "list", "--porcelain", "-z"], repo)
    if result.returncode != 0:
        return [], error_record("worktree_list_failed", result.command, result.stderr)
    return parse_worktrees(result.stdout), None


def list_branches(repo: str) -> tuple[dict[str, dict[str, str]], dict[str, Any] | None]:
    fmt = "%(refname:short)%1f%(objectname)%1f%(upstream:short)%1f%(upstream:track)%1f%(committerdate:iso-strict)%1e"
    result = run_git(["for-each-ref", f"--format={fmt}", "refs/heads"], repo)
    if result.returncode != 0:
        return {}, error_record("branch_list_failed", result.command, result.stderr)

    branches: dict[str, dict[str, str]] = {}
    for raw_record in result.stdout.split("\x1e"):
        record = raw_record.strip("\n")
        if not record:
            continue
        fields = record.split("\x1f")
        while len(fields) < 5:
            fields.append("")
        name, oid, upstream, tracking, committer_date = fields[:5]
        branches[name] = {
            "name": name,
            "object": oid,
            "upstream": upstream,
            "tracking": tracking,
            "committer_date": committer_date,
        }
    return branches, None


def is_merged(repo: str, branch_info: dict[str, str], base_commit: str) -> tuple[bool, dict[str, Any] | None]:
    target = branch_info["object"] or f"refs/heads/{branch_info['name']}"
    result = run_git(["merge-base", "--is-ancestor", target, base_commit], repo)
    if result.returncode == 0:
        return True, None
    if result.returncode == 1:
        return False, None
    return False, error_record("merge_check_failed", result.command, result.stderr, branch_info["name"])


def pattern_matches(branch: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(branch, pattern) for pattern in patterns)


def filter_reason(branch: str, include_patterns: list[str], exclude_patterns: list[str]) -> str | None:
    if pattern_matches(branch, exclude_patterns):
        return "protected"
    if include_patterns and not pattern_matches(branch, include_patterns):
        return "filtered"
    return None


def protected_reason(
    branch: str,
    current: str | None,
    local_base_branch: str | None,
    switch_base: bool,
    exclude_patterns: list[str],
) -> str | None:
    if pattern_matches(branch, exclude_patterns):
        return "protected"
    if branch in PROTECTED_BRANCHES:
        return "protected"
    if local_base_branch and branch == local_base_branch:
        return "protected"
    if current and branch == current and not switch_base:
        return "current_branch"
    return None


def checked_out_branches(worktrees: list[dict[str, Any]], removed_branches: set[str]) -> dict[str, list[str]]:
    checked: dict[str, list[str]] = {}
    for worktree in worktrees:
        branch = worktree.get("branch")
        if not branch or branch in removed_branches:
            continue
        checked.setdefault(branch, []).append(worktree["path"])
    return checked


def worktree_status(repo_path: str) -> tuple[bool, dict[str, Any] | None]:
    result = run_git(["status", "--porcelain=v1", "--untracked-files=normal"], repo_path)
    if result.returncode != 0:
        return False, error_record("status_failed", result.command, result.stderr, repo_path)
    return bool(result.stdout.strip()), None


def prune_metadata_plan(repo: str, execute: bool) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    command = ["worktree", "prune", "--verbose"] if execute else ["worktree", "prune", "--dry-run", "--verbose"]
    result = run_git(command, repo)
    if result.returncode != 0:
        return None, error_record("worktree_prune_failed", result.command, result.stderr)
    detail = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
    if not detail:
        return None, None
    return (
        action_record(
            "prune_metadata",
            repo,
            None,
            result.command,
            "stale_metadata",
            detail,
        ),
        None,
    )


def build_plan(
    repo: str,
    args: argparse.Namespace,
    base_commit: str,
    local_base_branch: str | None,
    initial_branch: str | None,
    branches: dict[str, dict[str, str]],
    worktrees: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    actions: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    merged: dict[str, bool] = {}

    for branch, info in branches.items():
        branch_merged, error = is_merged(repo, info, base_commit)
        merged[branch] = branch_merged
        if error:
            errors.append(error)

    primary_path = worktrees[0]["path"] if worktrees else None
    linked_worktrees = worktrees[1:] if worktrees else []
    remove_worktree_branches: set[str] = set()

    for worktree in linked_worktrees:
        path = worktree["path"]
        branch = worktree.get("branch")
        exists = os.path.exists(path)

        if not exists:
            skipped.append(
                skip_record(
                    "worktree",
                    path,
                    branch,
                    "missing_path",
                    "Run git worktree prune after confirming the path was not moved; use git worktree repair for moved paths.",
                )
            )
            continue
        if worktree.get("locked"):
            skipped.append(skip_record("worktree", path, branch, "locked", worktree.get("locked_reason")))
            continue
        if worktree.get("detached") or not branch:
            skipped.append(skip_record("worktree", path, branch, "detached"))
            continue
        reason = filter_reason(branch, args.include_pattern, args.exclude_pattern)
        if reason:
            skipped.append(skip_record("worktree", path, branch, reason))
            continue
        protected = protected_reason(
            branch,
            initial_branch,
            local_base_branch,
            args.switch_base,
            args.exclude_pattern,
        )
        if protected:
            skipped.append(skip_record("worktree", path, branch, protected))
            continue
        if branch not in branches:
            skipped.append(skip_record("worktree", path, branch, "branch_missing"))
            continue
        if not merged.get(branch, False):
            skipped.append(skip_record("worktree", path, branch, "unmerged"))
            continue
        dirty, error = worktree_status(path)
        if error:
            errors.append(error)
            skipped.append(skip_record("worktree", path, branch, "status_failed"))
            continue
        if dirty:
            skipped.append(skip_record("worktree", path, branch, "dirty"))
            continue
        actions.append(
            action_record(
                "remove_worktree",
                path,
                branch,
                ["git", "worktree", "remove", path],
                "merged_clean_worktree",
            )
        )
        remove_worktree_branches.add(branch)

    checked_after_removal = checked_out_branches(worktrees, remove_worktree_branches)
    switch_planned_for: str | None = None

    for branch, info in branches.items():
        reason = filter_reason(branch, args.include_pattern, args.exclude_pattern)
        if reason:
            skipped.append(skip_record("branch", branch, branch, reason))
            continue
        protected = protected_reason(
            branch,
            initial_branch,
            local_base_branch,
            args.switch_base,
            args.exclude_pattern,
        )
        if protected:
            skipped.append(skip_record("branch", branch, branch, protected))
            continue
        if not merged.get(branch, False):
            skipped.append(skip_record("branch", branch, branch, "unmerged"))
            continue

        if initial_branch and branch == initial_branch and args.switch_base:
            if not local_base_branch:
                skipped.append(
                    skip_record(
                        "branch",
                        branch,
                        branch,
                        "current_branch",
                        "No local base branch is available for --switch-base.",
                    )
                )
                continue
            actions.append(
                action_record(
                    "switch_base",
                    local_base_branch,
                    branch,
                    ["git", "switch", local_base_branch],
                    "current_branch_merged",
                    f"then run git merge --ff-only {args.base}",
                )
            )
            switch_planned_for = branch

        checked_paths = checked_after_removal.get(branch, [])
        if checked_paths and branch != switch_planned_for:
            if primary_path and checked_paths == [primary_path]:
                skipped.append(skip_record("branch", branch, branch, "current_branch"))
            else:
                skipped.append(
                    skip_record(
                        "branch",
                        branch,
                        branch,
                        "checked_out_elsewhere",
                        ", ".join(checked_paths),
                    )
                )
            continue

        actions.append(
            action_record(
                "delete_branch",
                branch,
                branch,
                ["git", "branch", "-d", branch],
                "merged_branch",
            )
        )

    prune_action, prune_error = prune_metadata_plan(repo, execute=False)
    if prune_error:
        errors.append(prune_error)
    if prune_action:
        actions.append(prune_action)

    return actions, skipped, errors


def run_fetch(repo: str, remote: str, dry_run: bool) -> dict[str, Any] | None:
    args = ["fetch", "--prune", remote]
    if dry_run:
        args.insert(1, "--dry-run")
    result = run_git(args, repo)
    if result.returncode == 0:
        return None
    return error_record("fetch_failed", result.command, result.stderr or result.stdout, remote)


def execute_plan(
    repo: str,
    args: argparse.Namespace,
    actions: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
    errors: list[dict[str, Any]],
) -> bool:
    destructive_failed = False

    for action in actions:
        if action["type"] != "switch_base" or action["status"] != "planned":
            continue
        switch_result = run_git(["switch", action["target"]], repo)
        if switch_result.returncode != 0:
            action["status"] = "failed"
            errors.append(error_record("switch_failed", switch_result.command, switch_result.stderr, action["target"]))
            destructive_failed = True
            break
        merge_result = run_git(["merge", "--ff-only", args.base], repo)
        if merge_result.returncode != 0:
            action["status"] = "failed"
            errors.append(error_record("fast_forward_failed", merge_result.command, merge_result.stderr, args.base))
            destructive_failed = True
            break
        action["status"] = "done"

    if destructive_failed:
        return False

    for action in actions:
        if action["type"] != "remove_worktree" or action["status"] != "planned":
            continue
        result = run_git(["worktree", "remove", action["target"]], repo)
        if result.returncode != 0:
            action["status"] = "failed"
            errors.append(error_record("worktree_remove_failed", result.command, result.stderr, action["target"]))
            destructive_failed = True
            break
        action["status"] = "done"

    if destructive_failed:
        return False

    for action in actions:
        if action["type"] != "delete_branch" or action["status"] != "planned":
            continue
        result = run_git(["branch", "-d", action["branch"]], repo)
        if result.returncode != 0:
            action["status"] = "skipped"
            skipped.append(
                skip_record(
                    "branch",
                    action["target"],
                    action["branch"],
                    "delete_refused",
                    result.stderr or result.stdout,
                )
            )
            continue
        action["status"] = "done"

    result = run_git(["worktree", "prune", "--verbose"], repo)
    if result.returncode != 0:
        errors.append(error_record("worktree_prune_failed", result.command, result.stderr))
        return False
    for action in actions:
        if action["type"] == "prune_metadata" and action["status"] == "planned":
            action["status"] = "done"
    return True


def grouped_actions(actions: list[dict[str, Any]], action_type: str, status: str | None) -> list[dict[str, Any]]:
    return [
        action
        for action in actions
        if action["type"] == action_type and (status is None or action.get("status") == status)
    ]


def print_action_lines(actions: list[dict[str, Any]]) -> None:
    for action in actions:
        branch = f" ({action['branch']})" if action.get("branch") else ""
        detail = f" - {action['detail']}" if action.get("detail") else ""
        print(f"- {action['target']}{branch}: {command_text(action['command'])}{detail}")


def print_skips(skipped: list[dict[str, Any]]) -> None:
    for item in skipped:
        branch = f" ({item['branch']})" if item.get("branch") else ""
        detail = f" - {item['detail']}" if item.get("detail") else ""
        print(f"- {item['type']} {item['target']}{branch}: {item['reason']}{detail}")


def print_errors(errors: list[dict[str, Any]]) -> None:
    for item in errors:
        command = f" [{command_text(item['command'])}]" if item.get("command") else ""
        target = f" {item['target']}" if item.get("target") else ""
        detail = f": {item['detail']}" if item.get("detail") else ""
        print(f"- {item['reason']}{target}{command}{detail}")


def print_summary(
    args: argparse.Namespace,
    actions: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    final_branch: str | None,
) -> None:
    dry_run = not args.yes
    if dry_run:
        sections = [
            ("Would switch", grouped_actions(actions, "switch_base", "planned")),
            ("Would remove", grouped_actions(actions, "remove_worktree", "planned")),
            ("Would delete", grouped_actions(actions, "delete_branch", "planned")),
            ("Would prune", grouped_actions(actions, "prune_metadata", "planned")),
        ]
    else:
        sections = [
            ("Switched", grouped_actions(actions, "switch_base", "done")),
            ("Removed", grouped_actions(actions, "remove_worktree", "done")),
            ("Deleted", grouped_actions(actions, "delete_branch", "done")),
            ("Pruned", grouped_actions(actions, "prune_metadata", "done")),
        ]

    print("Mode: dry-run" if dry_run else "Mode: yes")
    for title, items in sections:
        if not items:
            continue
        print(f"\n{title}")
        print_action_lines(items)

    if skipped:
        print("\nSkipped")
        print_skips(skipped)
    if errors:
        print("\nErrors")
        print_errors(errors)
    if dry_run and any(error["reason"] == "fetch_failed" for error in errors):
        print("\nPlan may be stale because fetch failed.")
    print(f"\nFinal branch: {final_branch or '(detached)'}")


def emit_result(
    args: argparse.Namespace,
    repo: str | None,
    base_commit: str | None,
    local_base_branch: str | None,
    remote: str,
    initial_branch: str | None,
    actions: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    final_branch: str | None,
) -> None:
    if args.json:
        print(
            json.dumps(
                {
                    "mode": "yes" if args.yes else "dry-run",
                    "repo": repo,
                    "base": {
                        "ref": args.base,
                        "commit": base_commit,
                        "local_branch": local_base_branch,
                    },
                    "remote": remote,
                    "current_branch": initial_branch,
                    "actions": actions,
                    "skipped": skipped,
                    "errors": errors,
                    "final_branch": final_branch,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print_summary(args, actions, skipped, errors, final_branch)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    remote = select_remote(args.base, args.remote)
    repo, repo_error = discover_repo()
    if repo_error:
        emit_result(args, None, None, None, remote, None, [], [], [repo_error], None)
        return 2
    assert repo is not None

    remote = select_remote(args.base, args.remote, repo)
    initial_branch = current_branch(repo)
    fetch_error = None
    if not args.no_fetch:
        fetch_error = run_fetch(repo, remote, dry_run=not args.yes)
        if fetch_error and args.yes:
            emit_result(args, repo, None, None, remote, initial_branch, [], [], [fetch_error], initial_branch)
            return 1

    base_commit, base_error = resolve_base_commit(repo, args.base)
    local_base_branch = resolve_local_base_branch(repo, args.base)
    if base_error:
        emit_result(args, repo, None, local_base_branch, remote, initial_branch, [], [], [base_error], initial_branch)
        return 2
    assert base_commit is not None

    if args.yes and args.switch_base and not local_base_branch:
        error = error_record(
            "local_base_missing",
            detail=f"Create or check out a local branch for base {args.base!r} before using --switch-base.",
        )
        emit_result(args, repo, base_commit, local_base_branch, remote, initial_branch, [], [], [error], initial_branch)
        return 2

    worktrees, worktree_error = list_worktrees(repo)
    branches, branch_error = list_branches(repo)
    discovery_errors = [error for error in (fetch_error, worktree_error, branch_error) if error]
    if worktree_error or branch_error:
        emit_result(
            args,
            repo,
            base_commit,
            local_base_branch,
            remote,
            initial_branch,
            [],
            [],
            discovery_errors,
            initial_branch,
        )
        return 2

    actions, skipped, plan_errors = build_plan(
        repo,
        args,
        base_commit,
        local_base_branch,
        initial_branch,
        branches,
        worktrees,
    )
    errors = [*discovery_errors, *plan_errors]

    ok = True
    if args.yes:
        ok = execute_plan(repo, args, actions, skipped, errors)

    final_branch = current_branch(repo)
    emit_result(
        args,
        repo,
        base_commit,
        local_base_branch,
        remote,
        initial_branch,
        actions,
        skipped,
        errors,
        final_branch,
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
