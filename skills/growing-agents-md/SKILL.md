---
name: growing-agents-md
description: Create a compact AGENTS.md when missing, or refine an existing AGENTS.md so it stays short, current, and useful for implementation agents. Use this when the user explicitly asks for a growing, compact AGENTS.md or wants to create or maintain AGENTS.md without letting it bloat.
---

# Growing AGENTS.md

Maintain a compact, high-signal `AGENTS.md` for the current repository.

This skill has exactly two jobs:

1. **If `AGENTS.md` does not exist:** create a minimal, high-quality one.
2. **If `AGENTS.md` already exists:** refine it so it remains compact, current, and implementation-useful.

The goal is **not** to accumulate notes.  
The goal is to keep `AGENTS.md` **short, project-specific, and operationally valuable**.

## Core policy

Treat `AGENTS.md` as a **living, bounded document**.

Always optimise for these properties:

- Short enough to read quickly
- Specific to this repository
- Useful to an implementation agent with no prior context
- Free from stale, redundant, or inferable content

When updating an existing file, **prune first**.  
Do not default to appending.

## What belongs in AGENTS.md

Include only information that satisfies most of the following:

- It is **project-specific**
- It is **not easily inferable** from code, config, or standard conventions
- It helps an agent begin or continue implementation without unnecessary clarification
- Getting it wrong would cause wasted work, confusion, or bad changes
- It is stable enough to deserve placement in a persistent repository instruction file

Good candidates include:

- Repository-specific workflow constraints
- Important architectural boundaries that are not obvious from local code inspection
- Non-obvious conventions actually used in this project
- High-value entry points for build, test, or validation
- Strong project preferences that materially affect implementation choices

## What does not belong in AGENTS.md

Do **not** include:

- Generic programming advice
- Restatements of what the code already makes obvious
- Large command inventories
- Historical notes
- Temporary task-specific reminders
- Long explanations
- Speculation
- Catch-all sections such as `Notes`, `Misc`, `Context`, or `Other`

If information is volatile, detailed, or better represented elsewhere, keep it in code, scripts, config, or dedicated docs instead.

## Editing rules

When `AGENTS.md` exists, perform these operations in this order:

1. Remove stale items
2. Remove redundant items
3. Compress verbose items
4. Merge overlapping items
5. Rewrite unclear items
6. Add only truly missing, high-value items

Prefer **rewriting the whole file coherently** over incrementally appending text.

## Size discipline

Aim for a compact document.

Target:
- roughly 20 to 30 lines when possible
- brief sections
- terse bullets
- no paragraph that exists only for explanation

If forced to choose, omit lower-value detail rather than exceed the signal budget.

## Recommended structure

Use a minimal structure like this when creating or rewriting:

- Purpose or scope
- Key workflow rules
- Project-specific implementation guidance
- Validation or completion checks
- Maintenance note

Do not mechanically preserve an existing structure if it causes bloat.

## Maintenance note policy

A short maintenance note is allowed, but it must stay short.

It should reinforce rules such as:

- keep this file lean
- delete inferable content
- rewrite stale guidance
- prefer stable rules over volatile facts

Do not let the maintenance note become a manifesto.

## Procedure

### Case 1: AGENTS.md is missing

Create a new `AGENTS.md` that:

- is minimal
- reflects the actual repository
- avoids placeholders unless unavoidable
- includes only high-value project guidance

Do not invent repository facts.  
If repository evidence is insufficient, keep the file narrower rather than padding it.

### Case 2: AGENTS.md exists

Review the file critically.

For each existing item, ask:

- Is this still current?
- Is this project-specific?
- Is this non-inferable?
- Is this worth permanent space?
- Can this be shortened?
- Should this be merged or deleted?

Then rewrite the file into a cleaner compact version.

## Decision standard

Every retained line should justify its existence.

A line should usually survive only if removing it would make a competent implementation agent materially more likely to misunderstand the repository, violate a local convention, or pause for clarification.

## Output requirements

When performing this skill:

- Produce the resulting `AGENTS.md`
- Keep wording direct and compact
- Prefer imperative phrasing
- Avoid motivational language
- Avoid verbosity
- Avoid duplication

If useful, briefly summarise the main changes as:

- removed
- compressed
- added

But the primary output is the improved `AGENTS.md` itself.
