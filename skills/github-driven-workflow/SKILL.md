---
name: github-driven-workflow
description: Enforce issue-first, PR-gated delivery with no direct main pushes, independent review requirement, and deterministic merge gates. Use when assigned by an orchestrator to govern the full delivery lifecycle for a GitHub issue, when enforcing PR-gated delivery, when requiring independent review, or when checking merge readiness.
---

# github-driven-workflow

Enforce a fail-closed GitHub delivery workflow: every change traces to an issue, lands on a branch, ships through a PR, and merges only when all gates pass.

This skill governs the entire delivery lifecycle. It is assigned by an orchestrator or project rules to bind the implementing agent to this workflow for the duration of a task.

## When to use

Use this skill when an orchestrator or project instructions assign it to govern a delivery task. It controls the full lifecycle from issue intake through merge.

Assign this skill for tasks that involve:

- implementing a change from a GitHub issue (issue-first delivery)
- delivering work through a PR (PR-gated delivery)
- requiring independent review before merge
- checking or enforcing merge gate readiness

Do not invoke this skill for a single sub-step (e.g. "open a PR" or "check CI") unless the full workflow context is already established and the orchestrator has scoped the invocation explicitly.

## Workflow

### 1. Resolve state

Before writing any code:

- Identify the target GitHub issue.
- Confirm the default branch (`main` or equivalent).
- Confirm no uncommitted changes that belong to a different issue.

If no issue is identified, stop. Request or create one before continuing.

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

Independent review is required in principle. A qualifying review is review evidence produced by an actor other than the implementation author, made durably visible on the PR. Acceptable routes:

- A formal GitHub PR review (approved, changes requested, or commented) by a non-author human.
- A Copilot code review result visible on the PR.
- A GitHub `@codex` review on the PR, regardless of who posted the request.
- A Codex CLI review artifact posted as a PR comment, with the review output included verbatim and the reviewer identity stated.
- Another review-capable agent (subagent, reviewer bot) when its review summary and reviewer identity are recorded on the PR.
- An explicit user review on the PR (a formal review, or a comment clearly framed as a review with concrete findings or approval).

If no review route is viable, this gate may be bypassed when authorization is recorded on the PR. Authorization may be either an orchestrator-conveyed user instruction (cited by the implementing agent) or a comment from a verified repo-owner account. See "Authorized bypass" below.

Self-reviews, local notes, and unlinked claims do not qualify. Generic PR comments unrelated to review do not qualify.

Pick the lowest-friction route available. Do not exhaust slow asynchronous routes when a faster durable route (e.g. Codex CLI artifact, authorized bypass) is already available.

#### Requesting Copilot review

Copilot code review requires the `copilot-pull-request-reviewer` GitHub App to be installed on the repository. Assign Copilot as a reviewer using the REST API with a JSON body:

```sh
gh api repos/<owner>/<repo>/pulls/<N>/requested_reviewers \
  -X POST --input - <<'EOF'
{"reviewers": ["copilot-pull-request-reviewer[bot]"]}
EOF
```

- HTTP 200 with `requested_reviewers` containing `"login": "Copilot"` → reviewer added successfully.
- HTTP 422 ("not a collaborator") → the Copilot app is not installed on this repository. Use a different qualifying route.

Do not use `-f 'reviewers[]=Copilot'` or `gh pr edit --add-reviewer Copilot`; both silently fail or produce a GraphQL error.

Verify assignment:
```sh
gh pr view <N> --json reviewRequests \
  --jq '[.reviewRequests[].requestedReviewer.login]'
```
Should include `"Copilot"`.

Verify completion: poll `gh pr view <N> --json reviews` until a review entry with `author.login` of `copilot-pull-request-reviewer[bot]` appears.

#### Requesting @codex review

Post a mention comment to request a @codex review:

```sh
gh api repos/<owner>/<repo>/issues/<N>/comments \
  -X POST -f body='@codex please review this PR'
```

The comment always posts successfully. Verify that Codex received the notification:
```sh
gh api repos/<owner>/<repo>/issues/<N>/timeline \
  --jq '[.[] | select(.event == "mentioned") | .actor.login]'
```
Should include `"codex"`.

Verify completion by polling comments until a response from the Codex bot appears:
```sh
gh api repos/<owner>/<repo>/issues/<N>/comments \
  --jq '[.[] | select(.user.login | ascii_downcase | contains("codex")) | {author: .user.login, body: .body[:120]}]'
```

If no Codex response appears after a reasonable wait, the Codex app may not be active on this repository. Use a different qualifying route.

A @codex review counts as independent even when Codex opened the PR; the review agent invoked by mention runs in a separate context.

#### Codex CLI review artifact

When GitHub-side review routes are unavailable or impractical, run a local Codex CLI review and post the verbatim output as a PR comment so the artifact is durable:

```sh
codex exec "Review PR #<N> in this repo. Inspect the diff and report concrete findings." > /tmp/codex-review.md
gh pr comment <N> --body-file /tmp/codex-review.md
```

The comment must identify the reviewer ("Codex CLI review") and cover the actual diff.

#### Authorized bypass

When no review route is viable, the agent records the bypass on the PR with a comment citing the authorization:

