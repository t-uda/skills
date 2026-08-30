---
name: sot-integrity
description: Audit a source-of-truth artifact for authority, evidentiary grounding, trust scope, and conflict with repository reality before implementation or orchestration relies on it.
---

# SoT Integrity

Review a candidate source-of-truth (SoT) artifact as the autonomous agent or orchestrator that must rely on it without re-investigating its claims.

A document is not trustworthy because it is labelled "source of truth". Verify, do not assume.

## Use when

- a spec, plan, policy doc, AGENTS.md, or research summary is being treated as authoritative
- implementation is about to start and depends on SoT correctness
- a harness workflow uses docs to avoid repeated source inspection
- SoT, code, and upstream reality may have drifted apart
- an orchestrator must know what child agents may trust without re-investigating
- a project is explicitly SoT-centric and factual drift would be costly

Do not use this skill for generic prose/style review, broad research unrelated to a specific candidate SoT, planning-readiness review (`metaplan`), or compact repository guidance maintenance (`growing-agents-md`).

## Responsibility boundary

`sot-integrity` audits whether the artifact itself is trustworthy — grounded, unconflicted, and honest about its own gaps, within its stated scope.

- `metaplan` checks whether a *plan* names its governing SoT artifact, that artifact's authority, and precedence against other artifacts — it does not re-derive the trust model here.
- When `metaplan` finds that trust or conflict in a named SoT is material to execution readiness, `sot-integrity` runs on that artifact and returns one of the verdicts below.
- When scholarly references are material, delegate bibliographic identity, metadata, version, and citation-representation checks to `bib-integrity`; consume unresolved or invalid records as Source grounding evidence, while retaining responsibility for whether each source actually supports the SoT claim.
- `sot-integrity` does not judge execution readiness, task decomposition, or research worthiness (`metaplan`, `research-significance`).

## Inputs

Gather before proceeding; ask the user for any that are missing.

- `artifact` — path or content of the candidate SoT
- `scope` — the decision area the artifact is claimed to govern
- `consumers` — who or what will rely on it (agent, orchestrator, human reviewer)
- `companion_sources` — code paths, configs, upstream docs, or other artifacts the SoT should agree with
- `prior_status` — any previous verdict or known concerns

If `scope` or `companion_sources` needed to judge materiality are missing, do not guess a verdict — request them, or cap the read at `TRUSTED_WITH_GAPS` per the Boundary Cases below.

## Primary question

```text
Could a downstream agent rely on this SoT, within its stated scope, without re-investigating its claims and without producing implementation that diverges from repository reality or upstream truth?
```

If the answer is not clearly yes, locate the cause and produce concrete repair edits.

## Audit dimensions

Evaluate each dimension once. Output sections reference these findings instead of restating them.

### Authority & precedence

- Is this artifact actually the governing document for `scope`, and is that explicit rather than implied?
- Is precedence against other artifacts (spec, plan, AGENTS.md, README, issue text, code comments) stated — what overrides it, what it overrides?

### Source grounding

- Are factual claims backed by primary or official sources, faithfully summarized?
- Are assumptions or guesses presented as settled fact?
- Are version, date, or commit references attached where freshness is material?

### Trust scope

- Which sections are safe to rely on without re-checking, and which are provisional, stale, underspecified, or unresolved?
- Does the artifact mark its own gaps, or hide them?

### Conflict detection

- Does the SoT disagree with `companion_sources` (code, tests, config, upstream sources, other docs)?
- Is each conflict acknowledged in the artifact, with a stated resolution path?
- If code matches reality but contradicts a broken SoT, record this as a source-governance failure, not a code bug.

## Claim classification

Push the artifact toward classifying every material claim as one of:

- `settled-authoritative` — backed by primary source or governing authority; safe to trust
- `local-decision` — project decision, recorded with rationale; safe to trust within project
- `provisional` — working assumption, not yet verified; trust only with caveat
- `open-question` — known to be unresolved; agents must not invent answers
- `known-conflict` — disagreement with code or other source explicitly recorded

If the artifact cannot be read this way, recommend edits that make each claim classifiable.

## Verdict

A conflict or gap is **material** when it can change what a downstream agent implements, validates, or authorizes within `scope`. Cosmetic wording, resolved cross-references, and out-of-scope trivia are not material and do not affect the verdict.

### Decision order

The verdicts are categories, not a severity scale. Apply in order; assign the first match. Evaluate `BROKEN` and `CONFLICTED` before ever considering `TRUSTED_WITH_GAPS` — a document with both a material conflict and unrelated gaps is `CONFLICTED`, never `TRUSTED_WITH_GAPS`.

1. **`BROKEN`** — no safe bounded reliance remains: material conflicts, errors, or staleness are pervasive, or a single conflict undermines the artifact's core authority claim, so no section can be trusted without independent re-verification.
2. **`CONFLICTED`** — at least one material, bounded conflict exists against `companion_sources`, but sections outside its blast radius remain independently usable.
3. **`TRUSTED_WITH_GAPS`** — no active material conflict; bounded areas remain provisional, unresolved, or unverified.
4. **`TRUSTED`** — every material claim in scope is adequately grounded, internally consistent, and aligned with repository reality; no material conflict and no material gap remain.

