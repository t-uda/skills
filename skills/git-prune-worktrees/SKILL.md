---
name: git-prune-worktrees
description: Workspace-level Git cleanup — discover repositories under the current directory and prune merged branches, merged linked worktrees, stale remote-tracking refs, and stale worktree metadata.
---

# Git Prune Worktrees

Use this skill when the user asks to clean merged local branches, stale
remote-tracking refs, linked Git worktrees, or stale worktree metadata —
either in a single repository or across all repositories under a workspace
root.

## Core workflow

The bundled script is the source of truth for cleanup eligibility. The agent
chooses one mode based on user intent and runs the script once.

| User intent | Mode |
|---|---|
| Routine cleanup request | `--yes` |
| "Show me what would be cleaned" / preview / mutation or network blocked | `--dry-run` |
| User explicitly opts into per-Class-B confirmation | `--interactive` |

Pick exactly one. Default invocation:

```sh
python3 skills/git-prune-worktrees/scripts/git_prune_worktrees.py --yes
```

The script defaults to workspace mode rooted at the current working directory.
If the CWD is itself a Git repository and discovery finds no subordinate
repositories, the script operates on that single repo.

Do not chain modes within a single response. Do not ask for repeated
per-repository or per-branch confirmation. The script asks at most one
consolidated y/N prompt, and only in `--interactive` mode.

## Common options

- `--root <path>`: workspace root (default: cwd).
- `--repo <path>`: repeatable; bypass discovery and target specific repos.
- `--max-depth <n>`: discovery depth (default: 4).
- `--base origin/main`: merge target.
- `--remote origin`: remote used for fetch/prune and PR-merged detection.
- `--no-fetch`: skip fetch/prune when network access is unavailable.
- `--no-update-base`: skip fast-forward of the local base branch.
- `--process-policy {skip,ask,ignore}`: how to treat worktrees held by live
  processes (default: skip).
- `--garbage-glob <pat>`: extend the disposable-glob list (additive only).
- `--json`: emit one machine-readable JSON object.

## Agent invocation contract

The agent does **not** make per-item judgments. The script's deterministic
Class A/B/C/D dirty classification, PR-verified merge logic, protected-branch
list, and process probes are authoritative.

The agent must not:

- second-guess the classification;
- attempt to discard, stash, or rescue Class C/D items on the user's behalf;
- ask the user to adjudicate individual files (the consolidated prompt is the
  only sanctioned interaction point).

If the user disagrees with a classification, the resolution is to fix the
rules — `--garbage-glob`, `.gitignore`, or a code change — not an ad hoc
override.

### Re-execution

The script is idempotent. The agent may re-run it only when:

- the previous run reported `held` process probes and the user has confirmed
  the holding processes are gone; or
- the previous run reported `local_base_not_updated` for a transient reason
  the user has since cleared; or
- the previous run was `--dry-run` and the user approved the plan.

The agent must not re-run with a different mode hoping for a different
classification, or loop without explicit user instruction.

### Reporting back

After a run, report the JSON `summary` plus any non-empty `skipped` and
`errors` lists. Class C/D items are surfaced verbatim; do not propose
remedies unless the user asks.

## Safety model

A branch is considered merged when either condition holds:

1. **Reachability**: the branch tip is reachable from `--base` (true merge or
   fast-forward). Action uses `git branch -d` and reports
   `reason: merged_branch`.
2. **PR-verified**: a merged GitHub PR exists with `head = <branch>` and
   `base = <base>`, and at least one of the following holds:
   - **(a) exact match**: the local branch tip OID equals the PR's recorded
     `headRefOid`.
   - **(b) tree equality**: after fetching the PR head, the local branch tip
     and the PR head share the same file-tree OID. Covers cases where commit
     metadata differs but file content is identical.
   - **(c) ancestry**: after fetching the PR head, the local tip is a strict
     ancestor. Covers cases where the remote branch was extended beyond the
     local branch before merging.

   `git branch -D` is permitted only for case 2; the recorded PR# is required
   as the audit trail. Action reports `reason: merged_branch_via_pr` with
   `detail: merged via PR #<N>`.

PR detection is enabled automatically when `gh` is on PATH and the remote URL
contains `github.com`. It silently degrades otherwise. Per-branch `gh`
failures are reported as `pr_check_failed` errors but do not abort the run.

Protected branches (never deleted): `{main, master, develop, the resolved
local base branch}` plus any branch checked out as the current branch.

`git worktree remove --force` is forbidden.

## Dirty classification

For each dirty worktree, the script applies deterministic rules; the first
matching class wins.

- **Class D — high-risk** (always skipped): staged changes, merge conflicts,
  submodule status changes, untracked files >10 MiB, dirty state on a
  protected branch.
- **Class A — disposable**: every dirty path is gitignore-ignored or matches
  the built-in disposable-glob list (logs, caches, `__pycache__`,
  `node_modules`, build outputs, etc., extended via `--garbage-glob`).
  Cleaned with path-scoped `git checkout -- <paths>` and
  `git clean -fd -- <paths>`.
- **Class B — subsumed**: branch is PR-verified merged AND tracked diff
  matches base AND every untracked path is Class-A-disposable. Same cleanup
  as Class A; gated by `--yes` or `--interactive`.
- **Class C — potentially unique**: anything else. Always skipped. Not
  auto-discarded.

The script does not stash. Stashing is not part of any flow.

## Process probes

Before removing a worktree, the script probes for live processes whose cwd or
open files lie inside the worktree path. Probes degrade
`/proc/*/cwd` → `lsof +D` → `fuser -m`; tmux pane scan augments best-effort.

Outcomes: `clear` / `held` / `unavailable`.

`--process-policy` default is `skip`: both `held` and `unavailable` skip the
worktree. `ignore` proceeds regardless. `ask` falls back to `skip` outside
the consolidated confirmation path.