```sh
gh pr comment <N> --body 'Bypass: independent review waived. Authorization: <provenance>. Reason: <reason>.'
```

Accepted authorization provenance:

- **Orchestrator-conveyed user instruction.** The user has instructed the coding agent or orchestrator to run this workflow with bypass allowed. The bypass comment cites that instruction (e.g. "user instructed orchestrator to run github-driven-workflow with bypass allowed"). No per-PR comment from the repo owner is required on this path.
- **Repo-owner PR comment.** The repo owner posts the bypass comment directly. Verify the commenter login matches the owner:
  ```sh
  owner=$(gh repo view <owner>/<repo> --json owner --jq .owner.login)
  test "<commenter-login>" = "$owner"
  ```
  For org-owned repos (where the `owner` field is the org login and matches no human account), the comment must come from an account the org owner has explicitly delegated and must cite that delegation; verification compares the commenter against the delegated login, not the org slug. Generic admin permission alone is not sufficient on this path.

Record the cited provenance (and, on the repo-owner path, the verified `<commenter-login>`) alongside the bypass evidence in step 8.

#### Waiting for review

Copilot, `@codex`, and other agent reviews are asynchronous. After requesting:

1. Stop and wait. Do not attempt to merge.
2. Re-check the relevant endpoint periodically.
3. If no response appears within a reasonable wait, switch to a different qualifying route (e.g. Codex CLI artifact, manual user review, or owner bypass) rather than blocking indefinitely.

### 8. Check merge gates

Run all checks before merging. Each check uses a concrete command.

**PR state**

```sh
gh pr view <N> --json state,isDraft \
  --jq '{open: (.state == "OPEN"), notDraft: (.isDraft == false)}'
```

Both must be `true`.

**CI checks**

```sh
gh pr view <N> --json statusCheckRollup \
  --jq '.statusCheckRollup | map({name, state})'
```

- If the array is empty, no checks are configured; this gate passes.
- If any check has `state` other than `SUCCESS`, stop.
- If the command errors, stop.

**Labels**

```sh
gh pr view <N> --json labels \
  --jq '[.labels[].name] | any(. == "blocked" or . == "do-not-merge" or . == "needs-decision")'
```

Must return `false`.

**Unresolved review threads**

```sh
gh api graphql -f query='
{
  repository(owner: "<owner>", name: "<repo>") {
    pullRequest(number: <N>) {
      reviewThreads(first: 100) {
        nodes { isResolved }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
}'
```

Count nodes where `isResolved` is `false`. Must be zero. If `pageInfo.hasNextPage` is `true`, repeat with `after: "<endCursor>"` until all pages are checked. If the query errors, stop.

**Unchecked task boxes**

```sh
gh pr view <N> --json body \
  --jq '.body | test("- \\[ \\]|\\* \\[ \\]")'
```

Must return `false`.

**Independent review evidence**

At least one of the following must be present and durably visible on the PR:

- A formal review by a reviewer who is not an implementation author. Implementation authors are the commit authors on the PR (which may differ from the PR opener in split-author flows). The check fails closed when any commit author has no linked GitHub login, because then `$impls` would silently miss a self-review:
  ```sh
  gh pr view <N> --json reviews,commits \
    --jq '
      [.commits[].authors[].login] as $impls
      | if any($impls[]; . == null or . == "")
        then error("commit author missing GitHub login; record implementation author logins manually before trusting this gate")
        else [.reviews[]
              | select(.state == "APPROVED" or .state == "CHANGES_REQUESTED" or .state == "COMMENTED")
              | select(.author.login as $r | $impls | index($r) == null)] | length > 0
        end
    '
  ```
  Dismissed and pending review submissions are excluded so that a stale dismissed review cannot satisfy the gate.
- A review artifact comment (Codex CLI output, agent review summary, or other reviewer-identified review) on the PR. This route is trust-based: a comment posted by the implementation actor cannot be cryptographically attributed to the cited agent, so it is auditable rather than tamper-evident. Prefer formal non-author GitHub reviews when integrity matters more than friction.
- An authorized bypass comment on the PR per step 7. The comment must cite the authorization provenance — either an orchestrator-conveyed user instruction, or a verified repo-owner (or org-delegated) account.

Cite the evidence (review id, comment URL, or bypass comment URL plus the cited provenance) in the merge note.

### 9. Merge

Merge only when every gate passes. If any gate fails, fix, revalidate, or leave the PR open with a PR comment stating the exact blocking condition.

## Fail-closed behavior

Stop before implementation or merge when any required state cannot be verified.

Stop conditions:

- Issue is missing or ambiguous.
- Issue Scope or Acceptance is missing.
- Current branch is `main`.
- PR is missing.
- PR lacks `Closes #<issue>`.
- Independent review evidence is missing and no authorized bypass is recorded on the PR.
- CI check state is not `SUCCESS`, is pending, or the command errored.
- Unresolved review thread count is nonzero or the query errored.
- PR body has unchecked task boxes.
- PR has a blocking label.
- PR is draft.

When stopped, state the exact condition that blocked progress and the action needed to unblock it.

## Scope

This skill provides procedural guidance only. It does not configure GitHub branch protection rules, CI workflows, or repository permissions.
