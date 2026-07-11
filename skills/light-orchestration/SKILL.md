---
name: light-orchestration
description: Decide whether to execute a task directly or split it into a small number of tightly bounded subtasks, and produce minimal subtask contracts only when orchestration is justified.
---

# Light Orchestration

Help an orchestrator choose between direct execution and a minimal multi-agent split, and produce strictly bounded subtask contracts when a split is justified. This skill is for lightweight orchestration only: when producing the plan would cost more context than it saves, the Decision cascade below routes to single-agent execution.

## Core rule

This skill produces a decomposition. It does not dispatch. The orchestrator decides whether to invoke subagents and runs the dispatch itself. Treat any output of this skill as advisory until the orchestrator acts on it.

## When to use

Invoke this skill only when execution may need to span multiple subagents. For a single task that fits in one agent's context, choose planning depth via `triage` or write the brief via `lite-spec` directly; do not invoke this skill.

Use this skill when:

- a task may or may not benefit from being split across subagents
- an orchestrator must decide whether to execute directly or dispatch
- the user is considering parallel or staged subagent work
- bounded handoffs would reduce context bloat in a long task
- coordination between a small number of subtasks needs to be made explicit

Do not use this skill for:

- choosing planning depth (use `triage`)
- producing an execution brief for one bounded task (use `lite-spec`)
- hardening specs and plans before implementation (use `metaplan`)
- generating a single transfer prompt (use `handoff-prompt`)
- full workflow-engine design or automatic dispatch

## Inputs

Gather before proceeding. Ask the user for any that are missing — do not guess `context_budget` or `current_context` and do not proceed to the cascade on incomplete information.

- `task` — the work to be done
- `current_context` — what the orchestrator already has loaded (file paths / anchors) plus an estimated token footprint, or small/medium/large relative to `context_budget` when an exact count is unavailable
- `context_budget` — approximate token window available to a single agent in this harness
- `known_decisions` — design or scope choices already settled
- `repository_anchors` — file paths, modules, or docs that scope the work
- `constraints` — deadlines, budgets, parallelism limits, or required outputs

## Decision cascade

The single authoritative selection algorithm: evaluate the steps in order, stop at the first match. Step 3 is an unconditional default, so exactly one mode is always selected and every mode is reachable.

### Step 1 — `DEFER_OR_SPLIT_REWRITE`

Match if any of the following hold:

- a sound decomposition cannot be defined because a design or scope decision that would change subtask boundaries is still unresolved (absent from `known_decisions`)
- the task is too large or entangled to state even provisional local contracts for its subtasks
- the correct next step is rewriting or narrowing the task, not orchestrating it

If matched: do not produce a decomposition. Recommend the rewrite or scoping step, and require the orchestrator to re-invoke this skill once the task has been rewritten or the missing decision is settled. State the concrete re-invocation trigger (for example, "after `metaplan` returns Ready" or "after the user confirms the new scope").

### Step 2 — `ORCHESTRATE`

Reached only if Step 1 did not match. Match if **all** of the following hold:

- the task splits into a small number of subtasks (prefer 2–3, avoid more than 4) whose file/context needs barely overlap
- each subtask can be given clear local inputs, outputs, and a bounded contract (see Subtask contract)
- dependencies between subtasks are shallow — no long sequential chain
- total token cost across orchestrator plus subagents, including the cost of writing this plan, is lower than single-agent execution

If any fails, Step 2 does not match — fall through to Step 3.

### Step 3 — `SINGLE_AGENT` (default)

Reached whenever Steps 1 and 2 do not match; no further conditions apply. This is the bias-toward default — mixed or marginal evidence for `ORCHESTRATE` lands here, not a reason to write a longer plan to force a Step 2 match.

### Cascade in practice

Compact validation cases; mode strings match the Output format section A enum exactly.

| Case | Step reached | Mode |
|---|---|---|
| Open scope decision would change subtask boundaries | 1 | `DEFER_OR_SPLIT_REWRITE` |
| Fixed scope; 2 low-overlap subtasks, shallow deps, clear savings | 2 | `ORCHESTRATE` |
| Boundary: 2-way split possible, but pieces need ~80% of the same files | 2 fails (overlap) → 3 | `SINGLE_AGENT` |
| Boundary: splittable except one open decision on who owns a shared utility | 1 | `DEFER_OR_SPLIT_REWRITE` |
| Multi-condition: high file overlap + uncertain execution order + fits one context | 1 no (order ≠ unresolved design decision); 2 fails (overlap) → 3 | `SINGLE_AGENT` |
| Fits one context; a split would only add coordination overhead | 2 fails (net cost) → 3 | `SINGLE_AGENT` |
| `context_budget` or `current_context` missing | pre-cascade | ask the user; do not enter the cascade |
| Mixed signals, no demonstrable payoff | 2 fails (no clear match) → 3 | `SINGLE_AGENT` |

## Decomposition rules

Apply these only when the cascade selects `ORCHESTRATE`.

