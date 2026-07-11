---
name: metaplan
description: Review and tighten specs, plans, and task breakdowns before implementation so an autonomous coding agent can execute without ambiguity or avoidable re-research.
---

# Metaplan

Review planning artifacts as the coding agent that must execute them. Do not restate the plan. Find what would cause wrong assumptions, interruption, rework, redundant research, or implementation drift, then propose concrete edits.

## Use when

Use this skill when the user wants to:

- review or harden a spec, plan, task list, or implementation brief before coding starts
- reduce ambiguity, rework, avoidable confirmations, or repeated research
- make source-of-truth order, boundaries, and completion criteria explicit
- improve plan quality through review-and-rewrite cycles

Do not use this skill for post-implementation code review unless the planning artifacts are also under review.

## Responsibility boundary

`metaplan` judges whether the work package is execution-ready.

- If a plan depends on an external or contested source-of-truth artifact, require the plan to name that artifact, its authority, and its precedence.
- If the trustworthiness of that artifact itself must be audited, invoke `sot-integrity`; do not duplicate its full trust model here.
- If repository-wide behavior is already governed by `AGENTS.md` or equivalent, feature plans should reference it instead of repeating it unless a local exception is required.

## Primary question

```text
Could a capable coding agent, with no prior knowledge beyond the repository and the provided artifacts, execute this task correctly and efficiently without stopping for clarification?
```

## Readiness Model

### 1. `Not ready`

Use `Not ready` if any blocker exists. A blocker is any issue that can cause:

- materially different implementations
- an unauthorized product, policy, architecture, migration, security, or UX decision
- reliance on missing or conflicting source-of-truth authority
- unverifiable completion
- a foreseeable stop for clarification
- major rework from hidden dependencies, sequencing, or cross-system impact

### 2. `Ready with minor fixes`

Use `Ready with minor fixes` only when no blocker exists, but bounded local edits should be made before or during handoff. Minor fixes include:

- missing paths, commands, or names that are inferable from the artifacts or repository
- local wording that creates avoidable branching but has an obvious correction
- duplicated generic instructions that can be deleted or replaced by a reference
- incomplete but non-blocking validation details
- small task-order or checklist repairs that do not change scope

### 3. `Ready`

Use `Ready` only when:

- no blocker or local edit is needed before implementation
- source-of-truth order, scope, open decisions, verification, and stop conditions are explicit
- task complexity is visible enough for a competent agent to start immediately

Do not downgrade or upgrade for tone. Judge only execution readiness.

## Audit Checks

Apply these checks once. Do not repeat the same finding under multiple headings.

### Goal and Scope

- Is the goal operational rather than aspirational?
- Are in-scope work, non-goals, ownership boundaries, and "must not change" areas explicit?
- Are performance, security, UX, migration, or compatibility constraints stated when relevant?

### Inputs and Prerequisites

- Are required files, modules, interfaces, environments, commands, credential requirements, fixtures, and data named when needed?
- Are secret values kept out of planning artifacts?
- Are prerequisites ordered before dependent tasks?
- Are fallback behaviors specified for expected edge cases?

### Source of Truth and Settled Facts

- Which artifact governs implementation if spec, issue, plan, tasks, `AGENTS.md`, README, or inline comments disagree?
- Does the plan summarize prior research conclusions instead of merely linking to background material?
- Does it distinguish settled facts from open questions?
- If trust or conflict in a source artifact is material, should `sot-integrity` run first?

### Decisions and Ambiguity

- Are unresolved choices converted into decision rules or explicitly marked as blocking?
- Do phrases such as "as appropriate", "if needed", "consider", "possibly", and "decide whether" hide required decisions?
- Are tie-breaks and edge-case policies authorized?

### Tasks and Dependencies

- Are tasks ordered by dependency and traceable to requirements?
- Are task units small enough to execute and measure?
- Do tasks hide design choices that should be settled before implementation?

### Completion and Verification

- Can each acceptance criterion be verified objectively?
- Are required tests, validation commands, review gates, rollout checks, or manual checks named?
- Is there a clear stop condition for failed validation?

### Efficiency

- Remove repeated instructions across spec, plan, and tasks.
- Replace global policy copies with references to the governing artifact.
- Delete motivational prose, broad background, and examples that do not affect execution.

### Complexity and Risk

- Are cross-cutting changes, migrations, data compatibility, recovery, and regression risks visible?
- Is uncertainty named where it changes implementation order or validation scope?
- Does the plan avoid presenting risky work as a trivial edit?

## Output Contract

Produce these sections in order.

### A. Verdict

State exactly one:

- `Ready`
- `Ready with minor fixes`
- `Not ready`

### B. Blockers

List only issues that justify `Not ready`. For each blocker include:

- title
- why it blocks autonomous execution
- smallest concrete fix

If there are no blockers, write `None`.

### C. Non-blocking fixes

List only issues that support `Ready with minor fixes` or useful cleanup under these headings when present:

- Ambiguity
- Missing context
- Source-of-truth problems
- Boundary problems
- Completion criteria gaps
- Token inefficiency
- Complexity visibility

Omit empty headings. If there are no non-blocking fixes, write `None`.

### D. Proposed edits

Prefer direct patches the user can apply. Use one of:

- `Replace with`
- `Add`
- `Delete`
- `Move to AGENTS.md`
- `Move to task breakdown`
- `Reference instead of repeating`

Do not write "clarify this"; write the clarification.

### E. Readiness checklist

Use exact `pass` / `fail` status for:

- Goal is unambiguous
- Inputs and prerequisites are explicit
- Source of truth is explicit
- Scope boundaries are explicit
- Open decisions are resolved
- Completion criteria are testable
- Redundant instructions are removed
- Task complexity is legible to an agent

### F. Next action

End with exactly one:

- `revise the spec`
- `revise the plan`
- `revise the task breakdown`
- `update AGENTS.md or equivalent repository guidance`
- `proceed to implementation`

## Editing Rules

- Preserve intent; do not invent product or technical requirements.
- Prefer the smallest edit that removes the execution risk.
- Treat a question as blocking only when no safe local fix can be inferred.
- Convert optionality into decision rules and make precedence explicit when artifacts can disagree.
- Keep settled facts, open decisions, assumptions, and validation evidence distinct.
- Move durable repository policy to `AGENTS.md` or equivalent; keep feature plans feature-specific.
- Do not inflate minor issues into blockers.

## Boundary Cases

- `Ready`: the plan names source precedence, scope, ordered tasks, validation, and stop conditions; no edits are needed.
- `Ready with minor fixes`: the plan is executable, but it repeats global test commands and omits an inferable file path in one task.
- `Not ready`: the plan asks the agent to "choose the API design" without authorized criteria; implementation could diverge materially.
- Overlap case: if a source-of-truth gap also makes implementation branch, classify it as `Not ready`; otherwise list it as a non-blocking source-of-truth fix.
- Insufficient information: if the artifact set is incomplete and the missing artifact controls scope or acceptance, classify as `Not ready`.

## Quality Check

Before finishing, verify:

- the verdict follows the readiness model
- every blocker names a concrete failure mode and smallest fix
- non-blocking findings are not duplicated as blockers, and proposed edits are directly actionable
- output headings and final next-action value match the contract exactly
- source-of-truth trust questions are delegated to `sot-integrity` when appropriate
