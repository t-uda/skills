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

- Dry-run mode uses `git fetch --dry-run --prune`; it should not mutate refs. However, `git fetch origin <sha>` may be run in both modes to fetch specific PR head commits for ancestry and tree checks; this downloads a loose object only and does not mutate branches.
- `--yes` may run `git fetch --prune`, `git fetch origin <sha>` (PR head for OID-mismatch checks), `git worktree remove`, `git switch`, `git merge --ff-only`, `git branch -d`, `git branch -D` (only for PR-verified branches; see Safety model), and `git worktree prune`.
- If network access or `.git` mutation is blocked by the environment, use the environment's normal approval path. Do not bypass Git by deleting files manually.
- The script must not use `git worktree remove --force`.

## Safety model

A branch is considered merged when either condition holds:

1. **Reachability**: the branch tip is reachable from `--base` (true merge or fast-forward). Action uses `git branch -d` and reports `reason: merged_branch`.
2. **PR-verified**: a merged GitHub PR exists with `head = <branch>` and `base = <base>`, and at least one of the following holds:
   - **(a) exact match**: the local branch tip OID equals the PR's recorded `headRefOid`.
   - **(b) tree equality**: after fetching the PR head via `git fetch origin <headRefOid>`, the local branch tip and the PR head share the same file-tree OID (`<tip>^{tree} == <pr_head>^{tree}`). Covers cases where commit metadata (timestamp, author) differs but file content is identical — e.g., independent re-creation of the same commit by separate agents.
   - **(c) ancestry**: after fetching the PR head, the local tip is a strict ancestor (`git merge-base --is-ancestor`). Covers cases where the remote branch was extended beyond the local branch before merging.

   If `git fetch origin <headRefOid>` fails (server does not support SHA fetch or network error), the branch is treated as unmerged (safe fallback). Action uses `git branch -D` and reports `reason: merged_branch_via_pr` with `detail: merged via PR #<N>` recording the evidence.

`git branch -D` is permitted only for case 2; the recorded PR# is required as the audit trail. All three sub-checks guard against branch-name reuse: new local commits added after a PR was merged will differ in tree content and will not be ancestors of the old PR's `headRefOid`. Cherry-picks without an associated merged PR remain manual cleanup cases.

PR detection is enabled by default. It is automatically and silently skipped when `gh` is not on PATH or when the selected remote URL does not contain `github.com`. Use `--no-detect-pr-merged` to disable it explicitly. Per-branch `gh` failures are reported as `pr_check_failed` errors but do not abort the run.

The script skips dirty, locked, detached, missing-path, unmerged, protected, current, and checked-out branches or worktrees with explicit reasons. Treat skipped items as requiring manual review or a later rerun after the blocking condition is resolved.
