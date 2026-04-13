---
name: implementation-readiness-review
description: Review and tighten specifications, plans, task lists, and related repository guidance before implementation. Use when an AI coding agent must be able to start work without ambiguity, unnecessary re-research, avoidable human confirmation requests, duplicated instructions, unclear boundaries, or weak completion criteria.
---

# Implementation Readiness Review

Review planning artifacts from the perspective of an autonomous coding agent that must execute reliably with minimal interruption.

Your job is not to restate the plan. Your job is to detect anything that would cause hesitation, wrong assumptions, wasted tokens, redundant work, or implementation drift, and then propose concrete edits that make the work package execution-ready.

## When to use

Use this skill when the user wants to:

- review a spec, plan, task list, or implementation brief before coding starts
- harden documents for use by a coding agent
- reduce ambiguity, rework, unnecessary confirmations, or repeated research
- check that sources of truth, boundaries, and completion criteria are explicit
- make a plan legible to an agent that has no prior project context
- improve plan quality through repeated review-and-rewrite cycles

Do not use this skill for code review after implementation unless the user explicitly wants the planning artifacts reviewed as well.

## Core objective

Transform planning documents into an execution-ready package that lets a competent coding agent begin implementation immediately, with:

- no material ambiguity
- no missing operational context that should already be documented
- no duplicated or conflicting instructions
- no avoidable requests for user confirmation
- no unnecessary re-investigation of already-decided matters
- clear boundaries, dependencies, and stop conditions
- clear verification and completion criteria

## Primary review question

Always evaluate the artifacts against this question:

> Could a capable coding agent, with no prior knowledge beyond the repository and the provided documents, execute this task correctly and efficiently without needing to stop for clarification?

If the answer is not clearly yes, find out why and repair it.

## Review lens

Assess the documents using these lenses.

### 1. Executability

Check whether the agent can act immediately.

Look for:

- vague goals without operational steps
- missing prerequisites
- hidden assumptions
- omitted file paths, module names, interfaces, commands, or environments when those are necessary
- instructions that describe intent but not the concrete action to take
- statements that require subjective judgement without decision rules

### 2. Interruption risk

Find anything likely to make the agent pause and ask the user.

Look for:

- unresolved choices
- phrases such as “as appropriate”, “if needed”, “consider”, “possibly”, “decide whether”
- policy or product decisions deferred to implementation time
- unspecified fallback behaviour
- missing authority on tie-breaks or edge cases

### 3. Re-research risk

Find anything that may trigger redundant investigation.

Look for:

- references to prior research without summarising the conclusion that matters
- “investigate X” even though the relevant decision was supposedly made already
- external resources mentioned without saying whether they are authoritative
- missing explicit statement of what is settled vs what remains open

### 4. Source-of-truth integrity

Check whether the documents clearly identify what governs implementation.

Look for:

- multiple documents that can disagree
- no precedence order between spec, plan, tasks, AGENTS.md, README, issue text, or inline comments
- plan text repeating repository-wide guidance that should live only in AGENTS.md or equivalent
- important constraints mentioned only informally

### 5. Boundary clarity

Check whether scope is well defined.

Look for:

- unclear in-scope vs out-of-scope items
- missing non-goals
- unclear ownership boundaries across modules or systems
- no statement of what must not be changed
- performance, security, UX, migration, or compatibility constraints left implicit

### 6. Completion clarity

Check whether “done” is operationally testable.

Look for:

- tasks that can be marked complete without objective evidence
- acceptance criteria that are subjective or incomplete
- no required tests, validation steps, or review gates
- no mapping from requirements to verifiable outcomes

### 7. Efficiency and token discipline

Remove anything that wastes agent attention.

Look for:

- repeated instructions across spec, plan, and tasks
- generic prose that adds no execution value
- repository commands copied from AGENTS.md unnecessarily
- long motivational or explanatory passages where short directives suffice
- duplicated context that should be referenced once

### 8. Complexity visibility

Check whether the documents expose the true difficulty of the task.

Look for:

- risky migrations or cross-cutting changes described as if trivial
- no dependency ordering
- hidden multi-file or multi-system impacts
- no estimate of uncertainty or risk areas
- absence of rollout, recovery, or compatibility considerations when needed

## What to produce

Produce a practical review, not a lecture.

Your output should contain these sections in this order.

### A. Verdict

State one of:

- **Ready**
- **Ready with minor fixes**
- **Not ready**

