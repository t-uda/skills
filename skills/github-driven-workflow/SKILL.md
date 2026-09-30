---
name: github-driven-workflow
description: Deliver an authorised GitHub issue through a branch, validation, independent review and a gated PR merge. Use for implementation or resuming its review-and-merge cycle, including after reviewer or owner feedback. Distinguish review evidence from resolved findings and current merge authority; continue autonomously within the existing delegation. Do not push directly to the default branch or invent extra approval waits.
---

# github-driven-workflow

Enforce a fail-closed GitHub delivery workflow: every change traces to an issue, lands on a branch, ships through a PR, and merges only when all gates pass.

## When to use

Whenever a task implements a change from a GitHub issue and delivers it through a PR — invoked by an orchestrator, by project instructions, or by the implementing agent itself. It controls the full lifecycle from issue intake through merge, including resuming the review-and-merge cycle of an existing PR after reviewer or owner feedback.

A resumed sub-step keeps the full-lifecycle context. Do not rerun implementation merely because a user asks to inspect an existing PR's reviews.

## Workflow

### 1. Resolve state

Before writing code:

- Identify the target GitHub issue.
- Confirm the default branch (`main` or equivalent).
- Confirm no uncommitted changes belong to a different issue.

If no issue is identified, stop and request or create one.

### 2. Check issue readiness

Before implementation, read the issue body and relevant decision comments. Apply authorised amendments to the agreed scope; distinguish settled decisions from proposals. A dispatch summary does not replace that context.

Do this at initial intake and again when resuming after material scope changes. The newest comment is not automatically authoritative: distinguish an authorised decision from a suggestion, quoted material or an unresolved discussion. A settled decision takes effect whether or not it has been consolidated into the body. Give any reviewer the same governing specification.

Inspect the resulting specification for **scope** and **acceptance criteria**. If either is missing or ambiguous, update the issue or request updates before writing code.

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

Within existing authority, act on review feedback and continue through validation, independent review and merge without seeking fresh owner approval unless the governing instructions or repository rules require it. Read current review bodies, comments and threads; review presence alone does not establish that findings are addressed. Owner participation or a change request does not by itself create an owner checkpoint. Respect actual holds and unresolved owner-only decisions, pausing only dependent actions; do not invent a wait from silence or possible further feedback.

Independent review is required in principle. A qualifying review is review evidence produced by an actor other than the implementation author, durably visible on the PR.

A review request being dispatched, a review being returned, and its findings being addressed are different states. Reuse qualifying review evidence only for the scope it actually covers; after relevant changes, obtain the required review of the changed content rather than repeatedly dispatching an unrelated generic reviewer. A negative review can establish that review occurred, but cannot by its existence establish merge-readiness.

Before dispatching a reviewer, check whether existing evidence already qualifies under the evidence types below for the current change — including a scoped review obtained by a governing outer workflow. If it does, skip acquisition and proceed to §8.

If no qualifying evidence exists, run the bundled acquisition script. Resolve this path from the `github-driven-workflow` skill root, not from the target repository root:

```sh
scripts/acquire-review.py <OWNER>/<REPO> <PR_NUMBER> [kind]
```

In this source repository the same helper lives at `skills/github-driven-workflow/scripts/acquire-review.py`; in an installed skill it remains `scripts/acquire-review.py` relative to the installed skill directory.

Treat any nonzero exit as "review not acquired" and proceed to authorized bypass per below. Project-level customization of acquisition logic is documented in the skill's `README.md`.

