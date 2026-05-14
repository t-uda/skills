---
name: deslop-prose
description: Clean academic or professional prose that carries AI-generated residue by removing hype, decorative structure, vague metadiscourse, pseudo-technical phrasing, and claim-evidence mismatch while preserving technical meaning, qualifications, and authorial intent.
---

# Deslop Prose

Edit final or near-final prose so it says the same thing with higher signal and lower inflation.

Use this when the draft is already directionally correct but reads as generic, over-polished, over-enumerated, or AI-shaped. Do not use it for factual verification, source-of-truth adjudication, or discussion-history cleanup.

## Use when

Use this skill when:

- academic or professional prose sounds inflated, generic, or mechanically polished
- claims are broader or stronger than the evidence stated nearby
- decorative structure or metadiscourse is displacing content
- terminology sounds improvised when an established term would be clearer

## Do not use

Do not use this skill for:

- issue, PR, or prior-draft residue cleanup where the main problem is discussion provenance
- source-of-truth auditing, factual verification, or citation checking
- legal or policy text where rhetorical softening could change meaning
- drafts that still need architectural or substantive decisions

Use `deslop-history` when the artifact leaks process history, superseded alternatives, or agent-facing framing.

## Inputs

Gather or infer these before editing:

- `artifact` — the prose to clean
- `intended_reader` — who must read or act on it
- `artifact_type` — paper, memo, report, proposal, README, summary, or similar
- `technical_terms` — terms that should remain stable
- `evidence_scope` — the facts, results, citations, or qualifications that bound the claims

Ask only when rewriting could blur a technical term, scope boundary, or required qualification.

## Procedure

1. Identify the intended reader, artifact type, and evidence scope.
2. Mark sentences where style is carrying more weight than content.
3. Tighten claims so their strength matches the stated support.
4. Remove decorative structure, generic metadiscourse, and pseudo-technical inflation.
5. Rewrite with stable terminology and direct claims.
6. Check that qualifications, citations, definitions, and authorial intent still hold.

## Target Patterns

- `hype-inflation` — unsupported importance claims such as "transformative" or "pivotal"
- `enumeration-inflation` — decorative lists that imply coverage without support
- `generic-metadiscourse` — scaffolding like "It is important to note that"
- `framework-inflation` — grand labels such as "broader landscape" or "holistic framework" without a concrete framework
- `methodological-theatre` — vague rigor language where a concrete method should be named
- `vague-significance` — "valuable insights" or "important implications" without the concrete insight or implication
- `defensive-negative-framing` — "This is not X" when a positive statement would be clearer
- `unstable-terminology` — unusual paraphrases that obscure standard concepts
- `hyphen-chain-pseudo-terms` — long ad hoc compounds that sound technical without adding precision
- `formulaic-symmetry` — repeated structures like "not only X but also Y" when the contrast adds no value
- `claim-evidence-mismatch` — certainty, breadth, or importance exceeding the support in the text

## Rewrite Rules

- Prefer concrete contribution claims over broad importance claims.
- Prefer one supported dimension over a long decorative list.
- Start with the claim, not the sentence-level announcement of the claim.
- Name the actual method, evidence, dataset, theorem, metric, proof step, or procedure when known.
- Preserve necessary hedging, qualifications, citations, notation, and scope boundaries.
- Preserve established technical terms; do not paraphrase for freshness.
- Rewrite long ad hoc hyphenated compounds as ordinary noun phrases unless the compound is standard.
- Keep negative framing only when it prevents a likely misuse.
- Do not turn precise prose into smooth but lower-density prose.

Minimal examples:

```text
Before: This transformative framework provides valuable insights into a broad landscape of practical applications.
After: This framework identifies the practical conditions under which the method applies.
```

```text
Before: We systematically and rigorously analyse the method across efficiency, scalability, robustness, interpretability, and applicability.
After: We evaluate runtime and robustness on the reported benchmarks.
```

## Output

If the user asks to edit a file, apply the rewrite directly. If the user asks for cleanup text only, return the revised prose without an audit log.

When the user asks for review before editing, provide:

- the inferred reader and artifact type
- the main inflation patterns present
- the cleaned prose

When editing repository files:

- modify only the target artifact or directly required index entries
- keep the diff focused on prose cleanup guidance
- do not introduce style taxonomies beyond what the artifact needs

## Quality Check

Before finishing, verify:

- the claim strength matches the evidence actually present
- decorative enumeration and generic metadiscourse are gone
- technical meaning, qualifications, and terminology remain intact
- the prose sounds more direct, not more impressive
- `deslop-history` would not be the more appropriate skill

## Relationship to Other Skills

- Use `deslop-history` when the main problem is discussion provenance, prior-draft residue, or process framing.
- Use `sot-integrity` when authority, factual grounding, or trust scope must be audited.
- Use `textlint-cli` for deterministic lint checks, not context-sensitive prose judgment.