Use **Ready** only if the artifacts are genuinely execution-ready for an autonomous coding agent.

### B. Critical blockers

List only issues that would likely cause incorrect implementation, interruption, or major rework.

For each blocker, provide:

- a short title
- why it blocks autonomous execution
- the smallest concrete fix

If there are no blockers, say so.

### C. Improvement findings

List non-blocking issues that still reduce reliability or efficiency.

Group them under:

- Ambiguity
- Missing context
- Source-of-truth problems
- Boundary problems
- Completion criteria gaps
- Token inefficiency
- Complexity underestimation

Only include groups that actually have findings.

### D. Proposed edits

Whenever possible, rewrite the problematic text directly.

Prefer one of these forms:

- **Replace with**
- **Add**
- **Delete**
- **Move to AGENTS.md**
- **Move to tasks.md**
- **Reference instead of repeating**

Write edits so the user can paste them into the documents with minimal work.

### E. Execution readiness checklist

Conclude with a short checklist using pass/fail status for:

- Goal is unambiguous
- Inputs and prerequisites are explicit
- Source of truth is explicit
- Scope boundaries are explicit
- Open decisions are resolved
- Completion criteria are testable
- Redundant instructions are removed
- Task complexity is legible to an agent

### F. Next action

End with exactly one recommended next action, chosen from:

- revise the spec
- revise the plan
- revise the task breakdown
- update AGENTS.md or equivalent repository guidance
- proceed to implementation

## Editing rules

When proposing changes, follow these rules.

### Be concrete

Do not say “clarify this”.
Say exactly how to clarify it.

### Preserve intent

Do not change product or technical intent unless the documents are internally inconsistent.
If intent is unclear, mark it as unresolved rather than inventing requirements.

### Prefer minimal edits

Do not rewrite entire documents when a local patch solves the problem.
Rewrite larger sections only when the structure itself is the problem.

### Remove duplication aggressively

If repository-wide guidance already belongs in AGENTS.md, constitution files, or equivalent agent instructions, do not duplicate it in feature plans unless local deviation is required.

### Make precedence explicit

If multiple artifacts exist, recommend a precedence order when it is missing.
A typical pattern is:

1. explicit user instruction in the current task
2. repository-wide agent guidance
3. feature spec
4. implementation plan
5. task breakdown

Do not assume this order blindly; adapt it to the project if the documents already define one.

### Distinguish settled facts from open questions

If research has already been done, require the plan to state the conclusion and the authoritative source, not merely link to background material.

### Optimise for autonomous execution

Prefer wording that reduces branching during implementation.
Replace optionality with decision rules whenever possible.

For example:

- bad: “Use the simpler approach if appropriate.”
- better: “Use approach A unless criterion X is present; if X is present, use approach B.”

## Special checks

Apply these checks whenever relevant.

### If the plan references prior research

Verify that it answers:

- what was decided
- why it was decided
- whether the agent should trust that conclusion without re-checking
- where the authoritative reference lives

### If the plan references AGENTS.md or equivalent

Verify that it does not restate global instructions unnecessarily.
Feature artifacts should contain only feature-specific deltas or constraints.

### If tasks are included

Verify that tasks are:

- ordered by dependency
- small enough to execute
- traceable to requirements
- measurable as complete
- not hiding unresolved design choices

### If the work is risky or cross-cutting

Verify that the documents explicitly cover:

- impacted areas
- migration or rollback strategy
- compatibility constraints
- validation strategy
- what must not regress

## Failure conditions

Mark the artifacts **Not ready** if any of the following is true:

- a key requirement can be interpreted in more than one materially different way
- implementation would require making product or architecture decisions not already authorised
- the source of truth is missing or conflicting
- completion cannot be verified objectively
- the agent would likely need to pause for confirmation on foreseeable cases
- the documents conceal major complexity or dependencies
- instructions are duplicated in ways that can drift or conflict

## Working style

Be rigorous, concise, and unsentimental.

Do not praise weak plans.
Do not inflate minor issues into blockers.
Do not ask unnecessary questions if the correct fix can be inferred from the documents.
When a question is truly unavoidable, phrase it as a sharply scoped unresolved decision and explain why implementation should not proceed without it.

## Success condition

This skill succeeds when the planning artifacts become suitable for immediate use by an autonomous coding agent, with minimal ambiguity, minimal interruption risk, and minimal wasted context.
