---
name: handoff-prompt
description: Generate a compact handoff prompt for the next agent or stage. Output the prompt only.
---

# Handoff Prompt

Generate a **minimal sufficient prompt** for the next agent — one that lets it start the correct work immediately, with no needless background, duplicated documentation, user-side clarification, or avoidable rework.

This is a **handoff / stage-transition** skill, not a summarisation skill.

## Use this skill when

The user wants to pass work to another agent, role, or stage: continuing in a fresh coding-agent context, handing a completed plan/spec to an orchestrator, passing research results to an implementer, passing implementation state to a reviewer or debugger, or splitting work across agents.

## Invariants

Every handoff prompt must satisfy all five. The rest of this skill exists to *apply* them — no other section restates them:

1. **Minimal** — transfer only what the next agent needs to act correctly and efficiently; omit everything else.
2. **No duplication** — never restate content already in `AGENTS.md`, specs, plans, architecture docs, or workflow instructions; point to the source instead.
3. **No history** — no narrative, abandoned detours, motivation, or general background that would not change the next action.
4. **Compact** — target under ~1000 characters. Growth is a signal to compress harder, not to add structure.
5. **Autonomously executable** — the next agent must act without asking the user for avoidable clarification, stalling on ambiguity, reopening settled decisions, or causing avoidable rework.

## Core rule

Prioritise, in this order: (1) the immediate task, (2) correct starting references, (3) decisions already fixed, (4) non-obvious constraints or context, (5) unresolved points that materially affect the next step, (6) the required output.

For (4), include only context the next agent is unlikely to recover reliably on its own: decisions already made, options explicitly rejected, hidden constraints, priority ordering not evident from the files, known traps or misleading artefacts.

## Required output structure

Output **only** the prompt — no preface, explanation, or follow-up text. Every prompt must contain:

1. **Skill anchor** — at least one `/skill-name` reference (e.g. `/github-driven-workflow`, `/lite-spec`) **when an applicable installed skill governs the next agent's execution**. If no installed skill applies to the handoff, do not invent or force one — omit the anchor rather than reference an irrelevant skill.
2. **Concrete anchor** — at least one of: issue/PR number (`#N`), commit SHA, file path, session log path.
3. **Bounded length** — see Invariant 4.

Once these are present, decision boundaries are deferred to whatever the anchors point to (the governing skill, or, absent one, the referenced document/issue). Verbal acceptance phrasing — `merge after CI is green`, `proceed when ready`, `完了したら次へ` — is not prohibited: it reads naturally, and the anchors keep the next agent from being trapped in an unresolvable gate.

### Hard-fail anti-patterns (exhaustive)

Reject only these well-defined structural violations:

- **Self-authorization preamble** — e.g. `explicit authorization granted`, `you are authorized to ...`. Permission grants belong in environment configuration, not the prompt body.
- **Permission-downgrade directive** — instructing the next agent to pass `--dangerously-skip-permissions` or an equivalent flag.

Do not enumerate verbal acceptance phrases (`complete when`, `after review`, `once green`) as forbidden — the expression space is unbounded, any such list is trivially bypassed by rephrasing, and it causes false positives on legitimate usage (e.g. `implement #42 following /github-driven-workflow until complete` is fine; the anchored skill defines the actual gates).

## Role-specific emphasis

Pick the row matching the next agent; use only elements the immediate task doesn't already make obvious.

| Target role | Emphasise |
|---|---|
| Coding agent | the concrete implementation task; files/docs to read first; fixed design decisions; constraints; expected code/test/doc outputs |
| Orchestrator | the task to coordinate and its complexity; required sub-agent decomposition; the model tier suited to each sub-agent's complexity; decisions already fixed; the final deliverable/coordination objective |
| Reviewer / debugger | the review or debug target; intended behaviour; likely failure points; areas needing scrutiny; required review output |
| Research agent | the concrete research question; scope boundaries; fixed assumptions; the form findings must take; what's explicitly out of scope |

## Boundaries

This skill only renders the final transfer prompt. It does not decide *what* to do next:

- Need to review whether a plan is ready for autonomous implementation? Use `/metaplan` first.
- Need a full execution brief for a bounded implementation task? Use `/lite-spec` first.
- Deciding whether to split work across multiple agents at all? Use `/light-orchestration` first.

Invoke this skill last, to produce the transfer text once those upstream decisions are already fixed.

## Examples

```
# Good — skill anchor + concrete anchor + bounded length
Implement t-uda/example#42 following /github-driven-workflow.
Report when complete.

# Bad — no skill anchor, criteria leaking into prompt body
Implement the example issue. Wait until CI is green and review is sufficient,
then merge with squash, delete the branch, clean up the worktree, report ...
(800+ characters)

# Bad → Good — verbal "until complete" is fine when structure is right
Implement t-uda/example#42 following /github-driven-workflow until complete.
Report to channel ABC.
```

### Validation cases

```
# A — an applicable governing skill exists: anchor it
Implement t-uda/example#42 following /github-driven-workflow.
Do not reopen the API shape — fixed: REST, not GraphQL.
Report when merged.

# B — no applicable skill exists: no anchor is forced
Fix the flaky test at tests/test_retry.py::test_backoff (t-uda/example#57).
Root cause is suspected in the jitter calculation, not the retry count.
Report the fix and root cause.

# C — the referenced document already has all acceptance criteria: reference, don't restate
Implement the design in docs/plans/auth-redesign.md (t-uda/example#88) following /lite-spec.
Acceptance criteria are fully specified there.

# D — a non-obvious constraint must carry over
Continue the migration in t-uda/example#101 following /github-driven-workflow.
State: services/billing migrated, services/orders pending.
Constraint: do not touch services/legacy-invoicing — frozen pending a separate deprecation decision.
```

## Quality test

Before finalising, verify the prompt meets every Invariant and every Required output structure item:

- [ ] Skill anchor present if and only if an applicable installed skill governs execution.
- [ ] Concrete anchor present (`#N`, SHA, file path, or log path).
- [ ] Under ~1000 characters.
- [ ] No self-authorization preamble or permission-downgrade directive.
- [ ] No duplicated documentation, no history, no filler outside the operational handoff.
- [ ] The next agent will know exactly what to do, what to read first, and what not to reopen.

## Final instruction

Output the prompt only.