| Verdict | Agent guidance |
|---|---|
| `TRUSTED` | Rely on the SoT without re-investigation within its stated scope. |
| `TRUSTED_WITH_GAPS` | Rely on trusted sections; flag gaps; do not invent answers for gap areas. |
| `CONFLICTED` | Do not proceed in conflicted areas without explicit resolution; non-conflicted sections may still be trusted. |
| `BROKEN` | Stop. Repair the SoT or downgrade it to background context before implementation continues. |

## Required output

Produce these sections in this order.

### A. Verdict

State exactly one of: `TRUSTED`, `TRUSTED_WITH_GAPS`, `CONFLICTED`, `BROKEN`.

### B. Trust scope

From Authority & precedence and Trust scope findings: decision areas the SoT governs, decision areas it does not, and precedence against other artifacts when relevant.

### C. Critical evidence gaps

From Source grounding and Trust scope findings, list each material gap: the claim, what evidence is missing, what would close it. Write `None` if there are none.

### D. Conflicts found

From Conflict detection findings, list each material conflict: where the SoT says one thing (quote or location), where reality says another (file path, commit, link), and the material impact on implementation. Write `None` if there are none.

### E. Minimal repair edits

Propose the smallest concrete edits that move the artifact toward `TRUSTED`. Prefer one of:

- **Replace with**
- **Add**
- **Delete**
- **Mark as provisional**
- **Mark as open question**
- **Downgrade to background context**

Write edits so the user can paste them in directly. If no repair edits are needed, write `None`.

### F. Execution guidance

Tell downstream agents how to behave with this artifact in its current state: which sections may be trusted as-is, which require re-checking against named sources, what to do if reality and SoT disagree during implementation, and whether new factual claims require re-running this review.

### G. Next action

Output a single final line of the form `Next action: <value>`, where `<value>` is exactly one of:

- `proceed` — implementation may rely on the SoT within stated scope
- `proceed with caveats` — implementation may proceed only in trusted sections; flag gaps to user
- `repair SoT before implementation`
- `downgrade artifact from SoT to background context, then re-plan`
- `stop` — escalate to user; SoT is broken and no safe partial use exists

Choose the value consistent with the verdict: `TRUSTED` → `proceed`; `TRUSTED_WITH_GAPS` → `proceed with caveats`; `CONFLICTED` → `repair SoT before implementation`, or the downgrade action when repair is not worthwhile; `BROKEN` → `stop`, or the downgrade action when downgrading restores a safe planning basis.

## Boundary Cases

- `TRUSTED`: every claim is sourced or a recorded local decision; no gaps, no conflicts.
- `TRUSTED_WITH_GAPS`: one section is marked provisional pending an upstream release; no conflict exists.
- `CONFLICTED`: the SoT names a deprecated command as current; every other section remains accurate and usable.
- `BROKEN`: most factual claims conflict with current repository state, or the one claim the rest of the document depends on is wrong.
- `TRUSTED` / `TRUSTED_WITH_GAPS` boundary: any material claim not yet grounded — however small — forces `TRUSTED_WITH_GAPS`; there is no rounding up.
- `TRUSTED_WITH_GAPS` / `CONFLICTED` boundary: an unresolved gap stays `TRUSTED_WITH_GAPS` until it is confirmed to disagree with a companion source, at which point it becomes a conflict.
- `CONFLICTED` / `BROKEN` boundary: `CONFLICTED` holds while at least one section outside the conflict's blast radius stays independently reliable; once the conflict undermines the artifact's core authority claim or spans all in-scope sections, it is `BROKEN`.
- Mixed gaps+conflicts: a document with both a material conflict and unrelated gaps is `CONFLICTED` — apply Decision order top-down; never pick the softer verdict because gaps also exist.
- Insufficient information: if `scope` or `companion_sources` needed to judge materiality are missing, request them; if a provisional read is unavoidable, cap the verdict at `TRUSTED_WITH_GAPS` and name the missing input itself as a gap.
- Enum formatting: the final line copies the verdict-consistent value from `G` character-for-character — for example, a `TRUSTED_WITH_GAPS` audit ends `Next action: proceed with caveats` — with no leading bullet, numbering, or trailing commentary.

## Working rules

- Be rigorous and unsentimental; do not soften a verdict to avoid friction or average conflicting signals into a gentler one.
- Verify against `companion_sources` where provided. Do not approve on text alone.
- Do not invent missing facts. Mark unverifiable claims as a gap or open question.
- Do not restate repository-wide guidance that already lives elsewhere; reference it.
- Always emit the full verdict structure — never vague prose-only feedback.

## Quality check

Before finishing, verify: the verdict came from Decision order top-down (not overall impression); `BROKEN`/`CONFLICTED` were ruled out before `TRUSTED_WITH_GAPS`/`TRUSTED`; a mixed gaps+conflict input resolved to `CONFLICTED` or `BROKEN`, never `TRUSTED_WITH_GAPS`; C/D say `None` explicitly when empty; `G` matches the verdict row above.

## Relationship to other skills

This skill complements but does not replace:

- `metaplan` — execution-readiness review of specs and plans; see Responsibility boundary above
- `bib-integrity` — scholarly bibliographic-record verification; use its findings as Source grounding evidence while `sot-integrity` retains claim/source faithfulness and artifact-level verdicts
- `growing-agents-md` — compact repository guidance maintenance
- `handoff-prompt` — minimal transfer prompt generation

Recommended sequence (advisory, not enforced): verify SoT integrity → harden plans → hand off or orchestrate.
