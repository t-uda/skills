---
name: handoff-prompt
description: Generate a compact handoff prompt for the next agent or stage. Output the prompt only.
---

# Handoff Prompt

Generate a **minimal sufficient prompt** for the next agent.

This skill is for **handoff and stage transition**. It is not a summarisation skill.

Its goal is to produce a prompt that lets the next agent start the correct work immediately, without needless background, duplicated documentation, user-side clarification, or avoidable rework.

## Use this skill when

Use this skill when the user wants a prompt to pass work to another agent, another role, or another stage.

Typical cases:

- continuing work in a fresh coding-agent context
- passing a completed plan or spec to an orchestrator
- passing research results to an implementation agent
- passing implementation state to a reviewer or debugger
- splitting work across multiple agents

## Core rule

Do **not** transfer everything.

Transfer only what the next agent needs in order to act correctly and efficiently.

The output must prioritise:

1. the immediate task
2. the correct starting references
3. decisions already fixed
4. non-obvious constraints or context
5. unresolved points that materially affect the next step
6. the required output

## Mandatory requirements

### 1. Output only the prompt

Return the transfer prompt and nothing else.

Do not add any preface, explanation, note, or follow-up text.

### 2. Keep it compact

Use the shortest prompt that still enables correct action.

If the prompt becomes long, compress harder. Excessive length is a warning sign that too much low-value context has been preserved.

### 3. Do not duplicate existing documentation

Do not restate content already documented in places such as:

- `AGENTS.md`
- specification documents
- implementation plans
- architecture documents
- repository workflow instructions

Refer to those sources briefly instead of copying them.

### 4. Preserve only non-obvious context

Include only context that the next agent is unlikely to recover reliably from the repository or existing documents.

Examples of valid carry-over:

- decisions already made
- options explicitly rejected
- hidden constraints
- important user preferences that affect execution
- known traps, weak spots, or misleading artefacts
- priority ordering that is not obvious from the files alone

### 5. Remove history that does not change action

Do not include:

- narrative history
- abandoned detours that no longer matter
- motivational explanation
- general background that does not affect the next action
- obvious operational instructions already documented elsewhere

### 6. Optimise for autonomous execution

The generated prompt must help the next agent proceed **without**:

- asking the user for avoidable clarification
- stalling because of ambiguous wording
- re-opening settled decisions
- causing avoidable rework

Write the prompt so that the next agent can determine what to do, what not to do, what to read first, and what to produce.

## Role-specific requirements

### Coding agent

Emphasise:

- the concrete implementation task
- the files or documents to inspect first
- design decisions already fixed
- implementation constraints
- expected code, test, and document outputs

### Orchestrator

Emphasise:

- the current task to be coordinated
- the complexity of the task
- the required decomposition into sub-agents if needed
- the need to choose appropriate models for the sub-agents based on task complexity
- decisions already fixed and not to be reopened
- the required final deliverable and coordination objective

An orchestrator handoff must explicitly guide the orchestrator to judge task complexity and assign suitable sub-agents and model levels accordingly.

### Reviewer or debugger

Emphasise:

- the review or debugging target
- intended behaviour
- likely failure points
- specific areas requiring scrutiny
- the required review output

### Research agent

Emphasise:

- the concrete research question
- scope boundaries
- assumptions already fixed
- the form of findings needed
- what lines of investigation are out of scope

## Preferred content structure

Include only the elements that are necessary for the specific handoff, chosen from:

1. target role
2. immediate task
3. read first
4. fixed decisions
5. non-obvious context
6. open issues that affect the next step
7. constraints and prohibitions
8. required output

Do not force a full template when fewer elements are sufficient.

## Writing rules

The generated prompt must be:

- specific
- operational
- compact
- unambiguous
- easy to copy

Avoid wording that is broad, vague, interpretive, or compatible with too many possible meanings.

Prefer direct instructions over abstract guidance.

## Quality test

Before finalising the transfer prompt, ensure that:

- the next agent will know exactly what to do next
- the next agent will know what to read first
- the next agent will not needlessly re-read duplicated material
- the next agent will not ask the user for clarification unless a truly missing input remains
- the next agent will not reopen settled choices
- the prompt contains no filler outside the operational handoff

## Final instruction

When invoked, output the transfer prompt immediately.

Return the prompt only.
