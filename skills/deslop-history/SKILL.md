---
name: deslop-history
description: Clean final user-visible artifacts produced from accepted decisions, reviewed direction, or issue/PR discussion by removing non-essential historical context, discussion provenance, superseded alternatives, and process framing while preserving current decisions, contracts, constraints, operational rationale, and required compatibility notes.
---

# Deslop History

Edit a final artifact draft so it reads as direct, user-facing material for its intended reader.

Use this as a last pass after the governing decision or direction has converged. Do not use it to decide policy, revise architecture, or adjudicate open design questions.

## Use when

Use this skill when:

- a final user-visible artifact needs cleanup before sharing, committing, or handing off
- a source-of-truth doc, decision note, ADR-like note, implementation plan, summary, or skill was derived from issue or PR discussion
- accepted decisions are mixed with provenance, superseded alternatives, prior-draft commentary, or agent-facing explanation
- the artifact should present the current decision, boundary, contract, or instruction set rather than how it was reached

## Do not use

Do not use this skill for:

- historical records, changelogs, postmortems, or audit artifacts where history is required content
- unresolved design discussions
- legal, regulatory, or compliance material where provenance must be preserved

Do not remove:

- compatibility, migration, or deprecation notes that affect current behaviour
- rationale needed to understand decision boundaries or prevent misimplementation

## Inputs

Gather or infer these before editing:

- `artifact` — the text or file to clean
- `intended_reader` — who must use the final output
- `artifact_type` — doc, plan, summary, skill, source-of-truth note, ADR-like note, or other form
- `required_history` — any historical context the artifact type explicitly requires
- `current_authority` — the accepted decision, issue, PR, spec, or source that governs the current state

Ask only when removing history could destroy required provenance or a needed operational caveat.

## Procedure

1. Identify the intended reader and artifact type.
2. Determine whether the artifact type requires historical context.
3. Classify each paragraph, bullet, table row, or section.
4. Delete residue unless the artifact type explicitly requires it.
5. Rewrite retained content so it reads as direct final-form guidance.
6. Check that the cleaned artifact still preserves the current decision, contract, responsibility split, assumptions, constraints, and operational rationale.

## Classification

Use these categories.

- `current-state-essential` — current decisions, interfaces, contracts, responsibility splits, active constraints, active assumptions, and operational open issues
- `operational-rationale` — rationale still needed to prevent misimplementation or misuse
- `historical-meta-residue` — discussion provenance, superseded alternatives, prior drafts, process notes, defensive explanations, and agent-facing framing
- `nonessential-context` — background that may be interesting but does not change the reader's action

Keep `current-state-essential`.
Keep `operational-rationale`, but compress it and write it in present-state terms.
Remove `historical-meta-residue` and `nonessential-context` unless the artifact type requires them.
Do not output the classification unless the user explicitly asks for a review trace.

## Removal Heuristics

Candidates for deletion or rewriting include:

- "This was discussed in ..."
- "After issue discussion ..."
- "This supersedes ..."
- "The earlier direction ..."
- "The first pass ..."
- "The initial draft ..."
- "This note exists because ..."
- "We considered ..."
- "In review ..."
- "For now" when it reflects discussion timing rather than a real boundary
- migration or backward-compatibility framing with no current operational effect

Candidates for retention include:

- active constraints that still shape implementation or use
- current interfaces, contracts, and responsibility boundaries
- compatibility requirements that affect actual behaviour
- open issue links that define unresolved operational boundaries
- rationale that prevents a likely wrong implementation
- dates, versions, or commit references when freshness or compatibility matters

## Rewrite Rules

- Prefer present-tense, authoritative descriptions.
- Replace provenance with direct current-state wording.
- Replace "This supersedes X" with "Use Y" unless readers must actively avoid X.
- Remove defensive framing about why the artifact exists.
- Remove agent-facing process commentary from user-facing outputs.
- Keep caveats that affect execution, but make them operational.
- Preserve links only when they define current authority, unresolved boundaries, or required follow-up.
- Do not introduce new decisions, broaden scope, or erase active constraints.

Minimal examples:

```text
Before: After issue discussion, we decided the skill should preserve compatibility notes when needed.
After: Preserve compatibility notes when they affect current behaviour.
```

```text
Before: This supersedes the earlier direction to include the full discussion.
After: Include only current decisions and operational constraints.
```

## Output

If the user asks to edit a file, apply the cleaned artifact directly. If the user asks for review or cleanup text only, return the cleaned artifact without an audit log.

When the user asks for review before editing, provide:

- the inferred reader and artifact type
- any history that must be retained
- the cleaned artifact

When editing repository files:

- modify only the target artifact or directly required index entries
- keep the diff focused on residue removal and final-form wording
- do not add historical commentary about the cleanup itself

## Quality Check

Before finishing, verify:

- the target reader can see the current decision, contract, or instruction set without reading issue history
- remaining historical text changes present action or is required by the artifact type
- discussion provenance, superseded alternatives, and prior-draft commentary are absent unless required by the artifact type
- deleting removed text cannot cause likely misimplementation
- the artifact reads as if written directly in final form
- open issue references remain only when operationally useful

## Relationship to Other Skills

- Use `sot-integrity` when the artifact's authority or factual grounding must be audited.
- Use `metaplan` when a plan or spec still needs execution-readiness review.
- Use `handoff-prompt` when the output is a transfer prompt for another agent.
