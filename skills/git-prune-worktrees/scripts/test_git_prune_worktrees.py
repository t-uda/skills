#!/usr/bin/env python3
"""Smoke tests for git_prune_worktrees.py using temporary repositories."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("git_prune_worktrees.py")


def run(command: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"command failed: {' '.join(command)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(["git", *args], cwd=cwd, check=check)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def branch_exists(repo: Path, branch: str) -> bool:
    return git(repo, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}", check=False).returncode == 0


def make_commit(repo: Path, name: str) -> None:
    write(repo / f"{name}.txt", name)
    git(repo, "add", f"{name}.txt")
    git(repo, "commit", "-m", name)


def make_merged_branch(repo: Path, branch: str) -> None:
    git(repo, "switch", "-c", branch, "main")
    make_commit(repo, branch)
    git(repo, "switch", "main")
    git(repo, "merge", "--no-ff", branch, "-m", f"merge {branch}")


def make_unmerged_branch(repo: Path, branch: str) -> None:
    git(repo, "switch", "-c", branch, "main")
    make_commit(repo, branch)
    git(repo, "switch", "main")


class RepoFixture:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.origin = root / "origin.git"
        self.repo = root / "repo"
        self.paths: dict[str, Path] = {}

    @classmethod
    def create(cls, root: Path) -> "RepoFixture":
        fixture = cls(root)
        git(root, "init", "--bare", str(fixture.origin))
        git(root, "clone", str(fixture.origin), str(fixture.repo))
        git(fixture.repo, "config", "user.email", "agent@example.com")
        git(fixture.repo, "config", "user.name", "Agent")
        write(fixture.repo / "README.md", "fixture\n")
        git(fixture.repo, "add", "README.md")
        git(fixture.repo, "commit", "-m", "initial")
        git(fixture.repo, "branch", "-M", "main")
        git(fixture.repo, "push", "-u", "origin", "main")
        return fixture

    def add_standard_cases(self) -> None:
        for branch in ("merged-delete", "wt-clean", "wt-dirty", "wt-locked", "wt-missing"):
            make_merged_branch(self.repo, branch)
        make_unmerged_branch(self.repo, "unmerged")

        for branch in ("wt-clean", "wt-dirty", "wt-locked", "wt-missing"):
            path = self.root / branch
            git(self.repo, "worktree", "add", str(path), branch)
            self.paths[branch] = path

        write(self.paths["wt-dirty"] / "dirty.txt", "dirty\n")
        git(self.repo, "worktree", "lock", "--reason", "keep", str(self.paths["wt-locked"]))
        shutil.rmtree(self.paths["wt-missing"])

        detached = self.root / "wt-detached"
        git(self.repo, "worktree", "add", "--detach", str(detached), "main")
        self.paths["wt-detached"] = detached
        git(self.repo, "switch", "main")


class GitPruneWorktreesTests(unittest.TestCase):
    def run_script(self, repo: Path, *args: str, check: bool = True) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        result = run([sys.executable, str(SCRIPT), "--json", *args], cwd=repo, check=check)
        data = json.loads(result.stdout)
        return result, data

    def test_dry_run_makes_no_cleanup_changes_and_reports_stable_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = RepoFixture.create(Path(tmp))
            fixture.add_standard_cases()

            result, data = self.run_script(fixture.repo, "--base", "main", "--no-fetch")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(
                set(data),
                {"actions", "base", "current_branch", "errors", "final_branch", "mode", "remote", "repo", "skipped"},
            )
            self.assertTrue(fixture.paths["wt-clean"].exists())
            self.assertTrue(branch_exists(fixture.repo, "merged-delete"))
            action_types = {action["type"] for action in data["actions"]}  # type: ignore[index]
            self.assertIn("remove_worktree", action_types)
            self.assertIn("delete_branch", action_types)
            skip_reasons = {item["reason"] for item in data["skipped"]}  # type: ignore[index]
            self.assertTrue(
                {"dirty", "locked", "detached", "missing_path", "unmerged"}.issubset(skip_reasons),
                skip_reasons,
            )

    def test_yes_removes_only_clean_merged_worktrees_and_branches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = RepoFixture.create(Path(tmp))
            fixture.add_standard_cases()

            result, data = self.run_script(fixture.repo, "--base", "main", "--no-fetch", "--yes")

            self.assertEqual(result.returncode, 0)
            self.assertFalse(fixture.paths["wt-clean"].exists())
            self.assertFalse(branch_exists(fixture.repo, "wt-clean"))
            self.assertFalse(branch_exists(fixture.repo, "merged-delete"))
            self.assertTrue(fixture.paths["wt-dirty"].exists())
            self.assertTrue(branch_exists(fixture.repo, "wt-dirty"))
            self.assertTrue(fixture.paths["wt-locked"].exists())
            self.assertTrue(branch_exists(fixture.repo, "wt-locked"))
            self.assertTrue(branch_exists(fixture.repo, "unmerged"))
            done_types = {action["type"] for action in data["actions"] if action["status"] == "done"}  # type: ignore[index]
            self.assertIn("remove_worktree", done_types)
            self.assertIn("delete_branch", done_types)

    def test_current_branch_requires_switch_base_or_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = RepoFixture.create(Path(tmp))
            make_merged_branch(fixture.repo, "current-merged")
            git(fixture.repo, "switch", "current-merged")

            result, data = self.run_script(fixture.repo, "--base", "main", "--no-fetch")

            self.assertEqual(result.returncode, 0)
            reasons = {item["reason"] for item in data["skipped"]}  # type: ignore[index]
            self.assertIn("current_branch", reasons)
            self.assertTrue(branch_exists(fixture.repo, "current-merged"))

            result, data = self.run_script(fixture.repo, "--base", "main", "--no-fetch", "--yes", "--switch-base")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(data["final_branch"], "main")
            self.assertFalse(branch_exists(fixture.repo, "current-merged"))

    def test_fetch_failure_with_yes_stops_before_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = RepoFixture.create(Path(tmp))
            make_merged_branch(fixture.repo, "merged-delete")
            git(fixture.repo, "remote", "set-url", "origin", str(Path(tmp) / "missing.git"))

            result, data = self.run_script(fixture.repo, "--base", "main", "--yes", check=False)

            self.assertNotEqual(result.returncode, 0)
            reasons = {item["reason"] for item in data["errors"]}  # type: ignore[index]
            self.assertIn("fetch_failed", reasons)
            self.assertTrue(branch_exists(fixture.repo, "merged-delete"))

    def test_local_slash_base_branch_is_not_treated_as_remote(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = RepoFixture.create(Path(tmp))
            git(fixture.repo, "branch", "release/foo", "main")

            result, data = self.run_script(fixture.repo, "--base", "release/foo", "--yes")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(data["remote"], "origin")
            self.assertEqual(data["base"]["local_branch"], "release/foo")  # type: ignore[index]


if __name__ == "__main__":
    unittest.main()
