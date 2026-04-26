#!/usr/bin/env python3
"""Smoke tests for git_prune_worktrees.py using temporary repositories."""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("git_prune_worktrees.py")


def install_fake_gh(
    root: Path,
    responses: dict[tuple[str, str], list[dict[str, object]]] | None = None,
    *,
    fail: bool = False,
) -> Path:
    """Create a fake `gh` executable in a fresh dir and return that dir.

    `responses` maps (head-branch, base-branch) to the JSON array
    `gh pr list ... --json number,headRefOid` should return.
    `fail=True` makes every non-version invocation exit nonzero (simulates auth failure).
    """
    bin_dir = root / "fake-bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    data_dir = root / "fake-gh-data"
    data_dir.mkdir(parents=True, exist_ok=True)
    index: dict[str, str] = {}
    if responses is not None:
        for i, ((head, base), payload) in enumerate(responses.items()):
            data_path = data_dir / f"resp-{i}.json"
            data_path.write_text(json.dumps(payload), encoding="utf-8")
            index[f"{head}\0{base}"] = str(data_path)
    index_path = data_dir / "index.json"
    index_path.write_text(json.dumps(index), encoding="utf-8")
    script = bin_dir / "gh"
    script.write_text(
        f"""#!/usr/bin/env python3
import json, os, sys
args = sys.argv[1:]
if args[:1] == ["--version"]:
    print("gh fake 0.0.0")
    sys.exit(0)
if {fail!r}:
    sys.stderr.write("fake gh: simulated failure\\n")
    sys.exit(1)
head = base = ""
i = 0
while i < len(args):
    if args[i] == "--head" and i + 1 < len(args):
        head = args[i + 1]
    elif args[i] == "--base" and i + 1 < len(args):
        base = args[i + 1]
    i += 1
with open({str(index_path)!r}) as fh:
    index = json.load(fh)
key = head + "\\x00" + base
path = index.get(key)
if path and os.path.exists(path):
    with open(path) as fh:
        sys.stdout.write(fh.read())
else:
    sys.stdout.write("[]")
sys.exit(0)
""",
        encoding="utf-8",
    )
    script.chmod(script.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return bin_dir


def branch_oid(repo: Path, branch: str) -> str:
    return git(repo, "rev-parse", branch).stdout.strip()


def env_without_real_gh(extra_bin: Path | None = None) -> dict[str, str]:
    """Return env with real `gh` removed from PATH; optionally prepend a fake-gh dir."""
    env = os.environ.copy()
    parts = env.get("PATH", "").split(os.pathsep)
    filtered = [p for p in parts if p and not (Path(p) / "gh").exists()]
    if extra_bin is not None:
        filtered.insert(0, str(extra_bin))
    env["PATH"] = os.pathsep.join(filtered)
    return env


def run(
    command: list[str],
    cwd: Path | None = None,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        check=False,
        env=env,
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


def make_squash_merged_branch(repo: Path, branch: str) -> None:
    """Simulate a squash-merge: branch tip is not reachable from main, but its
    content has been applied to main as a separate commit.
    """
    git(repo, "switch", "-c", branch, "main")
    make_commit(repo, branch)
    git(repo, "switch", "main")
    # Apply the same content as a fresh commit on main (as squash merge would).
    write(repo / f"{branch}.txt", branch)
    git(repo, "add", f"{branch}.txt")
    git(repo, "commit", "-m", f"squash {branch}")


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
    def run_script(
        self,
        repo: Path,
        *args: str,
        check: bool = True,
        env: dict[str, str] | None = None,
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        result = run([sys.executable, str(SCRIPT), "--json", *args], cwd=repo, check=check, env=env)
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

    def _setup_squash_fixture(self, root: Path, branch: str = "issue-99-foo") -> tuple[RepoFixture, str]:
        fixture = RepoFixture.create(root)
        make_squash_merged_branch(fixture.repo, branch)
        oid = branch_oid(fixture.repo, branch)
        # Point origin at a GitHub-style URL so PR detection activates.
        # Fetch is unreachable, so tests must pass --no-fetch.
        git(fixture.repo, "remote", "set-url", "origin", "git@github.com:fake/repo.git")
        return fixture, oid

    def test_pr_merged_branch_force_deleted_with_pr_detail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture, oid = self._setup_squash_fixture(root)
            bin_dir = install_fake_gh(
                root, {("issue-99-foo", "main"): [{"number": 99, "headRefOid": oid}]},
            )
            env = env_without_real_gh(bin_dir)

            result, data = self.run_script(
                fixture.repo, "--base", "main", "--no-fetch", "--yes", env=env,
            )

            self.assertEqual(result.returncode, 0)
            self.assertFalse(branch_exists(fixture.repo, "issue-99-foo"))
            done = [a for a in data["actions"] if a["status"] == "done" and a["type"] == "delete_branch"]  # type: ignore[index]
            self.assertEqual(len(done), 1)
            self.assertEqual(done[0]["reason"], "merged_branch_via_pr")
            self.assertIn("PR #99", done[0]["detail"])
            self.assertEqual(done[0]["command"], ["git", "branch", "-D", "issue-99-foo"])

    def test_no_detect_pr_merged_disables_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture, oid = self._setup_squash_fixture(root)
            bin_dir = install_fake_gh(
                root, {("issue-99-foo", "main"): [{"number": 99, "headRefOid": oid}]},
            )
            env = env_without_real_gh(bin_dir)

            result, data = self.run_script(
                fixture.repo, "--base", "main", "--no-fetch", "--no-detect-pr-merged", env=env,
            )

            self.assertEqual(result.returncode, 0)
            reasons = {item["reason"] for item in data["skipped"] if item["branch"] == "issue-99-foo"}  # type: ignore[index]
            self.assertEqual(reasons, {"unmerged"})
            self.assertTrue(branch_exists(fixture.repo, "issue-99-foo"))

    def test_gh_missing_silently_falls_back(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture, _oid = self._setup_squash_fixture(root)
            env = env_without_real_gh(None)

            result, data = self.run_script(
                fixture.repo, "--base", "main", "--no-fetch", env=env,
            )

            self.assertEqual(result.returncode, 0)
            self.assertEqual(data["errors"], [])
            reasons = {item["reason"] for item in data["skipped"] if item["branch"] == "issue-99-foo"}  # type: ignore[index]
            self.assertEqual(reasons, {"unmerged"})

    def test_non_github_remote_skips_detection_silently(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = RepoFixture.create(root)
            make_squash_merged_branch(fixture.repo, "issue-99-foo")
            oid = branch_oid(fixture.repo, "issue-99-foo")
            # Origin already points at the local bare repo (not github.com).
            bin_dir = install_fake_gh(
                root, {("issue-99-foo", "main"): [{"number": 99, "headRefOid": oid}]},
            )
            env = env_without_real_gh(bin_dir)

            result, data = self.run_script(
                fixture.repo, "--base", "main", "--no-fetch", env=env,
            )

            self.assertEqual(result.returncode, 0)
            self.assertEqual(data["errors"], [])
            reasons = {item["reason"] for item in data["skipped"] if item["branch"] == "issue-99-foo"}  # type: ignore[index]
            self.assertEqual(reasons, {"unmerged"})

    def test_gh_failure_recorded_but_does_not_abort(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture, _oid = self._setup_squash_fixture(root)
            # Also create a normally-merged branch that should still be deleted.
            make_merged_branch(fixture.repo, "merged-delete")
            bin_dir = install_fake_gh(root, fail=True)
            env = env_without_real_gh(bin_dir)

            result, data = self.run_script(
                fixture.repo, "--base", "main", "--no-fetch", "--yes", env=env,
            )

            self.assertEqual(result.returncode, 0)
            error_reasons = {e["reason"] for e in data["errors"]}  # type: ignore[index]
            self.assertIn("pr_check_failed", error_reasons)
            self.assertFalse(branch_exists(fixture.repo, "merged-delete"))
            self.assertTrue(branch_exists(fixture.repo, "issue-99-foo"))

    def test_reachability_merged_still_uses_safe_delete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = RepoFixture.create(root)
            make_merged_branch(fixture.repo, "true-merged")
            git(fixture.repo, "remote", "set-url", "origin", "git@github.com:fake/repo.git")
            bin_dir = install_fake_gh(root, {})  # No PR data; gh would return [] for any branch.
            env = env_without_real_gh(bin_dir)

            result, data = self.run_script(
                fixture.repo, "--base", "main", "--no-fetch", env=env,
            )

            self.assertEqual(result.returncode, 0)
            planned = [a for a in data["actions"] if a["type"] == "delete_branch" and a["branch"] == "true-merged"]  # type: ignore[index]
            self.assertEqual(len(planned), 1)
            self.assertEqual(planned[0]["reason"], "merged_branch")
            self.assertEqual(planned[0]["command"], ["git", "branch", "-d", "true-merged"])
            self.assertNotIn("detail", planned[0])

    def test_pr_head_oid_mismatch_blocks_force_delete(self) -> None:
        """A merged PR for the same branch name must not authorize deleting a
        branch whose tip has diverged (e.g. branch reused after the original PR
        merged). Without this guard, `git branch -D` would destroy unmerged work.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture, old_oid = self._setup_squash_fixture(root)
            # Add a new commit to the branch so its tip diverges from the merged PR's headRefOid.
            git(fixture.repo, "switch", "issue-99-foo")
            make_commit(fixture.repo, "extra")
            git(fixture.repo, "switch", "main")
            new_oid = branch_oid(fixture.repo, "issue-99-foo")
            self.assertNotEqual(old_oid, new_oid)

            bin_dir = install_fake_gh(
                root, {("issue-99-foo", "main"): [{"number": 99, "headRefOid": old_oid}]},
            )
            env = env_without_real_gh(bin_dir)

            result, data = self.run_script(
                fixture.repo, "--base", "main", "--no-fetch", "--yes", env=env,
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue(branch_exists(fixture.repo, "issue-99-foo"))
            reasons = {item["reason"] for item in data["skipped"] if item["branch"] == "issue-99-foo"}  # type: ignore[index]
            self.assertEqual(reasons, {"unmerged"})

    def test_local_slash_base_branch_preserved_in_pr_query(self) -> None:
        """When --base is a local branch like `release/foo`, the PR query must
        use the full name; otherwise PRs get filtered against the wrong base
        and a force-delete based on a same-name PR could destroy work.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = RepoFixture.create(root)
            git(fixture.repo, "branch", "release/foo", "main")
            # Create a squash-merged branch off `release/foo`.
            git(fixture.repo, "switch", "-c", "issue-50-bar", "release/foo")
            make_commit(fixture.repo, "issue-50-bar")
            git(fixture.repo, "switch", "release/foo")
            write(fixture.repo / "issue-50-bar.txt", "issue-50-bar")
            git(fixture.repo, "add", "issue-50-bar.txt")
            git(fixture.repo, "commit", "-m", "squash issue-50-bar")
            git(fixture.repo, "switch", "main")
            oid = branch_oid(fixture.repo, "issue-50-bar")
            git(fixture.repo, "remote", "set-url", "origin", "git@github.com:fake/repo.git")
            # Fake gh only returns the PR when queried with base=release/foo (full name).
            # If the script truncated the base to `foo`, the lookup misses → branch left alone.
            bin_dir = install_fake_gh(
                root, {("issue-50-bar", "release/foo"): [{"number": 50, "headRefOid": oid}]},
            )
            env = env_without_real_gh(bin_dir)

            result, data = self.run_script(
                fixture.repo, "--base", "release/foo", "--no-fetch", "--yes", env=env,
            )

            self.assertEqual(result.returncode, 0)
            self.assertFalse(branch_exists(fixture.repo, "issue-50-bar"))
            done = [
                a for a in data["actions"]  # type: ignore[index]
                if a["status"] == "done" and a["branch"] == "issue-50-bar"
            ]
            self.assertEqual(len(done), 1)
            self.assertEqual(done[0]["reason"], "merged_branch_via_pr")
            self.assertIn("PR #50", done[0]["detail"])


if __name__ == "__main__":
    unittest.main()
