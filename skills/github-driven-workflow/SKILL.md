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

Run the review acquisition script with `<OWNER>/<REPO> <PR_NUMBER>`:

- If `REVIEW_ACQUIRE_SCRIPT` is set, run `"$REVIEW_ACQUIRE_SCRIPT" <OWNER>/<REPO> <PR_NUMBER>`.
- Otherwise, locate `acquire-review.sh` under this skill's installation directory and run it. Common install paths: `.claude/skills/github-driven-workflow/acquire-review.sh`, `.agents/skills/github-driven-workflow/acquire-review.sh`, `.github/skills/github-driven-workflow/acquire-review.sh`. Resolve to a real path (no literal `<skill-dir>` placeholder) before invoking.

A project-specific override must accept the same `<OWNER>/<REPO> <PR_NUMBER>` arguments and exit 0 on success. Exit-code matrices may differ between implementations; **callers should treat any nonzero exit as "review not acquired"** and proceed to authorized bypass per below. Implementations are encouraged but not required to use exit 64 for usage error and exit 127 for missing dependencies.

The bundled default tries Copilot → `@codex` mention → Codex CLI artifact in order and prints `route: <name> (dispatched)` or `route: <name> (evidence)` on success. The token distinguishes whether evidence is already on the PR: `(dispatched)` means only that an async request was sent (Copilot reviewer assigned, `@codex` mention posted) and the §8 evidence gate is **not** yet satisfied; `(evidence)` means a synchronous artifact comment was posted (e.g. Codex CLI) and the §8 gate can match it directly. **Callers must not equate `route: <name>` alone with merge-readiness — only the §8 gate determines that.** For dispatched routes, wait briefly and re-check §8; if evidence does not accrue within a reasonable wait, switch routes or proceed to authorized bypass per below.

Acceptable evidence on the PR:

- A formal GitHub PR review (approved, changes requested, or commented) by a non-author human.
- A Copilot code review result.
- A `@codex` review (independent regardless of who posted the request).
- A Codex CLI review artifact posted as a PR comment, identifying the reviewer and covering the diff.
- An explicit user PR comment clearly framed as a review (concrete findings or approval), even if not posted as a formal GitHub Review event.
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

The gate passes when **any** of the three clauses below is satisfied. They mirror the evidence types §7 accepts; do not filter by `state` or `author.login` (independence is enforced at evidence-recording time per §7).

*Clause 1 — formal Review event.* Copilot, `@codex`, and human GitHub reviews land here.

```sh
gh pr view <N> --json reviews --jq '.reviews | length >= 1'
```

Returning `true` satisfies the gate.

*Clause 2 — `Reviewed-by:` comment artifact.* Codex CLI artifact comments and other reviewer agents recorded per §7.

```sh
gh api repos/<owner>/<repo>/issues/<N>/comments \
  --jq '[.[] | select(.body | test("(?m)^Reviewed-by:\\s*\\S"))] | length >= 1'
```

Returning `true` satisfies the gate. Honor system per §7: the `<entity-id>` after `Reviewed-by:` must be non-empty and distinct from the PR author identity, but its validity is not machine-verified.

*Clause 3 — owner comment-as-review or authorized bypass.* The owner-as-review path requires both an owner-login match and an explicit review verb in the same comment.

```sh
owner=$(gh repo view <owner>/<repo> --json owner --jq .owner.login)
gh api repos/<owner>/<repo>/issues/<N>/comments \
  --jq --arg owner "$owner" '[.[] | select(
    (.user.login == $owner and (.body | test("(?i)\\b(Approved|Reviewed|LGTM|Changes requested)\\b")))
    or (.body | test("^Bypass: independent review waived\\. Authorization: .+\\. Reason: .+\\."))
  )] | length >= 1'
```

Returning `true` satisfies the gate. For org-owned repos, substitute the delegated account per §7 in the owner comparison. An authorized bypass recorded per §7 is matched by the second sub-clause and needs no separate query.

**Do not gate on `reviewDecision`.** It aggregates branch protection rules; without an approving-review rule, it stays empty regardless of review count.

**Do not add gates beyond this set.** `mergeStateStatus`, `reviews[].author.login` filtering, and any check not listed in §7's evidence types are anti-patterns in autonomous environments.

> **Auto Mode note:** Child agents may attempt to add gates "for safety" (commonly `reviewDecision == APPROVED`, author-login filtering, or restricting to clause 1 only). The three-clause set above is authoritative and reflects §7's full evidence vocabulary; additions or restrictions are self-fabrications and should be rejected.

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
