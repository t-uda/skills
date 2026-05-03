---
name: lite-spec
description: Produce a compact execution spec for bounded, non-trivial implementation work that needs a short execution brief but does not require `metaplan`.
---

# Lite Spec

Create a compact execution brief for bounded implementation work: more than a tiny local edit, but not large or ambiguous enough for `metaplan`.

## When to use

Use this skill for bounded, non-trivial implementation work — typically spanning multiple files or one subsystem — when a short execution brief would reduce drift by writing down a few of the relevant scope, constraints, risks, or done criteria.

Do not use it for tiny edits that can be done immediately, or for large/high-risk/ambiguous changes that should go through `metaplan`.

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
