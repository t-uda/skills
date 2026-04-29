---
name: claude-code-advanced-orchestration
description: Operational guidance for using Claude Code as a delegated worker behind a coordinator agent. Covers delegation posture, stable session identity, permission strategy, worktree/tmux patterns, dynamic agents, effort selection, bare-mode auth, MCP trust, and remote-control caveats.
---

# Claude Code Advanced Orchestration

Use this skill when a coordinator agent (the caller) delegates implementation
work to Claude Code (the worker) and needs durable, non-obvious operational
guidance for that handoff.

This skill is **not** a CLI reference. It does not replace `claude --help`.
It captures the patterns that are easy to get wrong and the caveats that
silently waste time or context when ignored.

## When to use

Use this skill when any of the following hold:

- a coordinator agent will spawn Claude Code as a named worker rather than
  implementing work itself
- Claude Code must run unattended for more than a few turns
- the worker session must be re-entered later (`--continue`, `--resume`,
  `--fork-session`)
- the task crosses git worktrees, tmux sessions, or multiple PRs
- session-scoped reviewer / tester / security agents are needed
- the task explicitly requires `--bare`, `--permission-mode`, MCP servers,
  or remote-control

Do not use this skill for one-shot interactive use, simple `claude -p`
prompts, or generic shell setup. Prefer the relevant focused skill instead.

## Core posture: coordinator and delegate

Frame the work as two roles.

- **`<COORDINATOR>`** — the caller. Launches, constrains, monitors, and
  reports. Owns conversation with the user. Does not silently take over the
  worker's task.
- **`<DELEGATE_AGENT>`** — Claude Code, invoked for a specific task. Owns
  the implementation work inside its constraints. Reports completion or
  stop reason back to the coordinator.

Operational rules for the coordinator:

- name the delegate explicitly (`--name <task-slug>`); do not let the
  identity drift mid-task
- pass a single `<WORKFLOW_INSTRUCTION>` (skill or slash command) so the
  delegate's process is auditable
- pass a concrete `<ISSUES>` reference and `<EXPECTED_OUTPUT>` rather than
  open-ended goals
- when the delegate stops because of timeout, max-turns, permission denial,
  policy refusal, or an unhandled error, **report the stop**; do not
  reimplement the task in the coordinator context

