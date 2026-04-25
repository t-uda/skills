---
name: github-driven-workflow
description: Enforce issue-first, PR-gated delivery with no direct main pushes, independent review requirement, and deterministic merge gates. Use when assigned by an orchestrator to govern the full delivery lifecycle for a GitHub issue, when enforcing PR-gated delivery, when requiring independent review, or when checking merge readiness.
---

# github-driven-workflow

Enforce a fail-closed GitHub delivery workflow: every change traces to an issue, lands on a branch, ships through a PR, and merges only when all gates pass.

This skill governs the entire delivery lifecycle. It is assigned by an orchestrator or project rules to bind the implementing agent to this workflow for the duration of a task.

## When to use

Use this skill when an orchestrator or project instructions assign it to govern a delivery task. It controls the full lifecycle from issue intake through merge.

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

A qualifying independent review is one of:

- A GitHub PR review or PR comment by a human actor other than the implementation author.
- A Copilot code review result visible on the PR.
- A `@codex` review comment visible on the PR.
- A subagent review only when the environment explicitly supports subagents and the PR body contains the subagent review summary and identity.

Do not treat self-review, local notes, or an unlinked claim as qualifying.

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

#### Waiting for review

Both Copilot and @codex reviews are asynchronous. After requesting:

1. Stop and wait. Do not attempt to merge.
2. Re-check the relevant endpoint periodically.
3. If no response appears, state the blocking condition and ask for an alternative reviewer.

If no qualifying route is available, stop and request a human reviewer via `gh pr edit <N> --add-reviewer <login>`.

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
      reviewThreads(first: 50) {
        nodes { isResolved }
      }
    }
  }
}'
```

Count nodes where `isResolved` is `false`. Must be zero. If the query errors, stop.

**Unchecked task boxes**

```sh
gh pr view <N> --json body \
  --jq '.body | test("- \\[ \\]|\\* \\[ \\]")'
```

Must return `false`.

**Independent review evidence**

```sh
gh pr view <N> --json reviews \
  --jq '[.reviews[] | {author: .author.login, state: .state}]'
```

At least one qualifying review must be present. Self-reviews (same login as the implementation author) do not qualify.

### 9. Merge

Merge only when every gate passes. If any gate fails, fix, revalidate, or leave the PR open with a PR comment stating the exact blocking condition.

## Fail-closed behavior

Stop before implementation or merge when any required state cannot be verified.

Stop conditions:

- Issue is missing or ambiguous.
- Issue Scope or Acceptance is missing.
- Current branch is `main` and no implementation branch exists.
- PR is missing.
- PR lacks `Closes #<issue>`.
- Independent review evidence is missing.
- CI check state is not `SUCCESS`, is pending, or the command errored.
- Unresolved review thread count is nonzero or the query errored.
- PR body has unchecked task boxes.
- PR has a blocking label.
- PR is draft.

When stopped, state the exact condition that blocked progress and the action needed to unblock it.

## Scope

This skill provides procedural guidance only. It does not configure GitHub branch protection rules, CI workflows, or repository permissions.
