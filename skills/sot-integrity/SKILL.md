---
name: sot-integrity
description: Audit a source-of-truth artifact for authority, evidentiary grounding, trust scope, and conflict with repository reality before implementation or orchestration relies on it.
---

# SoT Integrity

Review a candidate source-of-truth (SoT) artifact from the perspective of an autonomous coding agent or orchestrator that will rely on it without re-investigating its claims.

Treat SoT as a governed authority layer. A document does not become trustworthy because it is labelled "source of truth". Verify, do not assume.

## When to use

Use this skill when:

- a spec, plan, policy doc, AGENTS.md, or research summary is being treated as authoritative
- implementation is about to start and depends on SoT correctness
- a harness workflow uses docs to avoid repeated source inspection
- SoT, code, and upstream reality may have drifted apart
- an orchestrator must know what child agents may trust without re-investigating
- a project is explicitly SoT-centric and factual drift would be costly

Do not use this skill for:

- generic prose or style review
- broad factual research unrelated to a specific candidate SoT
- planning-readiness review (use `metaplan`)
- compact repository guidance maintenance (use `growing-agents-md`)

## Inputs

Gather before proceeding. Ask the user for any that are missing.

- `artifact` — path or content of the candidate SoT
- `scope` — the decision area the artifact is claimed to govern
- `consumers` — who or what will rely on it (agent, orchestrator, human reviewer)
- `companion_sources` — code paths, configs, upstream docs, or other artifacts that the SoT should agree with
- `prior_status` — any previous verdict or known concerns

## Primary question

Always evaluate the artifact against this question:

> Could a downstream agent rely on this SoT, within its stated scope, without re-investigating its claims and without producing implementation that diverges from repository reality or upstream truth?

If the answer is not clearly yes, locate the cause and produce concrete repair edits.

## Review lens

Assess the artifact through these five lenses.

### 1. Authority quality

- Is this artifact actually the governing document for the stated scope?
- Is its authoritativeness explicit or only implied?
- Is precedence against other artifacts (spec, plan, AGENTS.md, README, issue text, code comments) stated?
- Does the artifact say what overrides it and what it overrides?

### 2. Source quality

- Are factual claims grounded in primary or official sources?
- Are summaries faithful to those sources?
- Are assumptions or guesses presented as facts?
- Are links present but conclusions still inadequately extracted?
- Are version, date, or commit references attached where freshness matters?

### 3. Scope of trust

- Which sections are safe to trust without re-checking?
- Which sections are provisional, underspecified, stale, or unresolved?
- Is the trust boundary explicit enough for an autonomous agent to honour?
- Does the artifact mark gaps rather than hide them?

### 4. Conflict detection

- Does the SoT disagree with code, tests, config, repository behaviour, upstream sources, or other docs?
- Is each conflict acknowledged in the artifact itself?
- Does the artifact say what to do when document and reality diverge?
- If code matches reality but contradicts a broken SoT, name this as a source-governance failure, not a code bug.

### 5. Actionability under failure

- If the SoT is broken, should implementation stop?
- Should the artifact be downgraded from SoT to background context?
- Should agents follow repository reality temporarily while a repair task is opened?
- Is the next safe action explicit?

## Claim classification

Push the artifact toward classifying every material claim as one of:

- `settled-authoritative` — backed by primary source or governing authority; safe to trust
- `local-decision` — project decision, recorded with rationale; safe to trust within project
- `provisional` — working assumption, not yet verified; trust only with caveat
- `open-question` — known to be unresolved; agents must not invent answers
- `known-conflict` — disagreement with code or other source explicitly recorded

If the artifact cannot be read this way, recommend edits that make each claim classifiable.

## Verdict

Choose one verdict.

| Verdict | Definition | Agent guidance |
|---|---|---|
| `TRUSTED` | All claims are well-sourced, internally consistent, and aligned with repository reality. No conflicts detected. | Agents may rely on the SoT without re-investigation within its stated scope. |
| `TRUSTED_WITH_GAPS` | Core claims are sound but some areas are underspecified, provisional, or not yet verified. No active conflicts. | Agents may rely on trusted sections. Gaps must be flagged; agents must not invent answers for gap areas. |
| `CONFLICTED` | The SoT contradicts repository reality, code, other docs, or upstream sources in at least one material way, but the conflict is bounded. | Agents must not proceed in conflicted areas without explicit resolution. Non-conflicted sections may still be trusted. |
| `BROKEN` | The SoT contains major factual errors, multiple conflicts, or is so stale that relying on it would produce incorrect implementation. | Agents must stop. The SoT must be repaired or downgraded to background context before implementation continues. |

Use the strictest verdict that fits. Do not soften a verdict to avoid friction.

## Required output

Produce these sections in this order.

### A. Verdict

State exactly one of: `TRUSTED`, `TRUSTED_WITH_GAPS`, `CONFLICTED`, `BROKEN`.

### B. Trust scope

State what is and is not covered by the artifact:

- decision areas the SoT governs
- decision areas it does not govern
- precedence against other artifacts when relevant

### C. Critical evidence gaps

List claims that lack adequate sourcing or verification. For each:

- the claim
- what evidence is missing
- what would close the gap

If none, say so.

### D. Conflicts found

List concrete divergences between the SoT and code, tests, config, other docs, or upstream sources. For each:

- where the SoT says one thing (quote or location)
- where reality says another (file path, commit, link)
- material impact on implementation

If none, say so.

### E. Minimal repair edits

Propose the smallest concrete edits that move the artifact toward `TRUSTED`. Prefer:

- **Replace with**
- **Add**
- **Delete**
- **Mark as provisional**
- **Mark as open question**
- **Downgrade to background context**

Write edits so the user can paste them in directly.

### F. Execution guidance

Tell downstream agents how to behave with this artifact in its current state:

- which sections may be trusted as-is
- which sections require re-checking against named sources
- what to do if reality and SoT disagree during implementation
- whether new factual claims require re-running this review

### G. Next action

End with exactly one of:

- proceed: implementation may rely on the SoT within stated scope
- proceed with caveats: implementation may proceed only in trusted sections; flag gaps to user
- repair SoT before implementation
- downgrade artifact from SoT to background context, then re-plan
- stop: escalate to user; SoT is broken and no safe partial use exists

## Working rules

- Be rigorous and unsentimental. Do not soften verdicts to avoid friction.
- Verify against companion sources where they were provided. Do not approve on text alone.
- When the artifact and code disagree and code matches reality, name this as a source-governance failure, not a code bug.
- Prefer concrete edits over advice.
- Do not invent missing facts. If a claim cannot be verified from available sources, mark it as a gap or open question rather than asserting it.
- Do not restate repository-wide guidance that already lives elsewhere. Reference it.
- Do not produce vague prose-only feedback. Always emit the verdict structure.

## Relationship to other skills

This skill complements but does not replace:

- `metaplan` — execution-readiness review of specs and plans
- `growing-agents-md` — compact repository guidance maintenance
- `handoff-prompt` — minimal transfer prompt generation

Recommended sequence (advisory, not enforced): verify SoT integrity → harden plans → hand off or orchestrate.
