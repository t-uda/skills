---
name: triage
description: Decide whether a development task should be done now, handled with `lite-spec`, or sent to `metaplan`.
---

# Triage

Classify an incoming development task into one of three routes:

- `DO_IT_NOW`
- `LITE_SPEC`
- `METAPLAN`

The purpose of this skill is to keep planning overhead proportional to task difficulty.
Use the lightest route that still protects execution quality.

## When to use

Use this skill when:

- the user asks which planning depth is appropriate
- the task may or may not justify structured planning
- the implementation scope is not yet clear
- the user refers to staged planning, triage, routing, or planning depth selection
- it is unclear whether immediate execution would be efficient or reckless

Do not use this skill when the user has already chosen a specific planning mode and that choice is clearly appropriate.

## Evaluation criteria

Assess the task on these axes.

### 1. Ambiguity

How unclear are the requirements, scope, constraints, or completion conditions?

### 2. Blast radius

How many files, modules, interfaces, workflows, or behaviours are likely to change?

### 3. Reversibility

How easy would it be to undo a bad implementation choice?

### 4. Interruption risk

How likely is a coding agent to pause for clarification during execution?

### 5. Review value

How much would upfront planning reduce rework, drift, or hallucinated decisions?

## Routing rules

### Route: DO_IT_NOW

Choose this when most of the following hold:

- requirements are already concrete
- impact is local
- the change is easily reversible
- acceptance criteria are obvious
- planning overhead would exceed likely rework cost

Typical examples:

- wording edits
- renaming
- tiny bug fixes
- narrow mechanical changes
- local refactors with obvious boundaries

### Route: LITE_SPEC

Choose this when:

- the task is not trivial, but still bounded
- a short execution brief would reduce drift
- a few constraints, risks, or edge cases should be written down
- full review of heavy planning artifacts would be disproportionate

Typical examples:

- medium feature additions
- non-trivial refactors within one subsystem
- changes spanning several files with limited design uncertainty
- work that needs one compact implementation brief before coding

### Route: METAPLAN

Choose this when one or more of the following hold:

- requirements are materially ambiguous
- the change affects architecture, interfaces, invariants, or migration
- multiple design choices must be resolved or tightened before coding
- the cost of a wrong implementation is high
- a coding agent would likely stall, guess, or re-research
- execution depends on hardened specs, plans, or task breakdowns

Typical examples:

- cross-cutting refactors
- architecture changes
- risky migrations
- tasks intended for autonomous coding agents where interruption must be minimised

## Output format

Return:

1. the selected route
2. a short justification
3. the main factors that drove the decision
4. the immediate next action

Use this structure:

```text
Route: <DO_IT_NOW | LITE_SPEC | METAPLAN>

Why:
- ...
- ...

Key factors:
- Ambiguity: low|medium|high
- Blast radius: low|medium|high
- Reversibility: high|medium|low
- Review value: low|medium|high

Next action:
- ...
```

## Important constraints

- Prefer the lightest adequate route.
- Do not escalate merely because the task is technical.
- Do not under-plan when ambiguity would predictably cause clarification loops or rework.
- Optimise for total execution efficiency rather than procedural formality.
