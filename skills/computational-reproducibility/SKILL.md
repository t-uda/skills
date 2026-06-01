---
name: computational-reproducibility
description: Use when running, reviewing, or preparing computational experiments so inputs, outputs, manifests, failure states, and generated artifacts remain explicit and reproducible.
---

# Computational Reproducibility

Use this skill to keep computational experiments reproducible before expensive execution or change submission.

The goal is experimental discipline: fail early on invalid setup, keep source and generated artifacts separate, record enough identity to rerun work, and report scientific outcomes without ambiguous status labels.

## When to use

Use this skill when:

- running or modifying computational experiments
- generating reports, figures, embeddings, metrics, CSV/JSON outputs, or model results
- preparing changes that depend on experiment outputs
- reviewing scientific-computing, numerical-analysis, TDA, simulation, or AI-for-science workflows
- long-running work could fail late because inputs, paths, dependencies, or compute access were not checked

## When not to use

Do not use this skill for:

- ordinary prose edits
- purely static documentation that does not depend on generated results
- repository-specific CI, storage, gatekeeper, or runbook design
- creating manifest schemas, validators, or tooling unless the user explicitly asks
- prescribing concrete artifact directory names for a repository

## Core principles

### No implicit fallback

Missing inputs, layout mismatch, dependency absence, unavailable compute, or unavailable API access must hard-fail before execution.

Fallbacks are allowed only when all of these are true:

- the user or repository explicitly opts in
- the fallback is recorded in the manifest or run notes
- outputs clearly identify the fallback path
- review can distinguish fallback results from primary results

Do not silently substitute sample data, cached outputs, smaller models, different backends, local paths, or alternate datasets.

The same rule governs fallbacks **inside** a computation, not only at its inputs. Silently replacing a degenerate intermediate or estimator with a default is forbidden under the identical conditions (hard-fail, or explicit opt-in + recorded + visible in outputs + distinguishable in review). Examples across domains:

- zero or near-zero weight sum substituted with uniform (or any) weights
- empty collection reduced to a default constant
- zero or near-zero denominator, norm, or scale substituted with a constant
- undefined primary estimator silently swapped for an alternate estimator or method
- NaN or missing value filled with 0 (or any constant)

Judge such a fallback by **impact if triggered**, not only by whether it fires on current data. A guard that never fires now can still be scientifically catastrophic if it would — for example a substituted scale that silently yields an order-of-magnitude-wrong result with no raise. A fallback that fires on a non-trivial fraction of inputs is itself a signal that the **primary** path's definition may be wrong; investigate the spec before accepting the fallback.

### Separate source and artifacts

Keep source files and generated artifacts distinct.

Source material may belong in git:

- code
- documentation
- tests
- fixtures
- small static reference inputs intentionally used by tests

Generated artifacts stay outside git by default:

- experiment outputs
- logs
- reports
- figures
- embeddings
- metrics
- CSV/JSON result dumps
- model outputs
- temporary caches

Commit generated artifacts only when the repository explicitly treats them as source, fixtures, or reviewed deliverables.

### Manifest before execution

Create or update the run manifest before expensive execution starts.

Record the applicable identity fields:

- repository commit SHA or source revision
- command or entry point
- configuration identity
- random seed, or an explicit statement that no stochastic process is used
- input identity, including dataset version, checksum, query, or source revision when available
- output identity, including run id and expected artifact location
- execution backend
- model or service when applicable
- dependency or environment identity
- compute venue when applicable
- fallback status

If a field does not apply, record that it is not applicable rather than omitting it when omission would create ambiguity.

### Preflight gates expensive execution

Expensive execution starts only after required inputs, dependencies, identities, and compute access are validated.

### Artifact layout stays invariant-level

Use stable source/output separation and stable run identity. Concrete directory names are repository policy.

## Preflight checklist

Before launching long-running work, validate:

- required inputs exist and match the expected type
- input roots and output roots are distinct
- output location is writable and does not overwrite unrelated runs
- dependencies are installed and importable or executable
- required credentials, services, APIs, or compute venues are available when applicable
- the manifest contains enough identity to rerun or audit the run
- generated artifacts will not be written into source directories unless explicitly intended

If preflight fails, stop before execution. Do not repair by guessing paths, creating ad-hoc fallback inputs, or switching execution backends silently.

## Artifact and manifest expectations

Manifest and artifact layout must make each run auditable without prescribing repository-specific paths.

The manifest must identify source revision, command, configuration, input identity, output identity, seed status, execution backend, applicable model/service identity, environment identity, and fallback status.

### Deterministic artifact layout

Use stable source/output separation and a stable run identity. The exact directory names are repository policy; this skill only requires that:

- each run has an identifiable output location
- outputs from separate runs do not overwrite each other accidentally
- artifacts can be traced back to their manifest
- source inputs are not mixed with generated outputs
- reviewers can tell which files are source, fixtures, generated outputs, or temporary artifacts

## Failure semantics

Use distinct status terms.

- `not-run`: execution did not start.
- `skipped`: execution was intentionally bypassed for a recorded reason.
- `failed`: execution started and did not complete successfully.
- `empty-result`: execution completed, but produced no result where a result may normally exist.
- `zero-result`: execution completed and the measured value is legitimately zero.

Do not use `empty`, `failed`, or `not-run` interchangeably. If a status is uncertain, mark it as unknown and explain what evidence is missing.

## Execution discipline

When running an experiment:

1. Identify the source revision and intended inputs.
2. Define the output identity before execution.
3. Write or update the manifest.
4. Run preflight checks.
5. Execute only after preflight passes.
6. Record the final status using the failure semantics above.
7. Keep generated artifacts out of source control unless explicitly authorized.

When modifying an existing workflow, preserve stricter behaviour. Do not add silent fallback, implicit path discovery, runtime substitution for degenerate intermediates, or source/artifact conflation for convenience.

## Review checklist

Before submitting changes involving computational experiments or generated outputs, check:

- Missing inputs and dependency absence hard-fail.
- Input and output roots are not conflated.
- Generated artifacts are outside git unless explicitly authorized.
- The manifest records source revision, inputs, outputs, seed status, execution backend, and applicable model/service identity.
- Preflight checks run before expensive execution.
- Artifact layout has stable source/output separation and run identity.
- Failure states distinguish `not-run`, `skipped`, `failed`, `empty-result`, and `zero-result`.
- Any fallback is explicit, opted in, and visible in outputs or manifest.
- No silent substitution for degenerate intermediates or estimators. Preflight and manifest checks do not surface runtime numerical guards, so read the code: grep for `or <const>`, `if x <= 0: x = <const>`, `default=` in max/min/reduce, `nan_to_num`, and `nanmean`/`nanmax`/`nansum` (silent drop), and try/except blocks returning a default.
- Each fallback is judged by impact if triggered, not only by whether it fires now; a high trigger rate is treated as a flag that the primary path may be misdefined.
- Host-specific paths, credentials, and local cache assumptions are not required for reproducibility.

## Stop conditions

Stop and ask for a repository-specific decision when:

- the user wants generated artifacts committed but no repository policy authorizes it
- the workflow needs a concrete manifest schema or validator
- source and artifact roots cannot be separated without changing repository layout
- compute, API, credential, or dependency availability cannot be verified
- fallback behaviour is desired but not explicitly authorized
- failure semantics cannot be assigned from the available evidence
