---
name: git-prune-worktrees
description: Safely prune stale remote-tracking refs, clean merged linked worktrees, merged local branches, and stale Git worktree metadata.
---

# Git Prune Worktrees

Use this skill when the user asks to clean merged local branches, stale remote-tracking refs, linked Git worktrees, or stale worktree metadata.

## Core workflow

1. Run the bundled script in dry-run mode first:

   ```sh
   python3 skills/git-prune-worktrees/scripts/git_prune_worktrees.py
   ```

2. Review the summary with the user. Report planned removals, branch deletions, skipped items, and errors.
3. Rerun with `--yes` only after the user explicitly asks for cleanup or approves the dry-run plan:

   ```sh
   python3 skills/git-prune-worktrees/scripts/git_prune_worktrees.py --yes
   ```

The script is the source of truth for cleanup eligibility. Do not duplicate its branch or worktree decision logic in prose.

## Common options

- `--base origin/main`: merge target for strict reachability checks.
- `--remote origin`: remote used for fetch/prune and for GitHub PR detection.
- `--no-fetch`: skip fetch/prune when network access is unavailable or not approved.
- `--no-detect-pr-merged`: disable GitHub PR-merged detection (default: enabled when `gh` is on PATH and the remote points to GitHub).
- `--switch-base`: with `--yes`, switch away from a merged current branch before deleting it.
- `--include-pattern <glob>`: only consider matching local branch names.
- `--exclude-pattern <glob>`: protect matching local branch names. Exclude wins over include.
- `--json`: emit one machine-readable JSON object.

## Approval and failure handling

- Dry-run mode uses `git fetch --dry-run --prune`; it should not mutate refs.
- `--yes` may run `git fetch --prune`, `git worktree remove`, `git switch`, `git merge --ff-only`, `git branch -d`, `git branch -D` (only for PR-verified branches; see Safety model), and `git worktree prune`.
- If network access or `.git` mutation is blocked by the environment, use the environment's normal approval path. Do not bypass Git by deleting files manually.
- The script must not use `git worktree remove --force`.

## Safety model

A branch is considered merged when either condition holds:

1. **Reachability**: the branch tip is reachable from `--base` (true merge or fast-forward). Action uses `git branch -d` and reports `reason: merged_branch`.
2. **PR-verified**: a merged GitHub PR exists with `head = <branch>` and `base = <base>`, **and** the local branch tip OID equals the PR's recorded `headRefOid` (covers squash and rebase merges). Action uses `git branch -D` and reports `reason: merged_branch_via_pr` with `detail: merged via PR #<N>` recording the evidence.

`git branch -D` is permitted only for case 2; the recorded PR# is required as the audit trail. The headRefOid match guards against branch-name reuse: if a branch was deleted and recreated (or extended with new local commits) after a PR with the same name was merged, the local tip will not match the merged PR's head and the branch is treated as unmerged. Cherry-picks without an associated merged PR remain manual cleanup cases.

PR detection is enabled by default. It is automatically and silently skipped when `gh` is not on PATH or when the selected remote URL does not contain `github.com`. Use `--no-detect-pr-merged` to disable it explicitly. Per-branch `gh` failures are reported as `pr_check_failed` errors but do not abort the run.

The script skips dirty, locked, detached, missing-path, unmerged, protected, current, and checked-out branches or worktrees with explicit reasons. Treat skipped items as requiring manual review or a later rerun after the blocking condition is resolved.
