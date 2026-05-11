#!/usr/bin/env python3
"""Workspace-level Git cleanup janitor.

Cleans merged local branches, merged linked worktrees, stale remote-tracking
refs, and stale worktree metadata across one or more repositories under a
workspace root. The script is the source of truth for cleanup eligibility;
calling agents only choose a mode (default / --yes / --interactive / --dry-run)
and do not make per-item judgments.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable


PROTECTED_BRANCHES = {"main", "master", "develop"}

DISCOVERY_SKIP_DIRS = {
    ".venv", "node_modules", ".tox", ".cache", "dist", "build",
    ".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "target", "coverage", "htmlcov",
}

DEFAULT_GARBAGE_GLOBS = [
    "*.log", "*.tmp", "*.swp", "*.swo", "*.pyc",
    ".DS_Store", "Thumbs.db",
    "__pycache__/**", ".pytest_cache/**", ".mypy_cache/**", ".ruff_cache/**",
    "node_modules/**", "dist/**", "build/**", "target/**",
    ".venv/**", ".tox/**", ".cache/**",
    "coverage/**", ".coverage", "htmlcov/**",
]

LARGE_FILE_THRESHOLD = 10 * 1024 * 1024  # 10 MiB
ISSUE_BRANCH_PREFIX_RE = re.compile(r"^(issue-\d+)(?:$|[-_/])")


# ---------------------------------------------------------------------------
# Subprocess helpers
# ---------------------------------------------------------------------------


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


def git_args(command: list[str]) -> list[str]:
    return command[1:] if command and command[0] == "git" else command


# ---------------------------------------------------------------------------
# Records
# ---------------------------------------------------------------------------


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
    kind: str,
    target: str,
    branch: str | None,
    commands: list[list[str]],
    reason: str,
    detail: str | None = None,
    *,
    klass: str | None = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "kind": kind,
        "target": target,
        "branch": branch,
        "command": commands[0] if commands else [],
        "commands": commands,
        "reason": reason,
        "status": "planned",
    }
    if detail:
        record["detail"] = detail
    if klass:
        record["class"] = klass
    return record


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Workspace-level Git cleanup janitor. Discovers repositories under "
            "--root and cleans merged worktrees, merged branches, stale refs, "
            "and stale metadata."
        ),
    )
    parser.add_argument("--root", default=None, help="workspace root (default: cwd)")
    parser.add_argument(
        "--repo",
        action="append",
        default=[],
        help="restrict cleanup to this repository; repeatable; bypasses discovery",
    )
    parser.add_argument("--max-depth", type=int, default=4, help="discovery depth (default: 4)")
    parser.add_argument("--base", default="origin/main", help="merge target (default: origin/main)")
    parser.add_argument("--remote", default=None, help="remote (default: origin)")
    parser.add_argument("--dry-run", action="store_true", help="plan only; no mutation")
    parser.add_argument(
        "--yes", action="store_true",
        help="non-interactive; execute Class A and Class B without prompting",
    )
    parser.add_argument(
        "--interactive", action="store_true",
        help="allow one consolidated y/N prompt for Class B",
    )
    parser.add_argument("--no-fetch", action="store_true", help="skip fetch/prune")
    parser.add_argument("--no-update-base", action="store_true", help="skip base branch fast-forward")
    parser.add_argument(
        "--process-policy", choices=("skip", "ask", "ignore"), default="skip",
        help="how to treat worktrees held by live processes (default: skip)",
    )
    parser.add_argument(
        "--garbage-glob", action="append", default=[],
        help="repeatable; extend the disposable-glob list (additive only)",
    )
    parser.add_argument("--json", action="store_true", help="emit one JSON object")
    return parser.parse_args(argv)


def resolve_mode(args: argparse.Namespace) -> str:
    if args.dry_run:
        return "dry-run"
    if args.yes and args.interactive:
        # Defensive: argparse cannot easily express mutual exclusion for two
        # store_true flags without losing default semantics, so check here.
        raise SystemExit("error: --yes and --interactive are mutually exclusive")
    if args.yes:
        return "yes"
    if args.interactive:
        return "interactive"
    return "default"


# ---------------------------------------------------------------------------
# Repository discovery
# ---------------------------------------------------------------------------


def repo_common_dir(path: Path) -> str | None:
    result = run_git(["rev-parse", "--git-common-dir"], path)
    if result.returncode != 0:
        return None
    common = result.stdout.strip()
    common_path = Path(common)
    if not common_path.is_absolute():
        common_path = (path / common_path).resolve()
    return str(common_path.resolve())


def is_repo_root(path: Path) -> bool:
    return (path / ".git").exists()


def discover_repositories(root: Path, max_depth: int) -> list[Path]:
    """Discover Git repositories under root.

    Workspace contract: when subordinate repositories exist, operate on those;
    only fall back to the root repo when walk finds no subordinate matches.
    """
    candidates: list[Path] = []

    def walk(d: Path, depth: int) -> None:
        if depth > max_depth:
            return
        try:
            entries = sorted(d.iterdir())
        except (OSError, PermissionError):
            return
        for entry in entries:
            if entry.is_symlink() or not entry.is_dir():
                continue
            if entry.name in DISCOVERY_SKIP_DIRS:
                continue
            if is_repo_root(entry):
                candidates.append(entry.resolve())
                continue  # do not descend further into a found repo
            walk(entry, depth + 1)

    walk(root, 1)

    # Single-repo fallback: only treat root as a repo when no subordinate
    # repositories were found. Otherwise running from inside a repo that
    # contains nested repositories would unexpectedly clean both.
    if not candidates and is_repo_root(root):
        candidates.append(root.resolve())

    # Deduplicate by common git dir; prefer candidates where .git is a directory
    # (the primary worktree) over linked-worktree candidates whose .git is a file.
    by_id: dict[str, Path] = {}
    for candidate in candidates:
        rid = repo_common_dir(candidate)
        if rid is None:
            continue
        marker = candidate / ".git"
        is_primary = marker.is_dir()
        existing = by_id.get(rid)
        if existing is None:
            by_id[rid] = candidate
            continue
        existing_primary = (existing / ".git").is_dir()
        if is_primary and not existing_primary:
            by_id[rid] = candidate

    return sorted(by_id.values(), key=lambda p: str(p))


# ---------------------------------------------------------------------------
# Repo-level helpers (preserved from prior implementation)
# ---------------------------------------------------------------------------


def base_remote(base: str) -> tuple[str, str] | tuple[None, None]:
    if base.startswith("refs/"):
        return None, None
    remote, sep, branch = base.partition("/")
    if not sep or not remote or not branch:
        return None, None
    return remote, branch


def select_remote(base: str, remote_arg: str | None, repo: Path | None = None) -> str:
    remote, _branch = base_remote(base)
    if remote_arg is not None:
        return remote_arg
    if repo is not None and local_branch_exists(repo, base):
        return "origin"
    return remote or "origin"


def local_branch_exists(repo: Path, branch: str) -> bool:
    if not branch:
        return False
    result = run_git(["rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"], repo)
    return result.returncode == 0


def resolve_local_base_branch(repo: Path, base: str) -> str | None:
    if base.startswith("refs/heads/"):
        candidate = base.removeprefix("refs/heads/")
        return candidate if local_branch_exists(repo, candidate) else None
    if local_branch_exists(repo, base):
        return base
    _remote, branch = base_remote(base)
    if branch and local_branch_exists(repo, branch):
        return branch
    return None


def resolve_base_commit(repo: Path, base: str) -> tuple[str | None, dict[str, Any] | None]:
    result = run_git(["rev-parse", "--verify", f"{base}^{{commit}}"], repo)
    if result.returncode != 0:
        return None, error_record("base_missing", result.command, result.stderr, base)
    return result.stdout.strip(), None


def current_branch(repo: Path) -> str | None:
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


def list_worktrees(repo: Path) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    result = run_git(["worktree", "list", "--porcelain", "-z"], repo)
    if result.returncode != 0:
        return [], error_record("worktree_list_failed", result.command, result.stderr)
    return parse_worktrees(result.stdout), None


def list_branches(repo: Path) -> tuple[dict[str, dict[str, str]], dict[str, Any] | None]:
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


def is_merged(repo: Path, branch_info: dict[str, str], base_commit: str) -> tuple[bool, dict[str, Any] | None]:
    target = branch_info["object"] or f"refs/heads/{branch_info['name']}"
    result = run_git(["merge-base", "--is-ancestor", target, base_commit], repo)
    if result.returncode == 0:
        return True, None
    if result.returncode == 1:
        return False, None
    return False, error_record("merge_check_failed", result.command, result.stderr, branch_info["name"])


def parse_github_url(url: str) -> tuple[str, str] | None:
    if "github.com" not in url:
        return None
    path: str | None = None
    for prefix in (
        "https://github.com/",
        "http://github.com/",
        "ssh://git@github.com/",
        "git@github.com:",
    ):
        if url.startswith(prefix):
            path = url[len(prefix):]
            break
    if path is None:
        return None
    if path.endswith(".git"):
        path = path[:-4]
    parts = path.strip("/").split("/")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return None
    return parts[0], parts[1]


def discover_github_repo(repo: Path, remote: str) -> tuple[str, str] | None:
    result = run_git(["remote", "get-url", remote], repo)
    if result.returncode != 0:
        return None
    return parse_github_url(result.stdout.strip())


def gh_available() -> bool:
    try:
        completed = subprocess.run(
            ["gh", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except (FileNotFoundError, OSError):
        return False
    return completed.returncode == 0


def base_branch_name(base: str) -> str:
    if base.startswith("refs/heads/"):
        return base.removeprefix("refs/heads/")
    _remote, branch = base_remote(base)
    return branch or base


def issue_branch_prefix(branch: str) -> str | None:
    match = ISSUE_BRANCH_PREFIX_RE.match(branch)
    if match is None:
        return None
    return match.group(1)


def issue_branch_head_search(prefix: str) -> str:
    return f"head:{prefix}"


def gh_list_merged_prs(
    repo: Path,
    owner: str,
    name: str,
    base: str,
    *,
    head: str | None = None,
    search: str | None = None,
) -> tuple[list[dict[str, Any]] | None, dict[str, Any] | None]:
    command = [
        "gh", "pr", "list",
        "--repo", f"{owner}/{name}",
        "--state", "merged",
        "--base", base,
        "--json", "number,headRefName,headRefOid",
        "--limit", "100",
    ]
    if head is not None:
        command.extend(["--head", head])
    if search is not None:
        command.extend(["--search", search])
    try:
        completed = subprocess.run(
            command,
            cwd=str(repo),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            check=False,
        )
    except (FileNotFoundError, OSError) as exc:
        branch = head if head is not None else search or ""
        return None, error_record("pr_check_failed", command, str(exc), branch)
    if completed.returncode != 0:
        branch = head if head is not None else search or ""
        return None, error_record("pr_check_failed", command, completed.stderr, branch)
    try:
        items = json.loads(completed.stdout or "[]")
    except json.JSONDecodeError as exc:
        branch = head if head is not None else search or ""
        return None, error_record("pr_check_failed", command, str(exc), branch)
    if not isinstance(items, list):
        branch = head if head is not None else search or ""
        return None, error_record("pr_check_failed", command, "invalid gh response", branch)
    return items, None


def pr_merged_via_gh(
    repo: Path,
    owner: str,
    name: str,
    branch: str,
    branch_oid: str,
    base: str,
    remote: str = "origin",
) -> tuple[int | None, dict[str, Any] | None]:
    """Look up a merged PR for `branch` and verify the local tip is incorporated.

    Three sub-checks (preserved): exact OID match, tree equality, ancestry.
    Returns (pr_number, error). pr_number=None means no qualifying PR.
    """
    items, error = gh_list_merged_prs(
        repo, owner, name, base, head=branch,
    )
    if error is not None or items is None:
        return None, error

    if not items:
        prefix = issue_branch_prefix(branch)
        if prefix is not None:
            search_items, error = gh_list_merged_prs(
                repo, owner, name, base, search=issue_branch_head_search(prefix),
            )
            if error is not None or search_items is None:
                return None, error
            items = [
                item
                for item in search_items
                if isinstance(item, dict)
                and issue_branch_prefix(str(item.get("headRefName", ""))) == prefix
            ]

    oid_mismatch_candidates: list[tuple[int, str]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        pr_head_oid = item.get("headRefOid", "")
        number = item.get("number")
        if not isinstance(number, int) or not pr_head_oid:
            continue
        if pr_head_oid == branch_oid:
            return number, None
        oid_mismatch_candidates.append((number, pr_head_oid))

    for number, pr_head_oid in oid_mismatch_candidates:
        fetch_result = run_git(["fetch", remote, pr_head_oid], repo)
        if fetch_result.returncode != 0:
            continue
        local_tree = run_git(["rev-parse", f"{branch_oid}^{{tree}}"], repo)
        pr_tree = run_git(["rev-parse", f"{pr_head_oid}^{{tree}}"], repo)
        if (
            local_tree.returncode == 0
            and pr_tree.returncode == 0
            and local_tree.stdout.strip() == pr_tree.stdout.strip()
        ):
            return number, None
        ancestor_result = run_git(["merge-base", "--is-ancestor", branch_oid, pr_head_oid], repo)
        if ancestor_result.returncode == 0:
            return number, None

    return None, None


def protected_reason(
    branch: str,
    initial_branch: str | None,
    local_base_branch: str | None,
) -> str | None:
    if branch in PROTECTED_BRANCHES:
        return "protected"
    if local_base_branch and branch == local_base_branch:
        return "protected"
    if initial_branch and branch == initial_branch:
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


# ---------------------------------------------------------------------------
# Process probes
# ---------------------------------------------------------------------------


@dataclass
class ProbeResult:
    state: str  # "clear" | "held" | "unavailable"
    detail: str | None = None


def _proc_holders(target: Path) -> tuple[bool, list[str]]:
    """Return (probe_available, holders) using /proc/*/cwd on Linux."""
    proc = Path("/proc")
    if not proc.is_dir():
        return False, []
    holders: list[str] = []
    target_resolved = target.resolve()
    try:
        entries = list(proc.iterdir())
    except OSError:
        return False, []
    for entry in entries:
        if not entry.name.isdigit():
            continue
        cwd_link = entry / "cwd"
        try:
            cwd = cwd_link.resolve(strict=True)
        except (OSError, PermissionError, FileNotFoundError):
            continue
        try:
            cwd.relative_to(target_resolved)
        except ValueError:
            continue
        try:
            comm = (entry / "comm").read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            comm = "?"
        holders.append(f"pid {entry.name} ({comm})")
    return True, holders


def _lsof_held(target: Path) -> tuple[bool, bool]:
    """Return (probe_ran, held). probe_ran=False if lsof is missing."""
    if shutil.which("lsof") is None:
        return False, False
    try:
        completed = subprocess.run(
            ["lsof", "+D", str(target)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            encoding="utf-8", check=False,
        )
    except (OSError, FileNotFoundError):
        return False, False
    if completed.returncode not in (0, 1):
        return False, False
    lines = [ln for ln in completed.stdout.splitlines()[1:] if ln.strip()]
    return True, bool(lines)


def _fuser_held(target: Path) -> tuple[bool, bool]:
    if shutil.which("fuser") is None:
        return False, False
    try:
        completed = subprocess.run(
            ["fuser", "-m", str(target)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            encoding="utf-8", check=False,
        )
    except (OSError, FileNotFoundError):
        return False, False
    if completed.returncode not in (0, 1):
        return False, False
    pids = completed.stdout.split()
    return True, bool(pids)


def _tmux_holders(target: Path) -> list[str]:
    if shutil.which("tmux") is None:
        return []
    try:
        completed = subprocess.run(
            ["tmux", "list-panes", "-a", "-F", "#{pane_current_path}\t#{pane_current_command}"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            encoding="utf-8", check=False,
        )
    except (OSError, FileNotFoundError):
        return []
    if completed.returncode != 0:
        return []
    target_resolved = target.resolve()
    holders: list[str] = []
    for line in completed.stdout.splitlines():
        if not line.strip():
            continue
        path_str, _tab, cmd = line.partition("\t")
        try:
            pane_path = Path(path_str).resolve()
            pane_path.relative_to(target_resolved)
        except (ValueError, OSError):
            continue
        holders.append(f"tmux pane in {cmd or '?'}")
    return holders


def process_probe_real(worktree_path: str) -> ProbeResult:
    """Probe for processes holding the worktree by cwd or open files.

    /proc/*/cwd covers cwd-based holders. lsof/fuser cover open-file holders
    that may have a cwd elsewhere. When both are available we run them and
    union the results so editors and language servers with files open in the
    worktree are detected even if the editor was launched from elsewhere.
    """
    target = Path(worktree_path)
    if not target.exists():
        return ProbeResult("unavailable", "path missing")

    holders: list[str] = []
    primary_ran = False

    proc_ok, proc_holders = _proc_holders(target)
    if proc_ok:
        primary_ran = True
        holders.extend(proc_holders)
        holders.extend(_tmux_holders(target))

    lsof_ran, lsof_held = _lsof_held(target)
    if lsof_ran:
        primary_ran = True
        if lsof_held:
            holders.append("lsof reports open handles")

    if not primary_ran:
        fuser_ran, fuser_held = _fuser_held(target)
        if fuser_ran:
            primary_ran = True
            if fuser_held:
                holders.append("fuser reports active processes")

    if not primary_ran:
        return ProbeResult("unavailable", "no probe available")
    if holders:
        return ProbeResult("held", "; ".join(holders[:5]))
    return ProbeResult("clear", None)


# Tests substitute this. Production calls process_probe_real.
PROCESS_PROBE: Callable[[str], ProbeResult] = process_probe_real


# ---------------------------------------------------------------------------
# Dirty classification
# ---------------------------------------------------------------------------


@dataclass
class DirtyClassification:
    klass: str  # "A" | "B" | "C" | "D"
    tracked_paths: list[str] = field(default_factory=list)
    untracked_paths: list[str] = field(default_factory=list)
    evidence: str = ""

    def all_paths(self) -> list[str]:
        return [*self.tracked_paths, *self.untracked_paths]


def parse_porcelain_status(output: str) -> tuple[list[str], list[str], bool, bool]:
    """Return (tracked_modified_paths, untracked_paths, has_staged, has_conflict)."""
    tracked: list[str] = []
    untracked: list[str] = []
    staged = False
    conflict = False
    for raw in output.split("\n"):
        if not raw:
            continue
        if len(raw) < 3:
            continue
        x, y, _sp = raw[0], raw[1], raw[2]
        path = raw[3:]
        # Conflict states: any of D, A, U, T, etc. with both X and Y non-space and matching unmerged combos.
        unmerged_combos = {("D", "D"), ("A", "U"), ("U", "D"), ("U", "A"), ("D", "U"),
                           ("A", "A"), ("U", "U"), ("U", "T"), ("T", "U")}
        if (x, y) in unmerged_combos:
            conflict = True
            tracked.append(path)
            continue
        if x == "?" and y == "?":
            untracked.append(path)
            continue
        if x != " " and x != "?":
            staged = True
        if y != " " and y != "?":
            tracked.append(path)
        elif x != " " and x != "?":
            tracked.append(path)
    return tracked, untracked, staged, conflict


def get_dirty_status(repo_path: Path) -> tuple[DirtyClassification | None, dict[str, Any] | None]:
    """Return None if clean; else a DirtyClassification with paths populated.

    Class is initially set without merge/PR context; callers refine to A/B
    based on subsumption checks. D is final here.
    """
    result = run_git(["status", "--porcelain=v1", "--untracked-files=normal"], repo_path)
    if result.returncode != 0:
        return None, error_record("status_failed", result.command, result.stderr, str(repo_path))
    if not result.stdout.strip():
        return None, None
    tracked, untracked, staged, conflict = parse_porcelain_status(result.stdout)

    if staged:
        return DirtyClassification("D", tracked, untracked, "staged_changes"), None
    if conflict:
        return DirtyClassification("D", tracked, untracked, "merge_conflict"), None

    # Submodule status changes
    sub_result = run_git(["submodule", "status"], repo_path)
    if sub_result.returncode == 0 and sub_result.stdout:
        for line in sub_result.stdout.splitlines():
            if line[:1] in ("+", "-", "U"):
                return DirtyClassification("D", tracked, untracked, "submodule_change"), None

    # Large untracked files
    for u in untracked:
        full = repo_path / u
        try:
            if full.is_file() and full.stat().st_size > LARGE_FILE_THRESHOLD:
                return DirtyClassification("D", tracked, untracked, f"large_untracked:{u}"), None
        except OSError:
            continue

    # Default: not D yet. Caller refines to A/B/C.
    return DirtyClassification("C", tracked, untracked, ""), None


def matches_garbage_glob(path: str, globs: Iterable[str]) -> bool:
    for pat in globs:
        if fnmatch.fnmatchcase(path, pat):
            return True
        # Allow glob with "/**" suffix to match nested paths.
        if pat.endswith("/**"):
            prefix = pat[:-3]
            if fnmatch.fnmatchcase(path, prefix) or path.startswith(prefix + "/") or fnmatch.fnmatchcase(path, prefix + "/*"):
                return True
        # Allow basename match for simple "*.ext" patterns
        if "/" not in pat and "/" in path:
            if fnmatch.fnmatchcase(os.path.basename(path), pat):
                return True
    return False


def path_is_ignored(repo_path: Path, path: str) -> bool:
    result = run_git(["check-ignore", "-q", "--", path], repo_path)
    return result.returncode == 0


def all_paths_disposable(repo_path: Path, paths: Iterable[str], garbage_globs: list[str]) -> bool:
    for p in paths:
        if matches_garbage_glob(p, garbage_globs):
            continue
        if path_is_ignored(repo_path, p):
            continue
        return False
    return True


def tracked_diff_matches_base(repo_path: Path, base_commit: str, paths: list[str]) -> bool:
    """True when working-tree content for `paths` equals their content in base.

    Used by the Class B classifier: a dirty worktree on a PR-verified merged
    branch is subsumed when its uncommitted tracked edits already match the
    base tree.
    """
    if not paths:
        return True
    args = ["diff", "--quiet", base_commit, "--", *paths]
    result = run_git(args, repo_path)
    # `git diff --quiet` exits 0 on no diff, 1 on diff, >1 on error.
    return result.returncode == 0


def refine_classification(
    classification: DirtyClassification,
    repo_path: Path,
    branch_pr_merged_number: int | None,
    base_commit: str,
    garbage_globs: list[str],
) -> DirtyClassification:
    """Promote C to A or B if rules apply. D never demotes."""
    if classification.klass == "D":
        return classification

    untracked_disposable = all_paths_disposable(repo_path, classification.untracked_paths, garbage_globs)
    tracked_disposable = all_paths_disposable(repo_path, classification.tracked_paths, garbage_globs)

    # Class A: every dirty path is gitignore-or-glob disposable.
    if untracked_disposable and tracked_disposable:
        return DirtyClassification(
            "A", classification.tracked_paths, classification.untracked_paths,
            "all_paths_disposable",
        )

    # Class B: branch PR-verified merged AND tracked diff matches base AND untracked all disposable.
    if (
        branch_pr_merged_number is not None
        and untracked_disposable
        and tracked_diff_matches_base(repo_path, base_commit, classification.tracked_paths)
    ):
        return DirtyClassification(
            "B", classification.tracked_paths, classification.untracked_paths,
            f"subsumed_via_pr:#{branch_pr_merged_number}",
        )

    return classification  # remains C


# ---------------------------------------------------------------------------
# Per-repo planning
# ---------------------------------------------------------------------------


@dataclass
class RepoOutcome:
    path: str
    base: dict[str, Any]
    remote: str
    current_branch: str | None
    fetch: str = "skipped"
    base_update: str = "skipped"
    actions: list[dict[str, Any]] = field(default_factory=list)
    skipped: list[dict[str, Any]] = field(default_factory=list)
    dirty: list[dict[str, Any]] = field(default_factory=list)
    process_probes: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)


def run_fetch(repo: Path, remote: str, dry_run: bool) -> dict[str, Any] | None:
    args = ["fetch", "--prune", remote]
    if dry_run:
        args.insert(1, "--dry-run")
    result = run_git(args, repo)
    if result.returncode == 0:
        return None
    return error_record("fetch_failed", result.command, result.stderr or result.stdout, remote)


def fast_forward_base(
    repo: Path,
    base: str,
    base_commit: str,
    local_base_branch: str | None,
    initial_branch: str | None,
    worktrees: list[dict[str, Any]],
    dry_run: bool,
) -> tuple[str, dict[str, Any] | None]:
    """Return (status, error). status is one of: ff, skipped, already, unsafe, error."""
    if local_base_branch is None:
        return "skipped", None

    # Find local-tip OID and compare with base commit.
    tip = run_git(["rev-parse", "--verify", f"refs/heads/{local_base_branch}^{{commit}}"], repo)
    if tip.returncode != 0:
        return "error", error_record("base_resolve_failed", tip.command, tip.stderr, local_base_branch)
    if tip.stdout.strip() == base_commit:
        return "already", None

    # Is FF possible? local must be ancestor of base_commit.
    ancestor = run_git(["merge-base", "--is-ancestor", local_base_branch, base_commit], repo)
    if ancestor.returncode != 0:
        return "unsafe", None

    # Is the local base branch checked out anywhere?
    holding = [w for w in worktrees if w.get("branch") == local_base_branch]
    if not holding:
        if dry_run:
            return "ff", None
        result = run_git(["fetch", ".", f"{base}:{local_base_branch}"], repo)
        if result.returncode != 0:
            return "error", error_record("base_ff_failed", result.command, result.stderr, local_base_branch)
        return "ff", None

    # Checked out somewhere — safe only if the holding worktree is clean and
    # is the primary repo (so we can switch+merge in place).
    if len(holding) != 1 or holding[0]["path"] != str(repo):
        return "unsafe", None
    classification, status_err = get_dirty_status(repo)
    if status_err is not None:
        return "error", status_err
    if classification is not None:
        return "unsafe", None

    if dry_run:
        return "ff", None
    if initial_branch != local_base_branch:
        sw = run_git(["switch", local_base_branch], repo)
        if sw.returncode != 0:
            return "error", error_record("base_switch_failed", sw.command, sw.stderr, local_base_branch)
    merge = run_git(["merge", "--ff-only", base], repo)
    if merge.returncode != 0:
        return "error", error_record("base_ff_failed", merge.command, merge.stderr, local_base_branch)
    return "ff", None


def build_repo_plan(
    repo: Path,
    args: argparse.Namespace,
    base_commit: str,
    local_base_branch: str | None,
    initial_branch: str | None,
    branches: dict[str, dict[str, str]],
    worktrees: list[dict[str, Any]],
    remote: str,
    process_policy: str,
    garbage_globs: list[str],
    outcome: RepoOutcome,
) -> None:
    merged: dict[str, bool] = {}
    pr_merged_numbers: dict[str, int] = {}

    for branch, info in branches.items():
        branch_merged, error = is_merged(repo, info, base_commit)
        merged[branch] = branch_merged
        if error:
            outcome.errors.append(error)

    detect_pr = gh_available()
    gh_repo = discover_github_repo(repo, remote) if detect_pr else None
    if gh_repo is not None:
        gh_owner, gh_name = gh_repo
        pr_base = local_base_branch or base_branch_name(args.base)
        for branch, info in branches.items():
            if merged.get(branch, False):
                continue
            if protected_reason(branch, initial_branch, local_base_branch):
                continue
            number, pr_error = pr_merged_via_gh(
                repo, gh_owner, gh_name, branch, info["object"], pr_base, remote,
            )
            if pr_error:
                outcome.errors.append(pr_error)
                continue
            if number is not None:
                merged[branch] = True
                pr_merged_numbers[branch] = number

    primary_path = str(repo)
    linked_worktrees = [w for w in worktrees if w["path"] != primary_path]
    remove_worktree_branches: set[str] = set()

    for worktree in linked_worktrees:
        path = worktree["path"]
        branch = worktree.get("branch")
        exists = os.path.exists(path)

        if not exists:
            outcome.skipped.append(skip_record(
                "worktree", path, branch, "missing_path",
                "Run git worktree prune after confirming the path was not moved.",
            ))
            continue
        if worktree.get("locked"):
            outcome.skipped.append(skip_record(
                "worktree", path, branch, "locked", worktree.get("locked_reason"),
            ))
            continue
        if worktree.get("detached") or not branch:
            outcome.skipped.append(skip_record("worktree", path, branch, "detached"))
            continue
        protected = protected_reason(branch, initial_branch, local_base_branch)
        if protected:
            outcome.skipped.append(skip_record("worktree", path, branch, protected))
            continue
        if branch not in branches:
            outcome.skipped.append(skip_record("worktree", path, branch, "branch_missing"))
            continue
        is_branch_merged = merged.get(branch, False)
        if not is_branch_merged:
            outcome.skipped.append(skip_record("worktree", path, branch, "unmerged"))
            continue

        # Process probe
        probe = PROCESS_PROBE(path)
        outcome.process_probes.append({
            "worktree": path, "result": probe.state, "detail": probe.detail,
        })
        if probe.state == "held":
            if process_policy in ("skip", "ask"):
                # `ask` falls back to skip outside the consolidated confirmation
                # path. v1 does not surface held worktrees in the prompt.
                outcome.skipped.append(skip_record(
                    "worktree", path, branch, "process_held", probe.detail,
                ))
                continue
            # process_policy == "ignore": fall through.
        if probe.state == "unavailable" and process_policy in ("skip", "ask"):
            outcome.skipped.append(skip_record(
                "worktree", path, branch, "process_probe_unavailable", probe.detail,
            ))
            continue

        # Dirty classification
        classification, status_err = get_dirty_status(Path(path))
        if status_err:
            outcome.errors.append(status_err)
            outcome.skipped.append(skip_record("worktree", path, branch, "status_failed"))
            continue

        if classification is not None:
            classification = refine_classification(
                classification, Path(path), pr_merged_numbers.get(branch),
                base_commit, garbage_globs,
            )
            outcome.dirty.append({
                "worktree": path,
                "class": classification.klass,
                "tracked_paths": classification.tracked_paths,
                "untracked_paths": classification.untracked_paths,
                "evidence": classification.evidence,
            })
            if classification.klass == "D":
                outcome.skipped.append(skip_record(
                    "worktree", path, branch, "dirty_class_d", classification.evidence,
                ))
                continue
            if classification.klass == "C":
                outcome.skipped.append(skip_record(
                    "worktree", path, branch, "dirty_class_c", "potentially_unique_work",
                ))
                continue
            # Class A or B: emit clean_dirty action(s) before remove_worktree
            outcome.actions.append(_clean_dirty_action(path, branch, classification))

        if branch in pr_merged_numbers:
            wt_reason = "merged_clean_worktree_via_pr"
            wt_detail = f"merged via PR #{pr_merged_numbers[branch]}"
        else:
            wt_reason = "merged_clean_worktree"
            wt_detail = None
        klass = classification.klass if classification else None
        outcome.actions.append(action_record(
            "remove_worktree", path, branch,
            [["git", "worktree", "remove", path]],
            wt_reason, wt_detail, klass=klass,
        ))
        remove_worktree_branches.add(branch)

    checked_after_removal = checked_out_branches(worktrees, remove_worktree_branches)

    for branch, info in branches.items():
        protected = protected_reason(branch, initial_branch, local_base_branch)
        if protected:
            outcome.skipped.append(skip_record("branch", branch, branch, protected))
            continue
        if not merged.get(branch, False):
            outcome.skipped.append(skip_record("branch", branch, branch, "unmerged"))
            continue

        checked_paths = checked_after_removal.get(branch, [])
        if checked_paths:
            if checked_paths == [primary_path]:
                outcome.skipped.append(skip_record("branch", branch, branch, "current_branch"))
            else:
                outcome.skipped.append(skip_record(
                    "branch", branch, branch, "checked_out_elsewhere",
                    ", ".join(checked_paths),
                ))
            continue

        if branch in pr_merged_numbers:
            delete_command = ["git", "branch", "-D", branch]
            delete_reason = "merged_branch_via_pr"
            delete_detail = f"merged via PR #{pr_merged_numbers[branch]}"
        else:
            delete_command = ["git", "branch", "-d", branch]
            delete_reason = "merged_branch"
            delete_detail = None
        outcome.actions.append(action_record(
            "delete_branch", branch, branch, [delete_command], delete_reason, delete_detail,
        ))

    # Prune metadata
    prune_action, prune_error = prune_metadata_plan(repo, execute=False)
    if prune_error:
        outcome.errors.append(prune_error)
    if prune_action:
        outcome.actions.append(prune_action)


def _clean_dirty_action(
    worktree_path: str,
    branch: str | None,
    classification: DirtyClassification,
) -> dict[str, Any]:
    commands: list[list[str]] = []
    if classification.tracked_paths:
        commands.append(["git", "checkout", "--", *classification.tracked_paths])
    if classification.untracked_paths:
        commands.append(["git", "clean", "-fd", "--", *classification.untracked_paths])
    return action_record(
        "clean_dirty", worktree_path, branch, commands or [["true"]],
        f"dirty_class_{classification.klass.lower()}",
        classification.evidence or None,
        klass=classification.klass,
    )


def prune_metadata_plan(repo: Path, execute: bool) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    command = ["worktree", "prune", "--verbose"] if execute else ["worktree", "prune", "--dry-run", "--verbose"]
    result = run_git(command, repo)
    if result.returncode != 0:
        return None, error_record("worktree_prune_failed", result.command, result.stderr)
    detail = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
    if not detail:
        return None, None
    return action_record(
        "prune_metadata", str(repo), None,
        [result.command], "stale_metadata", detail,
    ), None


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------


def execute_plan(
    repo: Path,
    actions: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    *,
    allow_class_b: bool,
    process_policy: str = "skip",
) -> bool:
    ok = True

    # Phase 1: clean_dirty for Class A always; Class B only if allowed.
    for action in actions:
        if action["kind"] != "clean_dirty" or action["status"] != "planned":
            continue
        klass = action.get("class")
        if klass == "B" and not allow_class_b:
            action["status"] = "skipped"
            skipped.append(skip_record(
                "worktree", action["target"], action["branch"],
                "class_b_skipped", "use --yes or --interactive to clean",
            ))
            continue
        if klass not in ("A", "B"):
            action["status"] = "skipped"
            continue
        # Run inside the worktree path, not the repo root.
        cwd = action["target"]
        for command in action["commands"]:
            if command == ["true"]:
                continue
            result = run_git(git_args(command), cwd)
            if result.returncode != 0:
                action["status"] = "failed"
                errors.append(error_record(
                    "clean_dirty_failed", result.command, result.stderr, action["target"],
                ))
                ok = False
                break
        else:
            action["status"] = "done"

    # Phase 2: remove_worktree (skip if its companion clean_dirty was skipped)
    skipped_targets = {a["target"] for a in actions if a["kind"] == "clean_dirty" and a["status"] in ("skipped", "failed")}
    for action in actions:
        if action["kind"] != "remove_worktree" or action["status"] != "planned":
            continue
        if action["target"] in skipped_targets:
            action["status"] = "skipped"
            continue
        # Re-probe just before destructive removal: in --interactive an
        # arbitrary delay can pass between planning and execution, and a new
        # shell or editor may have attached to the worktree in the meantime.
        # `--process-policy=ignore` skips the re-probe.
        if process_policy != "ignore":
            recheck = PROCESS_PROBE(action["target"])
            if recheck.state == "held":
                action["status"] = "skipped"
                skipped.append(skip_record(
                    "worktree", action["target"], action["branch"],
                    "process_held_at_execute", recheck.detail,
                ))
                continue
        result = run_git(git_args(action["commands"][0]), repo)
        if result.returncode != 0:
            action["status"] = "failed"
            errors.append(error_record(
                "worktree_remove_failed", result.command, result.stderr, action["target"],
            ))
            ok = False
            continue
        action["status"] = "done"

    # Phase 3: delete_branch
    for action in actions:
        if action["kind"] != "delete_branch" or action["status"] != "planned":
            continue
        result = run_git(git_args(action["commands"][0]), repo)
        if result.returncode != 0:
            action["status"] = "skipped"
            skipped.append(skip_record(
                "branch", action["target"], action["branch"], "delete_refused",
                result.stderr or result.stdout,
            ))
            continue
        action["status"] = "done"

    # Phase 4: prune_metadata
    for action in actions:
        if action["kind"] != "prune_metadata" or action["status"] != "planned":
            continue
        # Replace dry-run command with executing command.
        cmd = ["git", "worktree", "prune", "--verbose"]
        result = run_git(git_args(cmd), repo)
        if result.returncode != 0:
            errors.append(error_record(
                "worktree_prune_failed", result.command, result.stderr,
            ))
            ok = False
            continue
        action["commands"] = [cmd]
        action["command"] = cmd
        action["status"] = "done"

    return ok


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def outcome_to_dict(outcome: RepoOutcome) -> dict[str, Any]:
    return {
        "path": outcome.path,
        "base": outcome.base,
        "remote": outcome.remote,
        "current_branch": outcome.current_branch,
        "fetch": outcome.fetch,
        "base_update": outcome.base_update,
        "actions": outcome.actions,
        "skipped": outcome.skipped,
        "dirty": outcome.dirty,
        "process_probes": outcome.process_probes,
        "errors": outcome.errors,
    }


def summarize(outcomes: list[RepoOutcome]) -> dict[str, int]:
    safe = 0
    class_b = 0
    skipped = 0
    errors = 0
    for o in outcomes:
        for a in o.actions:
            if a["status"] != "done" and a["status"] != "planned":
                continue
            if a.get("class") == "B":
                class_b += 1
            else:
                safe += 1
        skipped += len(o.skipped)
        errors += len(o.errors)
    return {"safe_actions": safe, "class_b_actions": class_b, "skipped": skipped, "errors": errors}


def emit_text(
    mode: str,
    root: str,
    outcomes: list[RepoOutcome],
    discovery_errors: list[dict[str, Any]],
) -> None:
    print(f"Mode: {mode}")
    print(f"Root: {root}")
    if discovery_errors:
        print(f"\nDiscovery errors: {len(discovery_errors)}")
        for e in discovery_errors:
            target = f" {e['target']}" if e.get("target") else ""
            detail = f": {e['detail']}" if e.get("detail") else ""
            print(f"  {e['reason']}{target}{detail}")
    for outcome in outcomes:
        print(f"\n[{outcome.path}]")
        if outcome.fetch != "skipped":
            print(f"  fetch: {outcome.fetch}")
        if outcome.base_update != "skipped":
            print(f"  base_update: {outcome.base_update}")
        safe_actions = [a for a in outcome.actions if a.get("class") != "B"]
        b_actions = [a for a in outcome.actions if a.get("class") == "B"]
        if safe_actions:
            print(f"  actions: {len(safe_actions)}")
            for a in safe_actions:
                detail = f" — {a['detail']}" if a.get("detail") else ""
                print(f"    {a['kind']} {a['target']} ({a['reason']}){detail} [{a['status']}]")
        if b_actions:
            print(f"  class_b_actions: {len(b_actions)}")
            for a in b_actions:
                detail = f" — {a['detail']}" if a.get("detail") else ""
                print(f"    {a['kind']} {a['target']} ({a['reason']}){detail} [{a['status']}]")
        if outcome.skipped:
            print(f"  skipped: {len(outcome.skipped)}")
            for s in outcome.skipped:
                detail = f" — {s['detail']}" if s.get("detail") else ""
                print(f"    {s['type']} {s['target']} ({s['reason']}){detail}")
        if outcome.errors:
            print(f"  errors: {len(outcome.errors)}")
            for e in outcome.errors:
                target = f" {e['target']}" if e.get("target") else ""
                detail = f": {e['detail']}" if e.get("detail") else ""
                print(f"    {e['reason']}{target}{detail}")
    summary = summarize(outcomes)
    print(
        f"\nSummary: safe={summary['safe_actions']} "
        f"class_b={summary['class_b_actions']} "
        f"skipped={summary['skipped']} errors={summary['errors']}"
    )


def emit_json(
    mode: str,
    root: str,
    outcomes: list[RepoOutcome],
    discovery_errors: list[dict[str, Any]],
) -> None:
    data = {
        "mode": mode,
        "root": root,
        "errors": discovery_errors,
        "repos": [outcome_to_dict(o) for o in outcomes],
        "summary": summarize(outcomes),
    }
    print(json.dumps(data, indent=2, sort_keys=True))


def consolidated_prompt(outcomes: list[RepoOutcome]) -> bool:
    """Show one y/N prompt for Class B actions across all repos.

    Returns True if user answered yes.
    """
    b_actions: list[tuple[str, dict[str, Any]]] = []
    for o in outcomes:
        for a in o.actions:
            if a.get("class") == "B":
                b_actions.append((o.path, a))
    if not b_actions:
        return False
    print("\nClass B (subsumed by merged work) — proposed cleanup:", file=sys.stderr)
    for repo_path, a in b_actions:
        rel = a["target"]
        detail = f" — {a['detail']}" if a.get("detail") else ""
        print(f"  - [{repo_path}] {a['kind']} {rel}{detail}", file=sys.stderr)
    print("Proceed? [y/N] ", end="", file=sys.stderr, flush=True)
    try:
        answer = sys.stdin.readline().strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    return answer in {"y", "yes"}


# ---------------------------------------------------------------------------
# Top-level orchestration
# ---------------------------------------------------------------------------


def resolve_target_repos(args: argparse.Namespace, root: Path) -> tuple[list[Path], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    if args.repo:
        repos: list[Path] = []
        for r in args.repo:
            p = Path(r).resolve()
            if not is_repo_root(p):
                errors.append(error_record("not_a_git_repo", target=str(p)))
                continue
            repos.append(p)
        return repos, errors
    return discover_repositories(root, args.max_depth), errors


def process_repo(
    repo: Path,
    args: argparse.Namespace,
    mode: str,
    garbage_globs: list[str],
) -> RepoOutcome:
    initial_branch = current_branch(repo)
    remote = select_remote(args.base, args.remote, repo)
    outcome = RepoOutcome(
        path=str(repo),
        base={"ref": args.base, "commit": None, "local_branch": None},
        remote=remote,
        current_branch=initial_branch,
    )

    dry_run = mode == "dry-run"

    if not args.no_fetch:
        fetch_error = run_fetch(repo, remote, dry_run=dry_run)
        if fetch_error is None:
            outcome.fetch = "ok"
        else:
            outcome.fetch = "error"
            outcome.errors.append(fetch_error)
            if mode == "yes" or mode == "interactive" or mode == "default":
                # In execution modes, fetch failure aborts further work for this repo.
                return outcome

    base_commit, base_error = resolve_base_commit(repo, args.base)
    local_base_branch = resolve_local_base_branch(repo, args.base)
    outcome.base["local_branch"] = local_base_branch
    if base_error:
        outcome.errors.append(base_error)
        return outcome
    assert base_commit is not None
    outcome.base["commit"] = base_commit

    worktrees, worktree_error = list_worktrees(repo)
    branches, branch_error = list_branches(repo)
    if worktree_error:
        outcome.errors.append(worktree_error)
    if branch_error:
        outcome.errors.append(branch_error)
    if worktree_error or branch_error:
        return outcome

    # Base FF
    if not args.no_update_base:
        ff_status, ff_error = fast_forward_base(
            repo, args.base, base_commit, local_base_branch,
            initial_branch, worktrees, dry_run,
        )
        outcome.base_update = ff_status
        if ff_error:
            outcome.errors.append(ff_error)
        # If FF happened, refresh base_commit since local moved; reachability uses origin/<base>.
        if ff_status == "ff" and not dry_run:
            new_commit, _err = resolve_base_commit(repo, args.base)
            if new_commit is not None:
                outcome.base["commit"] = new_commit
                base_commit = new_commit
            # Reload branches in case anything changed.
            branches, _err = list_branches(repo)
    else:
        outcome.base_update = "skipped"

    build_repo_plan(
        repo, args, base_commit, local_base_branch, initial_branch,
        branches, worktrees, remote, args.process_policy, garbage_globs, outcome,
    )

    return outcome


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    mode = resolve_mode(args)
    root = Path(args.root).resolve() if args.root else Path.cwd()
    garbage_globs = [*DEFAULT_GARBAGE_GLOBS, *args.garbage_glob]

    repos, discovery_errors = resolve_target_repos(args, root)

    outcomes: list[RepoOutcome] = []
    for repo in repos:
        outcome = process_repo(repo, args, mode, garbage_globs)
        outcomes.append(outcome)

    # Mode-specific execution
    overall_ok = True
    if mode in ("yes", "default", "interactive"):
        allow_class_b_modes = {"yes": True, "default": False, "interactive": False}
        allow_class_b = allow_class_b_modes[mode]

        if mode == "interactive":
            if any(a.get("class") == "B" for o in outcomes for a in o.actions):
                allow_class_b = consolidated_prompt(outcomes)

        for outcome in outcomes:
            ok = execute_plan(
                Path(outcome.path), outcome.actions, outcome.skipped, outcome.errors,
                allow_class_b=allow_class_b, process_policy=args.process_policy,
            )
            if not ok:
                overall_ok = False
            outcome.current_branch = current_branch(Path(outcome.path)) or outcome.current_branch

    if args.json:
        emit_json(mode, str(root), outcomes, discovery_errors)
    else:
        emit_text(mode, str(root), outcomes, discovery_errors)

    # Exit-code semantics:
    # - 2: configuration / discovery / planning failure (caller should fix the
    #      invocation: bad --repo, missing base, broken worktree list, etc.)
    # - 1: execution failure or fetch failure during a non-dry-run mode
    # - 0: success, or only non-fatal errors such as pr_check_failed
    DISCOVERY_REASONS = {
        "not_a_git_repo", "base_missing", "worktree_list_failed",
        "branch_list_failed", "base_resolve_failed",
    }
    if discovery_errors:
        return 2
    if any(
        e["reason"] in DISCOVERY_REASONS
        for o in outcomes for e in o.errors
    ):
        return 2

    returncode = 0
    if not overall_ok:
        returncode = 1
    if mode != "dry-run":
        for outcome in outcomes:
            if outcome.fetch == "error":
                returncode = 1
                break
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