- use the fewest tasks that preserve clear boundaries
- order tasks by dependency; mark tasks that may run in parallel
- avoid overlapping file ownership across tasks
- avoid duplicated repository exploration; assign anchor files to one task and let others reference its output
- mark settled decisions as fixed and prohibit reopening them
- name what each task must not do, not just what it must do

If the split cannot satisfy these rules, treat Step 2 as unmatched and re-run from Step 3 (`SINGLE_AGENT`, or `DEFER_OR_SPLIT_REWRITE` if an unresolved decision is the cause).

## Subtask contract

Each subtask must include all of the following fields.

- **task** — one sentence describing the work
- **read first** — minimal files or docs to load before acting
- **do not read unless needed** — areas explicitly out of scope to reduce context bloat
- **fixed decisions** — choices already settled; not to be reopened
- **constraints** — required behaviour, prohibitions, or coordination rules
- **expected output** — concrete deliverable (files, diff, prompt, summary)
- **done criteria** — observable conditions that determine completion

Keep each contract compact. If a contract grows long, the split is probably wrong — reconsider the cascade.

## Global constraints

Required when the cascade selects `ORCHESTRATE`. Define:

- shared invariants neither subtask may violate
- coordination rules (ordering, merge points, shared file ownership)
- validation or merge strategy for combining outputs
- escalation rule when a subtask discovers that a fixed decision is wrong

If no escalation rule is provided, the default is: the subtask must halt and surface the conflict to the orchestrator before proceeding. Subtasks must never silently override a fixed decision.

Omit this section when the mode is `SINGLE_AGENT` or `DEFER_OR_SPLIT_REWRITE`.

## Output format

Return sections in this order.

### A. Decision

- execution mode: `SINGLE_AGENT | ORCHESTRATE | DEFER_OR_SPLIT_REWRITE`
- which cascade step matched, and a short justification tied to that step's conditions

### B. Decomposition

Include only when mode is `ORCHESTRATE`. List tasks in dependency order with one-line boundaries. Mark parallelisable tasks.

### C. Subtask contracts

One block per task using the required fields above.

### D. Global constraints

Shared invariants, coordination rules, validation or merge strategy, and escalation rule. Omit when mode is `SINGLE_AGENT` or `DEFER_OR_SPLIT_REWRITE`.

### E. Next action

Exactly one of:

- proceed with single-agent execution — `SINGLE_AGENT`
- dispatch subagents — `ORCHESTRATE`
- refine task split — `DEFER_OR_SPLIT_REWRITE`

## Example output (skeleton)

A minimal `ORCHESTRATE` output looks like the following. Use it as a shape, not a template to copy verbatim.

```text
A. Decision
- mode: ORCHESTRATE
- step: Step 2 matched — low-overlap split, shallow deps, clear savings
- justification: <1–2 sentences tied to the Step 2 conditions>

B. Decomposition
1. <Task A> — <one-line boundary>
2. <Task B> — <one-line boundary> (depends on 1; may run after A completes)

C. Subtask contracts
### Task A
- task: ...
- read first: ...
- do not read unless needed: ...
- fixed decisions: ...
- constraints: ...
- expected output: ...
- done criteria: ...

### Task B
- task: ...
- read first: ...
- do not read unless needed: ...
- fixed decisions: ...
- constraints: ...
- expected output: ...
- done criteria: ...

D. Global constraints
- invariants: ...
- coordination: ...
- merge: ...
- escalation: ...

E. Next action
dispatch subagents
```

For `SINGLE_AGENT`, sections B–D are omitted and section E is `proceed with single-agent execution`. For `DEFER_OR_SPLIT_REWRITE`, sections B–D are omitted and section E is `refine task split`.

## Working rules

Listed roughly in priority order.

- Do not auto-dispatch — this skill produces a decomposition; the orchestrator dispatches (see **Core rule**).
- Follow the cascade in order; do not shortcut to a preferred mode.
- Keep total subtasks small — more tasks usually mean more handoff cost, not more speed.
- Forbid repository-wide re-reads; each subtask reads only what its contract names.
- Forbid reopening fixed decisions; escalate per the global escalation rule (or its default) rather than diverging.
- Do not assign overlapping file ownership across subtasks.
- A long orchestration narrative is itself evidence the cascade should have landed on `SINGLE_AGENT` or `DEFER_OR_SPLIT_REWRITE`.
- Do not duplicate repository-wide guidance already in `AGENTS.md` or equivalent — reference it.

## Relationship to other skills

This skill complements but does not replace:

- `triage` — choose planning depth for a single task
- `lite-spec` — write a compact execution brief for a bounded task
- `metaplan` — review and tighten specs and plans before implementation
- `handoff-prompt` — generate a single transfer prompt for one next agent

Recommended sequence (advisory, not enforced): triage the task → if implementation, optionally `lite-spec` or `metaplan` → if multi-agent execution is being considered, run this skill → for each dispatched subtask, use `handoff-prompt` to render the final transfer prompt.
