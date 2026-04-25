---
name: github-driven-workflow
description: Enforce issue-first, PR-gated delivery with no direct main pushes, independent review requirement, and deterministic merge gates. Use when implementing from a GitHub issue, creating or merging a PR, protecting main from direct pushes, requiring independent review, or checking merge readiness.
---

# github-driven-workflow

Enforce a fail-closed GitHub delivery workflow: every change traces to an issue, lands on a branch, ships through a PR, and merges only when all gates pass.

## When to use

Use this skill when:

- the user asks to implement something from a GitHub issue
- the user asks to open, update, or merge a PR
- the user asks to protect `main` from direct pushes
- the user asks to enforce issue-first or PR-driven delivery
- the user asks to require independent review before merge
- the user asks to check or enforce merge gate readiness

## Workflow

### 1. Resolve state

Before writing any code:

- Identify the target GitHub issue.
- Confirm the default branch (`main` or equivalent).
- Confirm no uncommitted changes that belong to a different issue.

If no issue is identified, stop. Request or create one according to the user's available permissions before continuing.

### 2. Check issue readiness

Inspect the issue for:

- **Scope**: what is in scope and what is not.
- **Acceptance criteria**: conditions under which the issue is complete.

If either is missing or ambiguous, update the issue or request updates before writing any code.

### 3. Branch

- Do not implement on `main`.
- Do not push directly to `main`.
- Create a branch named `issue-<id>-<slug>` from the current default branch.
- Switch to that branch before making any changes.

### 4. Implement

Implement the change on the `issue-<id>-<slug>` branch.

### 5. Validate locally

Run the validation commands appropriate to this repository. Record the commands and their output.

### 6. Create a PR

The PR must include:

- `Closes #<issue>` in the body.
- A validation summary with recorded commands and results.
- Markdown task checkboxes (`- [ ]`) only for known remaining work; every unchecked box blocks merge.

### 7. Acquire independent review

A qualifying independent review is one of:

- A GitHub PR review or PR comment by an actor other than the implementation author.
- A Copilot reviewer result visible on the PR.
- A `@codex` review or comment visible on the PR.
- A subagent review only when the environment explicitly supports subagents and the PR body contains the subagent review summary and identity.

If no qualifying route is available, stop and request an external reviewer. Do not treat self-review, local notes, or an unlinked claim as qualifying evidence.

### 8. Check merge gates

All of the following must pass before merge:

- PR is open and not draft.
- All GitHub-reported required checks are success.
- If no required checks are reported, all present checks must be success.
- If CI status cannot be read, stop.
- GitHub unresolved review thread count is zero.
- If review thread state cannot be read, stop.
- PR body has no unchecked Markdown task boxes (`- [ ]` or `* [ ]`).
- PR has no `blocked`, `do-not-merge`, or `needs-decision` label.
- Qualifying independent review evidence exists.

### 9. Merge

Merge only when every gate passes. If any gate fails, fix, revalidate, or leave the PR open with a clear blocking reason stated in a PR comment.

## Fail-closed behavior

Stop before implementation or merge when any required state cannot be verified.

Stop conditions:

- Issue is missing or ambiguous.
- Issue Scope or Acceptance is missing.
- Implementation branch is missing or the current branch is `main`.
- PR is missing.
- PR lacks `Closes #<issue>`.
- Independent review evidence is missing.
- CI is failing, pending, or unreadable.
- Unresolved review thread count is nonzero or unreadable.
- PR body has unchecked TODO checkboxes.
- PR has a blocking label.
- PR is draft.

When stopped, state the exact condition that blocked progress and the action needed to unblock it.

## Scope

This skill provides procedural guidance only. It does not configure GitHub branch protection rules, CI workflows, or repository permissions.
