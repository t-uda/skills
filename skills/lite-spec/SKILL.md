---
name: lite-spec
description: Produce a compact execution spec for bounded implementation tasks that are too large to do immediately but do not require `metaplan`.
---

# Lite Spec

Produce a compact planning document for medium-complexity implementation work.

This skill covers the middle zone between:

- doing the work immediately
- sending planning artifacts to `metaplan`

The goal is to create just enough structure to reduce ambiguity and rework without imposing heavy process overhead.

## When to use

Use this skill when:

- the task is not trivial
- some decisions, risks, or boundaries should be made explicit
- implementation spans multiple files or one bounded subsystem
- a coding agent would benefit from a concise execution brief
- full review of detailed planning artifacts would be excessive

Do not use this skill for:

- tiny local edits that can be executed immediately
- large, high-risk, or highly ambiguous changes that should go through `metaplan`

## Deliverable

Produce a single compact document with these sections.

# Task
A short statement of what is being changed.

# Goal
The intended operational outcome.

# Scope
## In
What is included.

## Out
What is excluded.

# Constraints
Known requirements, assumptions, conventions, or non-negotiable conditions.

# Risks
The main failure modes, ambiguities, or edge cases.

# Implementation outline
A short sequence of concrete implementation steps.

# Done criteria
Observable conditions that determine completion.

## Style requirements

- Be compact.
- Prefer concrete statements over discussion.
- Avoid speculative design unless necessary.
- Optimise for immediate executability.
- Write for a coding agent with no hidden context.

## Procedure

1. Restate the task in concrete terms.
2. Identify the minimum necessary scope.
3. Extract explicit constraints and assumptions.
4. List only the most relevant risks.
5. Produce a short implementation outline.
6. Define done criteria that can be checked objectively.

## Output template

```md
# Task

# Goal

# Scope
## In
## Out

# Constraints

# Risks

# Implementation outline

# Done criteria
```

## Important constraints

- Do not expand into a full design document unless clearly necessary.
- Do not create artificial sections beyond the template.
- Keep the document lean enough that writing it costs less than one failed implementation attempt.
