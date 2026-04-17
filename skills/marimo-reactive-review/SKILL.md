---
name: marimo-reactive-review
description: Review an existing marimo notebook for reactive design quality, identify anti-patterns against marimo's dependency model, and propose a concrete refactor plan without rewriting the notebook unless asked.
---

# marimo Reactive Review

Use this skill when the user already has a marimo notebook and wants to know whether it is idiomatic, reactive, maintainable, and aligned with marimo's execution model.

This skill is review-only by default. It should inspect, diagnose, and recommend. Do not rewrite the notebook unless the user explicitly asks for edits.

## Relationship to other skills

- If the task is to create or edit a marimo notebook, use `marimo-notebook`.
- If the task is to convert a Jupyter notebook, use `jupyter-to-marimo` first.
- If the task is to prepare a notebook for scheduled or CLI-driven runs, use `marimo-batch`.
- Use this skill when the task is to evaluate whether an existing marimo notebook is taking proper advantage of reactivity.

## Review goals

Assess whether the notebook:

1. respects marimo's dependency model;
2. avoids hidden non-reactive state;
3. separates configuration, computation, and presentation cleanly;
4. uses UI and state idiomatically;
5. avoids expensive or side-effectful recomputation in the reactive path;
6. would be easy to extend into an interactive app or reliable script.

## Core principles

Anchor the review in marimo's documented model:

- Reactivity is driven by definitions and references between cells.
- Cells form a DAG.
- Global names should be defined in only one cell.
- Mutations across cells are not tracked.
- Plain variables and widget `.value` should be preferred over callback-heavy patterns.
- `mo.state()` should be recommended only when genuinely needed.

## What to inspect

### 1. Dependency structure

Check whether the notebook has a clear def-use structure.

Look for:

- global variables defined in more than one cell;
- cells that mix unrelated responsibilities;
- overly long chains where one small input change triggers too much recomputation;
- opportunities to split cells by semantic stage: setup, config, load, derive, compute, render, export.

### 2. Non-reactive patterns

Flag patterns that weaken reactivity:

- mutating lists, dicts, dataframes, or objects across cells;
- assigning object attributes in one cell and reading them elsewhere;
- relying on execution history rather than explicit dependencies;
- callback-based state where a plain derived variable would suffice.

### 3. UI and parameterisation

Identify constants that should probably become inputs.

Look for:

- hard-coded analysis parameters that are natural slider, select, or text inputs;
- multiple related parameters that should be grouped with `.batch().form()`;
- expensive cells that should not rerun on every widget change;
- places where a button, form submission, `mo.stop`, or lazy runtime would reduce accidental recomputation.

### 4. Expensive computation boundaries

Check whether heavy work is isolated appropriately.

Look for:

- data download, model fitting, optimisation, persistence computation, large plotting, or file export directly attached to fine-grained UI changes;
- repeated work that could be lifted into helper functions, script mode branches, caching, or explicit run triggers;
- side effects such as `savefig`, file writes, downloads, or external API calls inside reactive paths.

### 5. State management

Check whether the notebook uses the simplest viable state model.

Prefer:

- plain variables;
- widget `.value`;
- derived values in downstream cells.

Flag for review:

- unnecessary `mo.state()`;
- unnecessary `on_change` callbacks;
- storing UI objects inside state;
- bidirectional sync implemented in a fragile way.

### 6. Reusability and structure

Look for opportunities to improve reuse and testability.

Examples:

- move common imports to a single setup region if appropriate;
- lift pure helper logic into reusable functions;
- use `app.setup` or `@app.function` when the notebook contains reusable top-level logic;
- separate rendering helpers from numerical kernels.

## Severity levels

Classify findings using these levels:

- Critical: likely breaks correctness, reactivity, or maintainability.
- Major: works today, but strongly fights marimo's model.
- Moderate: acceptable but non-idiomatic; worth refactoring.
- Minor: polish, clarity, or ergonomics improvements.

## Review procedure

1. Identify the notebook's high-level intent.
2. Map its current structure into stages such as setup, config, load, compute, render, and export.
3. Inspect each stage for violations of marimo's reactive model.
4. Separate findings into:
   - correctness and reactivity issues,
   - UI and state design issues,
   - expensive recomputation issues,
   - maintainability and reuse issues.
5. Propose a target architecture.
6. Recommend the smallest refactor set that yields the biggest improvement.

## Output format

Produce the review in this structure.

### A. Overall verdict

Give a short paragraph answering:

- Is the notebook merely valid marimo syntax?
- Or is it genuinely designed around marimo's reactive model?

### B. Findings table

For each finding, include:

- severity;
- short title;
- exact location;
- why it matters for marimo;
- recommended change.

### C. Target reactive architecture

Describe the notebook's ideal structure, for example:

- setup or imports
- parameter UI
- data loading
- derived intermediate data
- expensive compute step
- rendering
- export or reporting

### D. Refactor plan

Give a short ordered plan, prioritised by impact.

### E. Optional widget suggestions

Only include this section when helpful. Suggest which hard-coded parameters should become UI controls, and whether they should be live-reactive, form-submitted, or button-triggered.

## Guardrails

- Do not recommend `mo.state()` unless plain variable reactivity is insufficient.
- Do not recommend callback-heavy designs when direct dependency tracking is enough.
- Do not praise a notebook as reactive merely because it uses `@app.cell`.
- Distinguish clearly between:
  - already idiomatic marimo,
  - valid but Jupyter-like marimo,
  - actively fighting the runtime model.
- Keep recommendations practical. Prefer the smallest architecture change that materially improves reactivity.
- Do not rewrite code unless explicitly asked.

## Heuristics for common verdicts

### Valid but Jupyter-like

Use this when the notebook:

- is split into cells,
- runs under marimo,
- but mostly consists of fixed constants plus one-shot computations,
- with little or no `mo.ui` usage,
- and little evidence of deliberate reactive design.

### Good reactive structure

Use this when the notebook:

- defines each global once;
- avoids cross-cell mutation;
- cleanly separates inputs, heavy compute, and rendering;
- uses widgets intentionally;
- limits unnecessary recomputation.

### Needs redesign

Use this when the notebook:

- mixes side effects and core computation freely;
- ties heavy work directly to frequent input changes;
- uses state or callbacks where derived variables would suffice;
- depends on execution order habits inherited from Jupyter.

## Useful review phrases

Prefer statements like:

- This notebook is valid marimo, but not yet designed as a reactive notebook.
- The main issue is not syntax; it is the placement of recomputation boundaries.
- This parameter belongs in the UI, but the downstream computation should probably be form-triggered rather than live-reactive.
- This mutation pattern weakens marimo's dependency tracking because the runtime tracks variable definitions and references, not object mutation.

## Non-goals

This skill does not primarily cover:

- generic code style review unrelated to marimo;
- Jupyter conversion mechanics;
- deployment setup;
- batch-job parameterisation;
- deep performance profiling beyond architectural recomputation concerns.

Refer to other skills when those become the real task.
