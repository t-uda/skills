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
- `--remote origin`: remote used for fetch/prune.
- `--no-fetch`: skip fetch/prune when network access is unavailable or not approved.
- `--switch-base`: with `--yes`, switch away from a merged current branch before deleting it.
- `--include-pattern <glob>`: only consider matching local branch names.
- `--exclude-pattern <glob>`: protect matching local branch names. Exclude wins over include.
- `--json`: emit one machine-readable JSON object.

## Approval and failure handling

- Dry-run mode uses `git fetch --dry-run --prune`; it should not mutate refs.
- `--yes` may run `git fetch --prune`, `git worktree remove`, `git switch`, `git merge --ff-only`, `git branch -d`, and `git worktree prune`.
- If network access or `.git` mutation is blocked by the environment, use the environment's normal approval path. Do not bypass Git by deleting files manually.
- Never force cleanup. The script must not use `git worktree remove --force` or `git branch -D`.

## Safety model

The first version uses strict Git reachability only. Branches merged by squash, rebase, or cherry-pick are manual cleanup cases.

The script skips dirty, locked, detached, missing-path, unmerged, protected, current, and checked-out branches or worktrees with explicit reasons. Treat skipped items as requiring manual review or a later rerun after the blocking condition is resolved.
