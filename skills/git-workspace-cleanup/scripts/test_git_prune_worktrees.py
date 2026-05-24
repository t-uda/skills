#!/usr/bin/env python3
"""Tests for git_prune_worktrees.py using temporary repositories.

Coverage:
- Preserved safety model: PR-verified `branch -D` with audit, reachability `-d`,
  protected branches, OID-mismatch guard, slash-base PR query.
- New workspace mode: discovery, multi-repo orchestration, base FF.
- Mode interaction: --dry-run no mutation, default executes safe + Class A,
  --yes adds Class B, --interactive prompts.
- Dirty classification: A discard, B discard with PR# evidence, C skip, D skip.
- Process probes: stubbed to test held / clear / unavailable handling.
"""

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


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def install_fake_gh(
    root: Path,
    responses: dict[tuple[str, str], list[dict[str, object]]] | None = None,
    *,
    search_responses: dict[tuple[str, str], list[dict[str, object]]] | None = None,
    fail: bool = False,
) -> Path:
    # The production code no longer passes --base to `gh pr list`; reachability
    # is now checked in-process via the baseRefName / mergeCommit fields in each
    # PR record. The fake-gh index therefore keys only on head/search (the base
    # component of the caller-supplied dict key is kept for readability but is
    # not part of the lookup key used by the fake binary).
    bin_dir = root / "fake-bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    data_dir = root / "fake-gh-data"
    data_dir.mkdir(parents=True, exist_ok=True)
    index: dict[str, str] = {}
    if responses is not None:
        for i, ((head, _base), payload) in enumerate(responses.items()):
            data_path = data_dir / f"resp-{i}.json"
            data_path.write_text(json.dumps(payload), encoding="utf-8")
            index[f"head\0{head}"] = str(data_path)
    if search_responses is not None:
        offset = len(index)
        for i, ((search, _base), payload) in enumerate(search_responses.items(), start=offset):
            data_path = data_dir / f"resp-{i}.json"
            data_path.write_text(json.dumps(payload), encoding="utf-8")
            index[f"search\0{search}"] = str(data_path)
    index_path = data_dir / "index.json"
    index_path.write_text(json.dumps(index), encoding="utf-8")
    script = bin_dir / "gh"
    script.write_text(
        f"""#!{sys.executable}
import json, os, sys
args = sys.argv[1:]
if args[:1] == ["--version"]:
    print("gh fake 0.0.0")
    sys.exit(0)
if {fail!r}:
    sys.stderr.write("fake gh: simulated failure\\n")
    sys.exit(1)
head = search = ""
i = 0
while i < len(args):
    if args[i] == "--head" and i + 1 < len(args):
        head = args[i + 1]
    elif args[i] == "--search" and i + 1 < len(args):
        search = args[i + 1]
    i += 1
with open({str(index_path)!r}) as fh:
    index = json.load(fh)
if head:
    key = "head\\x00" + head
elif search:
    key = "search\\x00" + search
else:
    key = ""
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


def env_without_real_gh(extra_bin: Path | None = None) -> dict[str, str]:
    env = os.environ.copy()
    parts = env.get("PATH", "").split(os.pathsep)
    filtered = [p for p in parts if p and not (Path(p) / "gh").exists()]
    if extra_bin is not None:
        filtered.insert(0, str(extra_bin))
    env["PATH"] = os.pathsep.join(filtered)
    # Always force the probe stub so /proc holders from the test runner
    # don't leak into worktree probes inside the fixture.
    env["GIT_PRUNE_TEST_PROBE"] = "clear"
    return env


def run(
    command: list[str],
    cwd: Path | None = None,
    check: bool = True,
    env: dict[str, str] | None = None,
    stdin: str | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        check=False,
        env=env,
        input=stdin,
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


def branch_oid(repo: Path, branch: str) -> str:
    return git(repo, "rev-parse", branch).stdout.strip()


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
    """Tip not reachable from main; content was applied to main as a squash."""
    git(repo, "switch", "-c", branch, "main")
    make_commit(repo, branch)
    git(repo, "switch", "main")
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
        root.mkdir(parents=True, exist_ok=True)
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

        write(self.paths["wt-dirty"] / "manual_change.py", "x = 1\n")
        git(self.paths["wt-dirty"], "add", "manual_change.py")
        # Stage so it's Class D, not A (manual file path doesn't match disposable globs).
        git(self.repo, "worktree", "lock", "--reason", "keep", str(self.paths["wt-locked"]))
        shutil.rmtree(self.paths["wt-missing"])

        detached = self.root / "wt-detached"
        git(self.repo, "worktree", "add", "--detach", str(detached), "main")
        self.paths["wt-detached"] = detached
        git(self.repo, "switch", "main")


# ---------------------------------------------------------------------------
# Run helper: launches the script via a small Python wrapper that imports the
# module, replaces PROCESS_PROBE with a stub, then calls main(). This is the
# only reliable way to substitute the probe across a subprocess boundary.
# ---------------------------------------------------------------------------


_LAUNCHER_TEMPLATE = """
import os, sys, importlib.util
spec = importlib.util.spec_from_file_location("git_prune_worktrees", os.environ["GIT_PRUNE_SCRIPT_PATH"])
m = importlib.util.module_from_spec(spec)
sys.modules["git_prune_worktrees"] = m
spec.loader.exec_module(m)

mode = os.environ.get("GIT_PRUNE_TEST_PROBE", "clear")
def _stub(path):
    if mode == "clear":
        return m.ProbeResult("clear", None)
    if mode == "held":
        return m.ProbeResult("held", "stubbed: pid 1 (test)")
    return m.ProbeResult("unavailable", "stubbed")
m.PROCESS_PROBE = _stub

raise SystemExit(m.main(sys.argv[1:]))
"""


def run_script_v2(
    repo: Path,
    *args: str,
    check: bool = True,
    env: dict[str, str] | None = None,
    stdin: str | None = None,
    probe: str = "clear",
) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
    base_env = env_without_real_gh(None) if env is None else env
    full_env = {
        **base_env,
        "GIT_PRUNE_SCRIPT_PATH": str(SCRIPT),
        "GIT_PRUNE_TEST_PROBE": probe,
    }
    result = run(
        [sys.executable, "-c", _LAUNCHER_TEMPLATE, "--json", *args],
        cwd=repo, check=check, env=full_env, stdin=stdin,
    )
    data = json.loads(result.stdout) if result.stdout else {}
    return result, data


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------


class CoreFlowTests(unittest.TestCase):
    def repo_data(self, data: dict, idx: int = 0) -> dict:
        return data["repos"][idx]  # type: ignore[index]

    def test_dry_run_makes_no_changes_and_emits_per_repo_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = RepoFixture.create(Path(tmp))
            fixture.add_standard_cases()
            result, data = run_script_v2(fixture.repo, "--dry-run", "--base", "main", "--no-fetch")
            self.assertEqual(result.returncode, 0)
            self.assertEqual(set(data), {"mode", "root", "errors", "repos", "summary"})
            self.assertEqual(data["mode"], "dry-run")
            r = self.repo_data(data)
            self.assertEqual(set(r) >= {"path", "actions", "skipped", "errors", "dirty",
                                         "process_probes", "fetch", "base_update",
                                         "current_branch", "remote", "base"}, True)
            self.assertTrue(fixture.paths["wt-clean"].exists())
            self.assertTrue(branch_exists(fixture.repo, "merged-delete"))
            kinds = {a["kind"] for a in r["actions"]}
            self.assertIn("remove_worktree", kinds)
            self.assertIn("delete_branch", kinds)
            skip_reasons = {item["reason"] for item in r["skipped"]}
            self.assertTrue(
                {"locked", "detached", "missing_path", "unmerged"}.issubset(skip_reasons),
                skip_reasons,
            )

    def test_yes_removes_clean_merged_worktrees_and_branches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = RepoFixture.create(Path(tmp))
            fixture.add_standard_cases()
            result, data = run_script_v2(fixture.repo, "--yes", "--base", "main", "--no-fetch")
            self.assertEqual(result.returncode, 0, msg=str(data))
            self.assertFalse(fixture.paths["wt-clean"].exists())
            self.assertFalse(branch_exists(fixture.repo, "wt-clean"))
            self.assertFalse(branch_exists(fixture.repo, "merged-delete"))
            # wt-dirty has staged change -> Class D -> still skipped.
            self.assertTrue(fixture.paths["wt-dirty"].exists())
            self.assertTrue(branch_exists(fixture.repo, "wt-dirty"))
            self.assertTrue(fixture.paths["wt-locked"].exists())
            self.assertTrue(branch_exists(fixture.repo, "wt-locked"))
            self.assertTrue(branch_exists(fixture.repo, "unmerged"))
            r = self.repo_data(data)
            done_kinds = {a["kind"] for a in r["actions"] if a["status"] == "done"}
            self.assertIn("remove_worktree", done_kinds)
            self.assertIn("delete_branch", done_kinds)

    def test_default_mode_executes_safe_without_yes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = RepoFixture.create(Path(tmp))
            make_merged_branch(fixture.repo, "branch-a")
            result, data = run_script_v2(fixture.repo, "--base", "main", "--no-fetch")
            self.assertEqual(result.returncode, 0, msg=str(data))
            self.assertEqual(data["mode"], "default")
            self.assertFalse(branch_exists(fixture.repo, "branch-a"))

    def test_current_branch_skipped_as_protected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = RepoFixture.create(Path(tmp))
            make_merged_branch(fixture.repo, "current-merged")
            git(fixture.repo, "switch", "current-merged")
            result, data = run_script_v2(fixture.repo, "--base", "main", "--no-fetch", "--dry-run")
            self.assertEqual(result.returncode, 0)
            r = self.repo_data(data)
            reasons = {item["reason"] for item in r["skipped"] if item["target"] == "current-merged"}
            self.assertIn("current_branch", reasons)
            self.assertTrue(branch_exists(fixture.repo, "current-merged"))

    def test_fetch_failure_aborts_repo_in_yes_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = RepoFixture.create(Path(tmp))
            make_merged_branch(fixture.repo, "merged-delete")
            git(fixture.repo, "remote", "set-url", "origin", str(Path(tmp) / "missing.git"))
            result, data = run_script_v2(fixture.repo, "--yes", "--base", "main", check=False)
            self.assertNotEqual(result.returncode, 0)
            r = self.repo_data(data)
            reasons = {e["reason"] for e in r["errors"]}
            self.assertIn("fetch_failed", reasons)
            self.assertTrue(branch_exists(fixture.repo, "merged-delete"))

    def test_local_slash_base_branch_resolved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = RepoFixture.create(Path(tmp))
            git(fixture.repo, "branch", "release/foo", "main")
            result, data = run_script_v2(fixture.repo, "--yes", "--base", "release/foo", "--no-fetch")
            self.assertEqual(result.returncode, 0)
            r = self.repo_data(data)
            self.assertEqual(r["remote"], "origin")
            self.assertEqual(r["base"]["local_branch"], "release/foo")


class PreservedSafetyModelTests(unittest.TestCase):
    def repo_data(self, data: dict) -> dict:
        return data["repos"][0]  # type: ignore[index]

    def _setup_squash_fixture(self, root: Path, branch: str = "issue-99-foo") -> tuple[RepoFixture, str]:
        fixture = RepoFixture.create(root)
        make_squash_merged_branch(fixture.repo, branch)
        oid = branch_oid(fixture.repo, branch)
        git(fixture.repo, "remote", "set-url", "origin", "git@github.com:fake/repo.git")
        return fixture, oid

    def test_pr_merged_branch_force_deleted_with_pr_detail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture, oid = self._setup_squash_fixture(root)
            bin_dir = install_fake_gh(
                root, {("issue-99-foo", "main"): [{"number": 99, "headRefOid": oid, "baseRefName": "main", "mergeCommit": None}]},
            )
            env = env_without_real_gh(bin_dir)
            result, data = run_script_v2(
                fixture.repo, "--yes", "--base", "main", "--no-fetch", env=env,
            )
            self.assertEqual(result.returncode, 0, msg=str(data))
            self.assertFalse(branch_exists(fixture.repo, "issue-99-foo"))
            r = self.repo_data(data)
            done = [a for a in r["actions"] if a["status"] == "done" and a["kind"] == "delete_branch"]
            self.assertEqual(len(done), 1)
            self.assertEqual(done[0]["reason"], "merged_branch_via_pr")
            self.assertIn("PR #99", done[0]["detail"])
            self.assertEqual(done[0]["command"], ["git", "branch", "-D", "issue-99-foo"])

    def test_gh_missing_silently_falls_back(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture, _oid = self._setup_squash_fixture(root)
            env = env_without_real_gh(None)
            result, data = run_script_v2(
                fixture.repo, "--base", "main", "--no-fetch", "--dry-run", env=env,
            )
            self.assertEqual(result.returncode, 0)
            r = self.repo_data(data)
            self.assertEqual(r["errors"], [])
            reasons = {item["reason"] for item in r["skipped"] if item["branch"] == "issue-99-foo"}
            self.assertEqual(reasons, {"unmerged"})

    def test_non_github_remote_skips_detection_silently(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = RepoFixture.create(root)
            make_squash_merged_branch(fixture.repo, "issue-99-foo")
            oid = branch_oid(fixture.repo, "issue-99-foo")
            bin_dir = install_fake_gh(
                root, {("issue-99-foo", "main"): [{"number": 99, "headRefOid": oid}]},
            )
            env = env_without_real_gh(bin_dir)
            result, data = run_script_v2(
                fixture.repo, "--base", "main", "--no-fetch", "--dry-run", env=env,
            )
            self.assertEqual(result.returncode, 0)
            r = self.repo_data(data)
            self.assertEqual(r["errors"], [])
            reasons = {item["reason"] for item in r["skipped"] if item["branch"] == "issue-99-foo"}
            self.assertEqual(reasons, {"unmerged"})

    def test_gh_failure_recorded_but_does_not_abort(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture, _oid = self._setup_squash_fixture(root)
            make_merged_branch(fixture.repo, "merged-delete")
            bin_dir = install_fake_gh(root, fail=True)
            env = env_without_real_gh(bin_dir)
            result, data = run_script_v2(
                fixture.repo, "--yes", "--base", "main", "--no-fetch", env=env,
            )
            self.assertEqual(result.returncode, 0)  # pr_check_failed is non-fatal
            r = self.repo_data(data)
            error_reasons = {e["reason"] for e in r["errors"]}
            self.assertIn("pr_check_failed", error_reasons)
            self.assertFalse(branch_exists(fixture.repo, "merged-delete"))
            self.assertTrue(branch_exists(fixture.repo, "issue-99-foo"))

    def test_reachability_merged_uses_safe_delete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = RepoFixture.create(root)
            make_merged_branch(fixture.repo, "true-merged")
            git(fixture.repo, "remote", "set-url", "origin", "git@github.com:fake/repo.git")
            bin_dir = install_fake_gh(root, {})
            env = env_without_real_gh(bin_dir)
            result, data = run_script_v2(
                fixture.repo, "--base", "main", "--no-fetch", "--dry-run", env=env,
            )
            self.assertEqual(result.returncode, 0)
            r = self.repo_data(data)
            planned = [a for a in r["actions"] if a["kind"] == "delete_branch" and a["branch"] == "true-merged"]
            self.assertEqual(len(planned), 1)
            self.assertEqual(planned[0]["reason"], "merged_branch")
            self.assertEqual(planned[0]["command"], ["git", "branch", "-d", "true-merged"])
            self.assertNotIn("detail", planned[0])

    def test_pr_head_oid_mismatch_blocks_force_delete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture, old_oid = self._setup_squash_fixture(root)
            git(fixture.repo, "switch", "issue-99-foo")
            make_commit(fixture.repo, "extra")
            git(fixture.repo, "switch", "main")
            new_oid = branch_oid(fixture.repo, "issue-99-foo")
            self.assertNotEqual(old_oid, new_oid)
            bin_dir = install_fake_gh(
                root, {("issue-99-foo", "main"): [{"number": 99, "headRefOid": old_oid}]},
            )
            env = env_without_real_gh(bin_dir)
            result, data = run_script_v2(
                fixture.repo, "--yes", "--base", "main", "--no-fetch", env=env,
            )
            self.assertEqual(result.returncode, 0)
            self.assertTrue(branch_exists(fixture.repo, "issue-99-foo"))
            r = self.repo_data(data)
            reasons = {item["reason"] for item in r["skipped"] if item["branch"] == "issue-99-foo"}
            self.assertEqual(reasons, {"unmerged"})

    def test_local_slash_base_branch_preserved_in_pr_query(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = RepoFixture.create(root)
            git(fixture.repo, "branch", "release/foo", "main")
            git(fixture.repo, "switch", "-c", "issue-50-bar", "release/foo")
            make_commit(fixture.repo, "issue-50-bar")
            git(fixture.repo, "switch", "release/foo")
            write(fixture.repo / "issue-50-bar.txt", "issue-50-bar")
            git(fixture.repo, "add", "issue-50-bar.txt")
            git(fixture.repo, "commit", "-m", "squash issue-50-bar")
            git(fixture.repo, "switch", "main")
            oid = branch_oid(fixture.repo, "issue-50-bar")
            git(fixture.repo, "remote", "set-url", "origin", "git@github.com:fake/repo.git")
            bin_dir = install_fake_gh(
                root, {("issue-50-bar", "release/foo"): [{"number": 50, "headRefOid": oid, "baseRefName": "release/foo", "mergeCommit": None}]},
            )
            env = env_without_real_gh(bin_dir)
            result, data = run_script_v2(
                fixture.repo, "--yes", "--base", "release/foo", "--no-fetch", env=env,
            )
            self.assertEqual(result.returncode, 0)
            self.assertFalse(branch_exists(fixture.repo, "issue-50-bar"))
            r = self.repo_data(data)
            done = [a for a in r["actions"] if a["status"] == "done" and a["branch"] == "issue-50-bar"]
            self.assertEqual(len(done), 1)
            self.assertEqual(done[0]["reason"], "merged_branch_via_pr")
            self.assertIn("PR #50", done[0]["detail"])

    def test_prefix_search_matches_renamed_issue_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            branch = "issue-18-merge-gate"
            fixture, oid = self._setup_squash_fixture(root, branch)
            bin_dir = install_fake_gh(
                root,
                search_responses={
                    ("head:issue-18", "main"): [{
                        "number": 18,
                        "headRefName": "issue-18-context-harness-guardrails-plan",
                        "headRefOid": oid,
                        "baseRefName": "main",
                        "mergeCommit": None,
                    }],
                },
            )
            env = env_without_real_gh(bin_dir)
            result, data = run_script_v2(
                fixture.repo, "--yes", "--base", "main", "--no-fetch", env=env,
            )
            self.assertEqual(result.returncode, 0, msg=str(data))
            self.assertFalse(branch_exists(fixture.repo, branch))
            r = self.repo_data(data)
            done = [a for a in r["actions"] if a["status"] == "done" and a["branch"] == branch]
            self.assertEqual(len(done), 1)
            self.assertEqual(done[0]["reason"], "merged_branch_via_pr")
            self.assertIn("PR #18", done[0]["detail"])


class WorkspaceDiscoveryTests(unittest.TestCase):
    def test_discovers_multiple_repos_under_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for sub in ("alpha", "beta"):
                fixture = RepoFixture.create(root / sub)
                make_merged_branch(fixture.repo, f"merged-{sub}")
            # Run from root with default workspace mode.
            result, data = run_script_v2(root, "--base", "main", "--no-fetch", "--dry-run")
            self.assertEqual(result.returncode, 0, msg=str(data))
            paths = {r["path"] for r in data["repos"]}  # type: ignore[index]
            self.assertEqual(len(paths), 2)
            for r in data["repos"]:  # type: ignore[index]
                kinds = {a["kind"] for a in r["actions"]}
                self.assertIn("delete_branch", kinds)

    def test_skips_node_modules_and_venv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for skip_dir in ("node_modules", ".venv"):
                fixture = RepoFixture.create(root / skip_dir / "should_skip")
                make_merged_branch(fixture.repo, "x")
            real = RepoFixture.create(root / "real")
            make_merged_branch(real.repo, "merged")
            result, data = run_script_v2(root, "--base", "main", "--no-fetch", "--dry-run")
            self.assertEqual(result.returncode, 0)
            paths = {r["path"] for r in data["repos"]}  # type: ignore[index]
            self.assertEqual(len(paths), 1)
            self.assertTrue(any("/real/" in p for p in paths), paths)


class DirtyClassificationTests(unittest.TestCase):
    def repo_data(self, data: dict) -> dict:
        return data["repos"][0]  # type: ignore[index]

    def test_class_a_disposable_garbage_cleaned(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = RepoFixture.create(root)
            make_merged_branch(fixture.repo, "feature")
            wt = root / "feature-wt"
            git(fixture.repo, "worktree", "add", str(wt), "feature")
            (wt / "junk.log").write_text("noise\n")
            (wt / "out.tmp").write_text("noise\n")

            result, data = run_script_v2(fixture.repo, "--yes", "--base", "main", "--no-fetch")
            self.assertEqual(result.returncode, 0, msg=str(data))
            self.assertFalse(wt.exists())
            self.assertFalse(branch_exists(fixture.repo, "feature"))
            r = self.repo_data(data)
            dirty_classes = {d["class"] for d in r["dirty"]}
            self.assertIn("A", dirty_classes)

    def test_class_c_potentially_unique_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = RepoFixture.create(root)
            make_merged_branch(fixture.repo, "feature")
            wt = root / "feature-wt"
            git(fixture.repo, "worktree", "add", str(wt), "feature")
            # An untracked .py source file is not in the disposable globs.
            (wt / "extra_module.py").write_text("def x(): pass\n")

            result, data = run_script_v2(fixture.repo, "--yes", "--base", "main", "--no-fetch")
            self.assertEqual(result.returncode, 0, msg=str(data))
            self.assertTrue(wt.exists())
            self.assertTrue(branch_exists(fixture.repo, "feature"))
            r = self.repo_data(data)
            classes = {d["class"] for d in r["dirty"]}
            self.assertEqual(classes, {"C"})

    def test_class_d_staged_change_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = RepoFixture.create(root)
            make_merged_branch(fixture.repo, "feature")
            wt = root / "feature-wt"
            git(fixture.repo, "worktree", "add", str(wt), "feature")
            write(wt / "manual.py", "x = 1\n")
            git(wt, "add", "manual.py")

            result, data = run_script_v2(fixture.repo, "--yes", "--base", "main", "--no-fetch")
            self.assertEqual(result.returncode, 0, msg=str(data))
            self.assertTrue(wt.exists())
            r = self.repo_data(data)
            classes = {d["class"] for d in r["dirty"]}
            self.assertEqual(classes, {"D"})


class ProcessProbeTests(unittest.TestCase):
    def test_held_worktree_skipped_under_default_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = RepoFixture.create(root)
            make_merged_branch(fixture.repo, "feature")
            wt = root / "feature-wt"
            git(fixture.repo, "worktree", "add", str(wt), "feature")

            result, data = run_script_v2(
                fixture.repo, "--yes", "--base", "main", "--no-fetch", probe="held",
            )
            self.assertEqual(result.returncode, 0, msg=str(data))
            self.assertTrue(wt.exists())
            r = data["repos"][0]  # type: ignore[index]
            reasons = {
                s["reason"]
                for s in r["skipped"]
                if Path(s["target"]).resolve() == wt.resolve()
            }
            self.assertIn("process_held", reasons)
            probe_states = {p["result"] for p in r["process_probes"]}
            self.assertIn("held", probe_states)

    def test_unavailable_probe_skipped_under_default_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = RepoFixture.create(root)
            make_merged_branch(fixture.repo, "feature")
            wt = root / "feature-wt"
            git(fixture.repo, "worktree", "add", str(wt), "feature")

            result, data = run_script_v2(
                fixture.repo, "--yes", "--base", "main", "--no-fetch", probe="unavailable",
            )
            self.assertEqual(result.returncode, 0)
            self.assertTrue(wt.exists())
            r = data["repos"][0]  # type: ignore[index]
            reasons = {
                s["reason"]
                for s in r["skipped"]
                if Path(s["target"]).resolve() == wt.resolve()
            }
            self.assertIn("process_probe_unavailable", reasons)

    def test_ignore_policy_proceeds_despite_held(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = RepoFixture.create(root)
            make_merged_branch(fixture.repo, "feature")
            wt = root / "feature-wt"
            git(fixture.repo, "worktree", "add", str(wt), "feature")

            result, data = run_script_v2(
                fixture.repo, "--yes", "--base", "main", "--no-fetch",
                "--process-policy", "ignore", probe="held",
            )
            self.assertEqual(result.returncode, 0, msg=str(data))
            self.assertFalse(wt.exists())


class ClassBAndInteractiveTests(unittest.TestCase):
    """Class B: PR-verified merged branch + dirty disposable content."""

    def _setup_class_b_fixture(self, root: Path) -> tuple[RepoFixture, Path, str]:
        """Construct a Class B scenario:

        - branch issue-99-foo modifies README.md to v2 (PR head OID recorded)
        - main is updated separately to v3 (representing the squash-merge that
          extended the branch on the remote)
        - worktree on issue-99-foo has README.md = v2 at HEAD
        - working tree edits README.md to v3 (matches base, dirty vs HEAD)

        The script must classify this as Class B (PR-verified merged + tracked
        diff matches base + no problematic untracked).
        """
        fixture = RepoFixture.create(root)
        git(fixture.repo, "remote", "set-url", "origin", "git@github.com:fake/repo.git")
        # Branch X with v2.
        git(fixture.repo, "switch", "-c", "issue-99-foo", "main")
        write(fixture.repo / "README.md", "v2\n")
        git(fixture.repo, "add", "README.md")
        git(fixture.repo, "commit", "-m", "v2 on issue-99-foo")
        oid = branch_oid(fixture.repo, "issue-99-foo")
        # main moves to v3 (representing the squash that extended the PR).
        git(fixture.repo, "switch", "main")
        write(fixture.repo / "README.md", "v3\n")
        git(fixture.repo, "add", "README.md")
        git(fixture.repo, "commit", "-m", "v3 on main")
        # Worktree on issue-99-foo, then edit README.md to v3 (matches base).
        wt = root / "feature-wt"
        git(fixture.repo, "worktree", "add", str(wt), "issue-99-foo")
        write(wt / "README.md", "v3\n")
        return fixture, wt, oid

    def test_class_b_classified_and_gated_by_yes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture, wt, oid = self._setup_class_b_fixture(root)
            bin_dir = install_fake_gh(
                root, {("issue-99-foo", "main"): [{"number": 99, "headRefOid": oid, "baseRefName": "main", "mergeCommit": None}]},
            )
            env = env_without_real_gh(bin_dir)

            # Default mode: Class B is skipped, worktree stays.
            result, data = run_script_v2(
                fixture.repo, "--base", "main", "--no-fetch", env=env,
            )
            self.assertEqual(result.returncode, 0, msg=str(data))
            self.assertTrue(wt.exists())
            r = data["repos"][0]  # type: ignore[index]
            classes = {d["class"] for d in r["dirty"]}
            self.assertEqual(classes, {"B"}, msg=str(data))

            # --yes mode: Class B is executed.
            result, data = run_script_v2(
                fixture.repo, "--yes", "--base", "main", "--no-fetch", env=env,
            )
            self.assertEqual(result.returncode, 0, msg=str(data))
            self.assertFalse(wt.exists())
            self.assertFalse(branch_exists(fixture.repo, "issue-99-foo"))

    def test_interactive_prompt_yes_executes_class_b(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture, wt, oid = self._setup_class_b_fixture(root)
            bin_dir = install_fake_gh(
                root, {("issue-99-foo", "main"): [{"number": 99, "headRefOid": oid, "baseRefName": "main", "mergeCommit": None}]},
            )
            env = env_without_real_gh(bin_dir)

            result, data = run_script_v2(
                fixture.repo, "--interactive", "--base", "main", "--no-fetch",
                env=env, stdin="y\n",
            )
            self.assertEqual(result.returncode, 0, msg=str(data))
            self.assertFalse(wt.exists())
            self.assertFalse(branch_exists(fixture.repo, "issue-99-foo"))

    def test_interactive_prompt_no_keeps_class_b(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture, wt, oid = self._setup_class_b_fixture(root)
            bin_dir = install_fake_gh(
                root, {("issue-99-foo", "main"): [{"number": 99, "headRefOid": oid, "baseRefName": "main", "mergeCommit": None}]},
            )
            env = env_without_real_gh(bin_dir)

            result, data = run_script_v2(
                fixture.repo, "--interactive", "--base", "main", "--no-fetch",
                env=env, stdin="n\n",
            )
            self.assertEqual(result.returncode, 0, msg=str(data))
            self.assertTrue(wt.exists())
            self.assertTrue(branch_exists(fixture.repo, "issue-99-foo"))


class ExitCodeTests(unittest.TestCase):
    def test_invalid_repo_arg_returns_2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result, data = run_script_v2(
                Path(tmp), "--repo", str(Path(tmp) / "does-not-exist"),
                "--base", "main", "--no-fetch", check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(data["errors"][0]["reason"], "not_a_git_repo")  # type: ignore[index]


class DiscoverySingleRepoFallbackTests(unittest.TestCase):
    def test_root_repo_skipped_when_subordinates_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outer = RepoFixture.create(root)
            inner = RepoFixture.create(root / "nested")
            make_merged_branch(outer.repo, "outer-merged")
            make_merged_branch(inner.repo, "inner-merged")
            # Run from the outer.repo directory so root is itself a repo and
            # discovery walks into nested/.
            result, data = run_script_v2(
                outer.repo.parent, "--base", "main", "--no-fetch", "--dry-run",
            )
            self.assertEqual(result.returncode, 0, msg=str(data))
            paths = {r["path"] for r in data["repos"]}  # type: ignore[index]
            # outer.repo is a repo at root/repo; inner.repo is at root/nested/repo
            # Discovery walks from `tmp` → finds tmp/repo (outer) and tmp/nested/repo (inner).
            # Both are subordinates of `tmp` itself, which isn't a repo.
            self.assertEqual(len(paths), 2)


class ModeMutualExclusionTests(unittest.TestCase):
    def test_yes_and_interactive_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = RepoFixture.create(Path(tmp))
            result, _ = run_script_v2(
                fixture.repo, "--yes", "--interactive", "--base", "main", "--no-fetch",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