The bundled default is reviewer-neutral: it picks `copilot` or `codex` uniformly at random (or honors an explicit `[kind]` third argument) and dispatches a single asynchronous review request, printing `route: <kind> (dispatched)` on success. The bundled script does not prefer any specific automatic reviewer; projects that want a different selection policy supply one via the `REVIEW_ACQUIRE_SCRIPT` override (see the skill's `README.md`). `(dispatched)` means only that an async request was sent; it is not review evidence. Wait briefly and re-check; if evidence does not accrue within a reasonable wait, dispatch a different kind or proceed to authorized bypass per below. Override implementations may also emit `(evidence)` when their route posts a durable artifact at dispatch time.

Acceptable evidence on the PR:

- A formal GitHub PR review (approved, changes requested, or commented) by a non-author human.
- A Copilot code review result.
- A `@codex` review (independent regardless of who posted the request) — typically a formal Review event, occasionally a top-level comment that the agent recognizes as a review.
- A Codex CLI review artifact posted as a PR comment, identifying the reviewer and covering the diff.
- An explicit user PR comment clearly framed as a review (concrete findings or approval), even if not posted as a formal GitHub Review event.
- Another reviewer agent recorded with `Reviewed-by: <reviewing-entity-id>` distinct from the implementer. Independence is judged by the recorded identity, not by the GitHub poster.

Self-reviews, local notes, unlinked claims, generic activity comments, pending draft reviews and unsupported markers do not qualify. Formal Review events and valid comment-based reviews carry equal weight. Pick the lowest-friction route available; do not exhaust slow async routes when a faster durable route is already available. Asynchronous routes (Copilot, `@codex`) require waiting; if no response appears within a reasonable wait, switch routes rather than block indefinitely.

#### Dispose of feedback

Make the disposition of feedback requiring action traceable on the PR through replies, linked fixes or a concise grouped response. Explain any non-action that affects acceptance; do not create a separate ledger or repeat evidence already available there. Do not waive an unmet owner requirement outside the existing delegation. Already satisfied or superseded feedback does not require renewed owner approval merely to record its disposition.

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

Record the cited provenance (and verified `<commenter-login>` on the owner path) alongside the bypass evidence in §8. A bypass waives only the acquisition requirement; it does not dispose of actual findings or grant additional merge authority.

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

**Review evidence, disposition and authority**

Before merge, read the current formal review submissions, review bodies, ordinary PR comments and inline threads, including their author or recorded reviewer, reviewed revision and subsequent disposition. Retrieve all needed pages; do not prefilter in a way that hides another reviewer, COMMENTED reviews or comment-based evidence.

```sh
# Current head, to compare with each review's commit_id or the SHA a comment-based review names
gh pr view <N> --json headRefOid --jq .headRefOid

# Formal Review events of every state, with reviewed revision
gh api --paginate repos/<owner>/<repo>/pulls/<N>/reviews \
  --jq '.[] | {user: .user.login, state, commit_id, submitted_at, html_url, body}'

# Ordinary PR comments: `Reviewed-by:` artifacts, @codex replies, owner reviews, bypass records
gh api --paginate repos/<owner>/<repo>/issues/<N>/comments \
  --jq '.[] | {user: .user.login, created_at, html_url, body}'

# Inline review-thread comments, including replies and those in resolved threads
gh api --paginate repos/<owner>/<repo>/pulls/<N>/comments \
  --jq '.[] | {user: .user.login, path, line, commit_id, in_reply_to_id, html_url, body}'
```

Record the reviewed SHA with comment-based evidence. Commit timestamps do not show when a commit was pushed, so a comment-based review that names no SHA cannot establish coverage of a head that may have changed; obtain review of the current head instead.

These queries locate evidence candidates; neither a review count nor a keyword match is a sufficient merge predicate. A pending draft, generic activity comment or unsupported marker is not completed review evidence, and a review-shaped comment containing `Changes requested` is not approval.

Evaluate separately:

1. Qualifying independent evidence under §7 covers the relevant final change, or an authorised acquisition bypass is recorded.
2. Blocking findings have been fixed and verified, or disposed of within the applicable authority. Do not infer this from review count or zero unresolved inline threads. Non-blocking suggestions do not automatically create a new approval round.
3. Merge remains within the existing delegation and satisfies the actual repository and task requirements.

An ordinary addressed change request proceeds through the applicable review and merge gates without a new owner verdict unless one is required. Do not turn a historical negative review into a permanent veto after its findings and applicable requirements are resolved. Conversely, a different reviewer's clean result does not erase unresolved findings or a specifically reserved decision.

For item 3, interpret existing authority rather than adding an owner gate:

- **No prior reservation** — the gates and delegation permit merge; proceed. Do not invent a preventive wait for an owner preference that has not been communicated.
- **Existing reservation** — the governing brief already requires owner approval. An owner correction, commit or report is not that approval; the reservation holds until an authorised amendment removes or satisfies it. A clear natural-language reservation counts without a keyword; owner activity alone creates none.

Do not require `reviewDecision == APPROVED` in every repository, and do not use an absent optional approval signal as a new blocker. Honour real repository requirements; do not dismiss a review or bypass protections merely to make a gate pass. GitHub poster identity alone does not establish whether the recorded reviewing entity is independent.

Apply this workflow and the actual governing requirements; do not invent extra reviewer identities, approval counts, cooldowns or owner checkpoints. When a real blocking condition exists, state it and continue all authorised work that does not depend on it.

Cite the evidence (review or comment URLs, or bypass comment URL plus cited provenance) and the disposition of blocking findings in the merge note.

### 9. Merge

Before executing the merge, refresh the relevant GitHub state, including `headRefOid`. If the head or a material intervention changed since evaluation, reevaluate the affected checks; do not rely on a cached merge-ready summary after new feedback. Merge only when every gate passes. If any gate fails, fix, revalidate, or leave the PR open with a comment stating the exact blocking condition. Keep evidence links in the normal PR trail rather than in a status document.

## Fail-closed behavior

Stop before implementation or merge when any required state cannot be verified.

Stop conditions:

- Issue missing or ambiguous, or missing Scope/Acceptance after reading its decision comments.
- Current branch is `main`, or PR is missing or draft.
- PR lacks `Closes #<issue>`.
- **Review missing** — no qualifying evidence covers the relevant final change and no authorized bypass is recorded. Acquire review or switch routes.
- **Blocking feedback unresolved** — fix, verify and record its disposition, then obtain review of the changed content as §7 requires.
- **Actual required decision outstanding** — a decision reserved by the governing context is unmet. This is the only owner-wait case; pause the dependent action and continue independent work.
- CI not `SUCCESS`, pending, or command errored.
- Unresolved review thread count nonzero or query errored.
- PR body has unchecked task boxes.
- PR has a blocking label.

When stopped, state the exact blocking condition and the action needed to unblock.

## Scope

Procedural guidance only. Does not configure GitHub branch protection, CI workflows, or repository permissions.
