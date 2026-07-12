---
name: triage
description: Decide whether a development task should be done now, handled with `lite-spec`, or sent to `metaplan`.
---

# Triage

Classify an incoming development task into one route — `DO_IT_NOW`, `LITE_SPEC`, or `METAPLAN` — so planning overhead stays proportional to task difficulty. Always prefer the lightest route that still protects execution quality.

## When to use

Use this skill when:

- the user asks which planning depth is appropriate
- the task may or may not justify structured planning
- the implementation scope is not yet clear
- the user refers to staged planning, triage, routing, or planning depth selection
- it is unclear whether immediate execution would be efficient or reckless

Do not use this skill when the user has already chosen a specific planning mode and that choice is clearly appropriate.

## Decision model

Assess the task on five axes. Each row names the axis's risk end and what it means; the safe end is the converse (concrete / local / easy to undo / unlikely to pause / planning overhead exceeds likely rework cost).

| Axis (risk end) | Risk end means |
|---|---|
| Ambiguity (high) | requirements, scope, constraints, or completion criteria read in more than one materially different way |
| Blast radius (high) | crosses architecture, interfaces, invariants, or migration paths |
| Reversibility (low) | a wrong implementation is hard or costly to undo |
| Interruption risk (high) | a coding agent would likely stall, guess, or re-research |
| Review value (high) | upfront planning would materially cut rework, drift, or hallucinated decisions |

### Routing procedure

Evaluate in order; the first match wins.

1. **`METAPLAN`** — Ambiguity high, Blast radius high, Reversibility low, or Interruption risk high (any one), or execution depends on a hardened spec/plan/task breakdown that does not yet exist. Review value at its risk end alone, with the other four axes safe, does not trigger `METAPLAN`.
2. **`DO_IT_NOW`** — otherwise, if most axes are at their safe end.
3. **`LITE_SPEC`** — otherwise (default): bounded but not trivial; a short brief would reduce drift.

### Tie resolution

A bounded task can also trip a `METAPLAN` trigger; the ordering resolves this: `METAPLAN` wins, because material ambiguity, invariant impact, costly-to-undo mistakes, and likely stalls outrank scope-boundedness. Below that bar, `LITE_SPEC` remains the default for mixed signals; route `DO_IT_NOW` instead only on a genuine borderline tie (unclear whether most axes sit at their safe end) where a brief would merely restate an already concrete task — if a brief would capture any constraint, risk, or edge case worth writing down, `LITE_SPEC` stands.

### Insufficient information

Treat an unassessable axis as ambiguity. Ask one targeted question naming what is missing only if the answer could change the route; otherwise assume the heavier plausible reading and proceed.

## Output format

Return:

1. the selected route
2. a short justification
3. the main factors that drove the decision (axis levels from the Decision model, not restated criteria)
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

## Boundary cases

- `DO_IT_NOW`: a wording fix or narrow bug fix with obvious acceptance criteria.
- `LITE_SPEC`: a feature spanning several files in one subsystem, bounded but not trivial.
- `METAPLAN`: a migration touching a public interface with several unresolved design choices.
- `LITE_SPEC`/`METAPLAN` boundary: a multi-file refactor with clear scope, no material ambiguity, low interruption risk, moderately costly worst case → `LITE_SPEC` (no trigger fires); the same refactor with one API decision left open and a hard-to-undo migration → `METAPLAN` (Interruption risk high and Reversibility low both trigger).
- Multi-condition: Blast radius and Review value at risk ends, Ambiguity low, Reversibility high → `METAPLAN`; Blast radius alone triggers it (step 1 matches first).
- Insufficient information: "improve the auth flow" with no target behavior stated → the missing target could shift the route between `LITE_SPEC` and `METAPLAN`; ask one question naming it before routing.
- Lightest-route bias: a mechanical, reversible rename touching six files, no interface change → `DO_IT_NOW`, not `LITE_SPEC`; file count alone does not put Blast radius at its risk end, and a brief would only restate the task.

## Important constraints

- Prefer the lightest adequate route; never escalate merely because the task is technical.
- Do not under-plan when ambiguity would predictably cause clarification loops or rework.
- Optimise for total execution efficiency, not procedural formality.
