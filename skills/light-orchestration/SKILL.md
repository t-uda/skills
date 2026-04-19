---
name: light-orchestration
description: Decide whether to execute a task directly or split it into a small number of tightly bounded subtasks, and produce minimal subtask contracts only when orchestration is justified.
---

# Light Orchestration

Help an orchestrator choose between direct execution and a minimal multi-agent split, and produce strictly bounded subtask contracts when a split is justified.

This skill is for lightweight orchestration only. If producing the orchestration plan would cost more context than it saves, recommend single-agent execution.

## When to use

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

Gather before proceeding. Ask the user for any that are missing.

- `task` — the work to be done
- `current_context` — what the orchestrator already has loaded
- `known_decisions` — design or scope choices already settled
- `repository_anchors` — file paths, modules, or docs that scope the work
- `constraints` — deadlines, budgets, parallelism limits, or required outputs

## Decision criteria

Bias toward `SINGLE_AGENT`. Choose `ORCHESTRATE` only when a split clearly reduces total cost.

Assess on these axes.

### 1. Context separability

Can the work be cut into pieces whose contexts barely overlap? If subtasks would each need most of the same files, splitting wastes context.

### 2. Coordination overhead

How much shared state must move between subtasks? High coordination defeats the savings of parallelism.

### 3. Independence and dependency depth

Can subtasks run independently, or do they form a long sequential chain? Long chains add handoff cost without adding parallelism.

### 4. Expected token savings

Would splitting reduce total token use across all agents (orchestrator plus subagents) compared to single-agent execution? If not, do not split.

### 5. Plan-vs-payoff ratio

If the orchestration plan itself would be long or fragile, treat that as evidence against orchestration, not as a reason to produce a longer plan.

## Execution modes

Choose exactly one.

### `SINGLE_AGENT`

Choose this when most of the following hold:

- the task fits comfortably in one agent's context
- subtasks would heavily overlap in files or background
- coordination overhead would dominate any parallel savings
- the orchestration plan would be longer than the task itself

Default to this mode unless a cheaper split can be described concretely.

### `ORCHESTRATE`

Choose this when all of the following hold:

- the task can be cut into a small number of low-overlap subtasks
- each subtask has clear local inputs and outputs
- dependencies between subtasks are shallow and explicit
- splitting will reduce total cost or unblock parallelism

Use the fewest subtasks that preserve clear boundaries. Prefer two or three over five.

### `DEFER_OR_SPLIT_REWRITE`

Choose this when:

- the task is too ambiguous, too large, or too entangled to split cleanly
- decomposition would require design or scoping decisions not yet made
- the right next step is to rewrite the task itself before orchestrating

In this mode, do not produce a decomposition. Recommend the rewrite or planning step instead.

## Decomposition rules

When mode is `ORCHESTRATE`:

- use the fewest tasks that preserve clear boundaries
- order tasks by dependency; mark tasks that may run in parallel
- avoid overlapping file ownership across tasks
- avoid duplicated repository exploration; assign anchor files to one task and let others reference its output
- mark settled decisions as fixed and prohibit reopening them
- name what each task must not do, not just what it must do

If you cannot satisfy these rules with the proposed split, return to mode selection and prefer `SINGLE_AGENT` or `DEFER_OR_SPLIT_REWRITE`.

## Subtask contract

Each subtask must include all of the following fields.

- **task** — one sentence describing the work
- **read first** — minimal files or docs to load before acting
- **do not read unless needed** — areas explicitly out of scope to reduce context bloat
- **fixed decisions** — choices already settled; not to be reopened
- **constraints** — required behaviour, prohibitions, or coordination rules
- **expected output** — concrete deliverable (files, diff, prompt, summary)
- **done criteria** — observable conditions that determine completion

Keep each contract compact. If a contract grows long, the split is probably wrong.

## Global constraints

When multiple subtasks exist, define:

- shared invariants neither subtask may violate
- coordination rules (ordering, merge points, shared file ownership)
- validation or merge strategy for combining outputs
- escalation rule when a subtask discovers that a fixed decision is wrong

Omit this section if mode is `SINGLE_AGENT` and no extra global constraints are needed.

## Output format

Return sections in this order.

### A. Decision

- execution mode: `SINGLE_AGENT | ORCHESTRATE | DEFER_OR_SPLIT_REWRITE`
- short justification tied to the decision criteria

### B. Decomposition

Include only when mode is `ORCHESTRATE`. List tasks in dependency order with one-line boundaries. Mark parallelisable tasks.

### C. Subtask contracts

One block per task using the required fields above.

### D. Global constraints

Shared invariants, coordination rules, and validation or merge strategy. Omit when mode is `SINGLE_AGENT` and no extra global constraints are needed.

### E. Next action

Exactly one of:

- proceed with single-agent execution
- dispatch subagents
- refine task split

## Working rules

- Prefer `SINGLE_AGENT` unless a cheaper split is concretely describable.
- Keep total subtasks small. More tasks usually mean more handoff cost, not more speed.
- Forbid repository-wide re-reads. Each subtask reads only what its contract names.
- Forbid reopening fixed decisions. If a subtask believes a fixed decision is wrong, escalate per the global escalation rule rather than diverging.
- Do not assign overlapping file ownership across subtasks.
- Do not produce a long orchestration narrative. If the plan grows long, that is evidence to fall back to `SINGLE_AGENT` or `DEFER_OR_SPLIT_REWRITE`.
- Do not auto-dispatch. This skill produces a decomposition; the orchestrator dispatches.
- Do not duplicate repository-wide guidance that already lives in `AGENTS.md` or equivalent. Reference it.

## Relationship to other skills

This skill complements but does not replace:

- `triage` — choose planning depth for a single task
- `lite-spec` — write a compact execution brief for a bounded task
- `metaplan` — review and tighten specs and plans before implementation
- `handoff-prompt` — generate a single transfer prompt for one next agent

Recommended sequence (advisory, not enforced): triage the task → if implementation, optionally `lite-spec` or `metaplan` → if multi-agent execution is being considered, run this skill → for each dispatched subtask, use `handoff-prompt` to render the final transfer prompt.