Project- or vendor-specific role policy (for example, "the coordinator must
never substitute for the delegate") belongs in the coordinator's own repo,
not in this skill.

## Session identity convention

Pick one stable `<task-slug>` per task and reuse it across:

- git branch: `issue-<id>-<slug>` or `<slug>`
- git worktree directory: `<slug>`
- tmux session name: `<slug>`
- Claude `--name <slug>`
- issue / PR title or reference

This makes `--continue`, `--resume`, log scraping, and tmux re-attach all
predictable from the same string.

Session continuation modes:

- `--continue` resumes the **most recent** session for the **current
  working directory**. It is directory-sensitive: running it from a
  different cwd will not find the prior session. Re-enter the worktree
  first.
- `--resume <session-id>` resumes a specific session id explicitly. Use
  this when the coordinator has stored the id from a prior run.
- `--fork-session` branches a new session from previous context without
  mutating the original. Useful for "what-if" review or parallel exploration
  off a long-running task.
- `--no-session-persistence` runs a one-shot session that is not saved.
  Use for ephemeral review, lint, or analysis where future continuation is
  unwanted.

## Permission strategy

Choose the narrowest permission mode that lets the task finish.

| Goal | `--permission-mode` | Tool scope |
|------|---------------------|------------|
| planning, no edits | `plan` | default tools, no writes |
| bounded autonomous execution | `auto` (or `acceptEdits`) | tight `--allowedTools` |
| read-only review of a diff | default | restrict to `Read`, or pipe diff via `claude -p` |
| trusted sandbox / disposable env | `bypassPermissions` (a.k.a. `--dangerously-skip-permissions`) | full, only inside an isolated sandbox |

Notes:

- For unattended delegation, `--permission-mode auto` with an explicit
  `--allowedTools` allowlist is the usual pairing. Default-deny everything
  the worker should not touch (network calls, destructive shell, secrets).
- `bypassPermissions` removes the safety net; only use it inside a
  container or worktree the user has explicitly designated as disposable,
  never against the host repository.
- `--permission-mode plan` does not guarantee read-only behaviour for
  every tool/MCP combination; treat it as "no edits by Claude itself" and
  still scope tools.

Inspect or audit the configured auto-mode policy with:

- `claude auto-mode defaults` — show the shipped default policy
- `claude auto-mode config` — show the effective merged config
- `claude auto-mode critique` — flag risky settings in the current config

Use these before granting `auto` for a long unattended run.

## Worktree and tmux patterns

Two patterns are useful. Pick one and stay in it for a given task.

### 1. Claude-managed worktree + tmux

```sh
claude -w <task-slug> --tmux --name <task-slug> \
  --permission-mode auto --allowedTools '<...>' \
  --append-system-prompt "<WORKFLOW_INSTRUCTION>" \
  -p "<ISSUES> ... <EXPECTED_OUTPUT>"
```

- `--tmux` requires `--worktree` (`-w`). It will not run without it.
- `--tmux=classic` selects traditional tmux behaviour when the default
  integration is unwanted (for example, when an external pane manager
  already controls the session layout).

### 2. Coordinator-managed worktree + tmux

When the coordinator wants full control over the lifecycle:

1. `git worktree add ../wt/<slug> -b <slug>`
2. `tmux new-session -d -s <slug> -c ../wt/<slug>`
3. `tmux send-keys -t <slug> 'claude --name <slug> ...' Enter`
4. monitor with `tmux capture-pane -pt <slug>`

This is the right shape when the coordinator already owns worktree
hygiene, branch naming, or PR creation and only wants Claude to run inside
a known pane.

## Dynamic agents

Three layers of agent definition exist; pick by lifetime.

- **Session-scoped, ad-hoc**: `--agents '<json>'` defines reviewer, tester,
  or security agents that live only for the current invocation. Use for
  one-off reviews or for orchestrating subagents the coordinator builds on
  the fly.
- **Configured selection**: `--agent <name>` selects an already configured
  agent (project- or user-level). Use when the coordinator has standardised
  agent definitions and wants reproducibility.
- **Persistent project-level**: `.claude/agents/<name>.md` files. Commit
  these when an agent definition is stable and shared across sessions.

Boundaries:

- Dynamic agents are useful as **delegated reviewers / specialists called
  by the worker**, not as a way to fan out work the coordinator should be
  splitting. If the coordinator needs orchestration, do that at the
  coordinator layer; do not shove it into a single Claude session via
  `--agents`.
- Keep the JSON small. Agents whose definitions exceed a few short fields
  belong in a committed `.claude/agents/<name>.md`.
- The `claude agents` management command behaviour should be treated as
  **needs validation** until a specific version has been confirmed in this
  repository. Do not script around it.

## Effort selection

`--effort` controls how aggressively Claude Code spends turns / context on
a single task. Pick the lowest level that still achieves the goal.

| Level | Practical use |
|-------|---------------|
| `low` | mechanical edits, scripted refactors, single-file tweaks |
| `medium` | typical implementation tasks that fit a small feature spec |
| `high` | multi-file changes, ambiguous specs, non-trivial debugging |
| `xhigh` | hard tasks requiring extended exploration; cost rises sharply |
| `max` | last-resort ceiling; reserve for tasks the coordinator has already triaged as complex |

Notes:

- The exact level set is **version-sensitive**. Claude Code 2.1.119 lists
  `xhigh`; earlier notes mention an `auto` value. Confirm against the
  installed binary (`claude --help`) before scripting an effort flag, and
  fail closed (default to `medium`) if the requested level is not present.
- Higher effort multiplies context and token spend. For unattended
  delegation, prefer `medium` and let the coordinator escalate with a
  fresh `--resume` rather than starting at `high`/`xhigh` blindly.

## Bare mode caveat

`--bare` runs without the usual environmental conveniences:

- it does **not** read OAuth tokens from the keychain
- it skips `CLAUDE.md` auto-discovery
- it does not load shell-side login conveniences

In OAuth-based environments (most desktop installs), `--bare` will fail
as "not logged in" unless one of the following is provided explicitly:

- `ANTHROPIC_API_KEY` in the environment, or
- `apiKeyHelper` configured in the user/project settings

Use `--bare` for hermetic CI runs and reproducible scripted invocations.
Do not use it as the default delegation mode in a developer environment;
the missing `CLAUDE.md` discovery silently strips project guidance from
the worker.

## MCP trust and scope

Claude Code can spawn stdio MCP servers from `.mcp.json`. Several inspection
commands trigger that spawn as a side effect:

- `claude mcp list`
- `claude mcp get <name>`
- `claude doctor`

Operational rules:

- run these only inside a directory whose `.mcp.json` you trust
- treat a freshly cloned repository's `.mcp.json` as untrusted by default
- prefer `--strict-mcp-config` when delegating, to refuse silent merges
  with user-level MCP config the worker should not see
- when an MCP server is required for the task, name it explicitly in the
  delegation prompt and document its scope; do not rely on whatever the
  worker's environment happens to load

## Remote-control: rare user-facing handoff only

Claude Code's remote-control / `--spawn=worktree` paths are sometimes
described as a way to dispatch work from a local orchestrator to a remote
session. **Do not treat them as a normal autonomous-execution backend.**

What remote-control actually is:

- a **user-facing handoff** to a claude.ai (or mobile) session
- not a reliable mechanism for transferring local context, handoff
  prompts, or PR/session state back to the local coordinator
- expensive when it gets stuck; can burn usage with little progress

Use remote-control only when **the user themselves** should observe or
intervene through claude.ai or mobile, for example:

- monitoring PR progress while away from the workstation
- responding to user-only confirmation points
- decisions that require the user's authority, authorship, or judgement
- situations where the coordinator must not act on the user's behalf

Do not escalate to remote-control merely because a local Claude task is
mildly stuck. That tends to be context-inefficient and leaves the user
with poor handoff context. If a task should run remotely, decide that at
the start of the task, not midstream.

Mark `remote-control --spawn=worktree` as a **needs-validation** recipe
in this repository; do not promote it to a recommended autonomous
delegation pattern without specific tests covering context handoff,
session/PR survivability, and recovery on the user's side.

## Generic delegation handoff template

A coordinator-to-delegate handoff prompt should be compact and fit any
chat/Discord/CLI gateway. Keep these placeholders generic:

```text
Role: <DELEGATE_AGENT> for <COORDINATOR>.
Workflow: follow <WORKFLOW_INSTRUCTION> for the entire task.
Isolation: <ISOLATION_REQUIREMENT> (e.g. git worktree, sandbox).
Task: <ISSUES>.
Constraints: <PERMISSION_SCOPE>, <ALLOWED_TOOLS>, <EFFORT>.
Output: <EXPECTED_OUTPUT> (PR link, JSON, summary, ...).
On stop (timeout, max-turns, permission denial, error): report and exit;
do not retry silently and do not exceed scope.
```

Any vendor-specific phrasing — coordinator role boundaries, gateway
formatting, mandatory workflow names — should live in the coordinator's
own instructions, not here.

## Validated vs needs-validation

**Validated for general use** in this skill:

- session identity convention across branch / worktree / tmux / `--name`
- `--continue` cwd-sensitivity; `--resume <id>` for explicit resume;
  `--fork-session` for branching context; `--no-session-persistence`
  for one-shot
- `--permission-mode plan|auto|bypassPermissions` decision tree, with
  `auto` plus tight `--allowedTools` for unattended delegation
- `--tmux` requires `--worktree`; `--tmux=classic` for traditional tmux
- session-scoped vs configured vs persistent agent layering
- effort-level escalation discipline (start `medium`, escalate via fresh
  resume, fail closed on unknown levels)
- `--bare` skips OAuth and `CLAUDE.md` discovery
- MCP-spawning side effects of `claude mcp list/get` and `claude doctor`

**Needs validation** before promoting to a recommended recipe:

- `claude agents` management command behaviour across versions
- `--brief` output shape for orchestration parsing
- `SendUserMessage` semantics in long-running delegated sessions
- stream-json orchestration event shape and stability
- `--permission-mode` edge cases for specific tools / MCP combinations
- `remote-control --spawn=worktree` as a context-preserving dispatch
  mechanism (currently treated as user-facing handoff only)

When using a needs-validation feature, mark it explicitly in the task and
keep the fallback path in scope.

## Working rules

- pick the narrowest permission scope that finishes the task
- pick the lowest effort that finishes the task; escalate via fresh resume
- one stable `<task-slug>` per task across all session-bearing surfaces
- run MCP-spawning commands only in trusted directories
- prefer `--strict-mcp-config` for delegated runs
- never silently take over a delegate's task after it stops
- treat remote-control as a user-facing intervention path, not a backend
- do not paste raw `claude --help` output into project documentation;
  link to it instead

## References

- Claude Code documentation: https://docs.claude.com/en/docs/claude-code
- Dev Container CLI (for hermetic delegation): see `devcontainer-cli`
- Worktree hygiene: see `git-prune-worktrees`
- Lightweight orchestration decisions: see `light-orchestration`
- Handoff prompt rendering: see `handoff-prompt`
