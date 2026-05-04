---
name: github-driven-workflow
description: Issue-first, PR-gated delivery — no direct main pushes, independent review required, deterministic merge gates. Use whenever a task implements a GitHub issue and ships through a PR (assigned by an orchestrator, by project rules, or self-invoked by the implementing agent).
---

# github-driven-workflow

Enforce a fail-closed GitHub delivery workflow: every change traces to an issue, lands on a branch, ships through a PR, and merges only when all gates pass.

## When to use

Whenever a task implements a change from a GitHub issue and delivers it through a PR — invoked by an orchestrator, by project instructions, or by the implementing agent itself. It controls the full lifecycle from issue intake through merge.

Do not invoke for a single sub-step (e.g. "open a PR", "check CI") unless the full workflow context is already established.

## Workflow

### 1. Resolve state

Before writing code:

- Identify the target GitHub issue.
- Confirm the default branch (`main` or equivalent).
- Confirm no uncommitted changes belong to a different issue.

If no issue is identified, stop and request or create one.

### 2. Check issue readiness

Inspect the issue for **scope** and **acceptance criteria**. If either is missing or ambiguous, update the issue or request updates before writing code.

### 3. Branch

- Do not implement on or push to `main`.
- Create `issue-<id>-<slug>` from the default branch and switch to it.

### 4. Implement

Implement the change on the `issue-<id>-<slug>` branch.

### 5. Validate locally

Run repo-appropriate validation. Record commands and output.

### 6. Create a PR

The PR must include:

- `Closes #<issue>` in the body.
- A validation summary with recorded commands and results.
- Markdown task checkboxes (`- [ ]`) only for known remaining work; every unchecked box blocks merge.

### 7. Acquire independent review

Independent review is required in principle. A qualifying review is review evidence produced by an actor other than the implementation author, durably visible on the PR.

Run the review acquisition script:

```sh
"${REVIEW_ACQUIRE_SCRIPT:-<skill-dir>/acquire-review.sh}" <OWNER>/<REPO> <PR_NUMBER>
```

`<skill-dir>` is this skill's installation directory (commonly `.claude/skills/github-driven-workflow/`, `.agents/skills/github-driven-workflow/`, or `.github/skills/github-driven-workflow/`). Set `REVIEW_ACQUIRE_SCRIPT` to override with a project-specific implementation; an override must accept `<OWNER>/<REPO> <PR_NUMBER>` and exit 0 on success.

The bundled default tries Copilot → `@codex` mention → Codex CLI artifact in order and prints `route: <name>` on success. Acceptable evidence on the PR:

- A formal GitHub PR review (approved, changes requested, or commented) by a non-author human.
- A Copilot code review result.
- A `@codex` review (independent regardless of who posted the request).
- A Codex CLI review artifact posted as a PR comment, identifying the reviewer and covering the diff.
- Another reviewer agent recorded with `Reviewed-by: <reviewing-entity-id>` distinct from the implementer. Independence is judged by the recorded identity, not by the GitHub poster.

Self-reviews, local notes, unlinked claims, and generic comments do not qualify. Pick the lowest-friction route available; do not exhaust slow async routes when a faster durable route is already available. Asynchronous routes (Copilot, `@codex`) require waiting; if no response appears within a reasonable wait, switch routes rather than block indefinitely.

#### Authorized bypass

When no review route is viable, record the bypass on the PR with a comment citing the authorization:

```sh
gh pr comment <N> --body 'Bypass: independent review waived. Authorization: <provenance>. Reason: <reason>.'
```

Accepted provenance:

- **Orchestrator-conveyed user instruction** — cite the instruction (e.g. "user instructed orchestrator to run github-driven-workflow with bypass allowed"). No per-PR owner comment required.
- **Repo-owner PR comment** — verify the commenter login matches the repo owner:
  ```sh
  owner=$(gh repo view <owner>/<repo> --json owner --jq .owner.login)
  test "<commenter-login>" = "$owner"
  ```
  For org-owned repos (where `owner` is the org login matching no human account), the comment must come from an account the org owner has explicitly delegated, citing that delegation; verification compares the commenter against the delegated login. Generic admin permission alone is not sufficient.

Record the cited provenance (and verified `<commenter-login>` on the owner path) alongside the bypass evidence in §8.

### 8. Check merge gates

Run all checks before merging.

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

Empty array ⇒ pass. Any non-`SUCCESS` state, or command error ⇒ stop.

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

Count nodes where `isResolved` is `false`. Must be zero. Paginate with `after: "<endCursor>"` while `hasNextPage` is `true`. Query error ⇒ stop.

**Unchecked task boxes**

```sh
gh pr view <N> --json body --jq '.body | test("- \\[ \\]|\\* \\[ \\]")'
```

Must return `false`.

**Independent review evidence or authorized bypass**

```sh
gh pr view <N> --json reviews --jq '.reviews | length >= 1'
```

Must return `true`. Do not filter by `state` or `author.login` here; independence is enforced at evidence-recording time (§7). An authorized bypass recorded per §7 satisfies this gate in lieu of review evidence.

**Do not gate on `reviewDecision`.** It aggregates branch protection rules; without an approving-review rule, it stays empty regardless of review count.

**Do not add gates beyond this set.** `mergeStateStatus` and `reviews[].author.login` filtering are anti-patterns in autonomous environments.

> **Auto Mode note:** Child agents may attempt to add gates "for safety" (commonly `reviewDecision == APPROVED` or author-login filtering). The set above is authoritative; additions are self-fabrications and should be rejected.

Cite the evidence (review count, comment URL, or bypass comment URL plus cited provenance) in the merge note.

### 9. Merge

Merge only when every gate passes. If any gate fails, fix, revalidate, or leave the PR open with a comment stating the exact blocking condition.

## Fail-closed behavior

Stop before implementation or merge when any required state cannot be verified.

Stop conditions:

- Issue missing or ambiguous, or missing Scope/Acceptance.
- Current branch is `main`, or PR is missing or draft.
- PR lacks `Closes #<issue>`.
- Independent review evidence missing and no authorized bypass recorded.
- CI not `SUCCESS`, pending, or command errored.
- Unresolved review thread count nonzero or query errored.
- PR body has unchecked task boxes.
- PR has a blocking label.

When stopped, state the exact blocking condition and the action needed to unblock.

## Scope

Procedural guidance only. Does not configure GitHub branch protection, CI workflows, or repository permissions.
