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

### 5a. Place evidence

Keep validation commands and results in the PR as required below. Do not create or expand repository files solely to record progress, completion, validation, review evidence, freshness timestamps, or GitHub queue state.

Keep durable repository content focused on the current system, its contracts, constraints, and reader-relevant rationale. Omit historical text when Git or the Issue/PR trail already answers the question and the text adds no current meaning. Preserve repository-required changelogs, ADRs, audit or migration records, and Issue/PR references that define current authority, unresolved boundaries, or compatibility constraints.

### 6. Create a PR

The PR must include:

- `Closes #<issue>` in the body.
- A validation summary with recorded commands and results.
- Markdown task checkboxes (`- [ ]`) only for known remaining work; every unchecked box blocks merge.

### 7. Acquire independent review

Independent review is required in principle. A qualifying review is review evidence produced by an actor other than the implementation author, durably visible on the PR.

Before dispatching a reviewer, check the §8 evidence clauses and confirm that any existing artifact qualifies under the evidence types below. If qualifying evidence already exists — including a scoped review obtained by a governing outer workflow — skip acquisition and proceed to §8.

If no qualifying evidence exists, run the bundled acquisition script. Resolve this path from the `github-driven-workflow` skill root, not from the target repository root:

```sh
scripts/acquire-review.py <OWNER>/<REPO> <PR_NUMBER> [kind]
```

In this source repository the same helper lives at `skills/github-driven-workflow/scripts/acquire-review.py`; in an installed skill it remains `scripts/acquire-review.py` relative to the installed skill directory.

Treat any nonzero exit as "review not acquired" and proceed to authorized bypass per below. Project-level customization of acquisition logic is documented in the skill's `README.md`.

The bundled default is reviewer-neutral: it picks `copilot` or `codex` uniformly at random (or honors an explicit `[kind]` third argument) and dispatches a single asynchronous review request, printing `route: <kind> (dispatched)` on success. The bundled script does not prefer any specific automatic reviewer; projects that want a different selection policy supply one via the `REVIEW_ACQUIRE_SCRIPT` override (see the skill's `README.md`). `(dispatched)` means only that an async request was sent — the §8 evidence gate is **not** yet satisfied. **Callers must not equate `route: <name>` alone with merge-readiness — only the §8 gate determines that.** Wait briefly and re-check §8; if evidence does not accrue within a reasonable wait, dispatch a different kind or proceed to authorized bypass per below. Override implementations may also emit `(evidence)` when their route posts a durable artifact at dispatch time.

Acceptable evidence on the PR:

- A formal GitHub PR review (approved, changes requested, or commented) by a non-author human.
- A Copilot code review result.
- A `@codex` review (independent regardless of who posted the request) — typically a formal Review event, occasionally a top-level comment that the agent recognizes as a review.
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

*Clause 1 — formal Review event.* Any formal GitHub PR Review event satisfies this clause regardless of the reviewer's identity (humans, Copilot, Codex, or other reviewer accounts that produce formal reviews). Reviewer agents that respond as a normal comment rather than a formal Review event are matched by Clause 2 (`Reviewed-by:` marker) or, when owner-authored with a review verb, by Clause 3.

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
