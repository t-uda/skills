---
name: formal-proof-exposition
description: Turn formal proofs and formalisation-discovered repairs into human-readable mathematical exposition. Use when proof-assistant representations, helper lemmas or proof traces obscure the underlying argument. Recover mathematical objects and preserve genuine repairs while using the common proof-exposition guidance. Not for proving the formal development, independently verifying claims, or deciding the document's audience and purpose.
---

# Formal Proof Exposition

A formal derivation certifies a claim through a particular representation and decomposition. Neither determines the best human explanation. Recover the mathematical objects, relations, and proof idea; retain the content needed for a sound argument, not every object needed by the prover.

## Use when

- Writing a manuscript proof or explanation from checked formal code or a formal derivation.
- A formalisation has exposed a missing hypothesis, case, or justification that must be reflected in prose.
- A manuscript revision follows helper lemmas, witnesses, or tactic steps instead of explaining the mathematics.

## Boundaries and composition

Use `math-proof-exposition` for the common human-proof rules; this skill adds only the formal-to-human translation decisions and does not restate them. Use `lean-formalization-discipline` for work on Lean proofs; `math-claim-integrity` for whether the mathematical claim is established, including its inspection of the formal declarations that support a claim presented as machine-checked; `math-semantic-preservation` for source-to-prose meaning, including probability and measure context; `math-notation-consistency` for canonical names and useful abbreviations; and `exposition-flow` for the agreed audience model and reader needs.

If the common exposition skill is unavailable, do not claim its review was performed. Its absence does not justify exporting the formal trace; the translation must still preserve the source claim and expose its actual mathematical reason.

## Inputs

Obtain the formal statement and relevant proof, their checking status, the target mathematical statement, the agreed audience model and notation, and any pre-formalisation human proof. Read enough definitions to distinguish mathematical structure from its representation. Do not assume that an unverified fragment or a nearby helper proves the target theorem.

## Translation rules

**FP-1 — Compare the actual statements first.**
Identify the hypotheses and conclusion of the formal result and of the target prose. A formally checked narrower statement does not certify a broader manuscript claim. Record mismatches before polishing. Do not silently import formal assumptions into the manuscript or remove a manuscript qualification because it was implicit in a formal type.

**FP-2 — Separate a mathematical repair from a formal workaround.**
A newly needed mathematical hypothesis, boundary case, or missing inference must survive translation. But an assumption appearing in one formal implementation does not by itself prove that the original theorem needs it: it may belong to a helper, an API route, or a temporary proof strategy.

Determine what the verified argument actually establishes. If changing the target statement is necessary or unresolved, present the discrepancy and proposed repair for author decision. Do not promote a workaround into a universal theorem hypothesis by inference from code alone.

**FP-3 — Recover objects from their representations.**
Distinguish the mathematical objects from indices, quotient representatives, membership witnesses, relation constructors, coercions, implementation helpers, termination machinery, and proof terms used to access them. Write at the object level, naming mathematical abstractions rather than repeatedly unfolding predicates because the formal code does so.

Retain a representation detail when the mathematics depends on it, including well-definedness, independence of representative, compatibility, or an essential bound. Hiding a witness's name does not eliminate the obligation it discharges.

**FP-4 — Reconstruct the argument rather than shorten the trace.**
Identify which invariant, construction property, universal property, estimate, or other reason subsumes a block of formal steps. Write the human argument around that reason and its actual hypotheses. Removing intermediate lines without identifying a sufficient reason can leave an opaque or invalid proof. Preserve a repair and the step that needs it without narrating every adjacent formal obligation.

An existence argument may justify a simple mathematical configuration without making its indexing route the main narrative. Conversely, keep the route when it is the substantive construction rather than incidental representation machinery.

**FP-5 — Export repairs, not helper granularity.**
Do not automatically give every formal helper, termination measure, or witness a manuscript name, paragraph, or numbered result. Apply the common exposition rules and `math-claim-integrity`'s hierarchy criteria to decide what the reader needs. Retain helpers and measures that carry independent mathematical or explanatory value.

When a pre-existing human proof has a sound architecture, preserve it and expose the repaired step. Formalisation effort and formal dependency order are not evidence that the paper must be reorganised in the same order.

The agreed reader questions decide how much formal-specific detail appears. Do not suppress it when the readers need it: an audit or tutorial brief can require material that a findings report should omit.

## Procedure

1. Compare the formal and target statements, including live assumptions, and establish what has actually been checked.
2. Identify genuine mathematical content and repairs separately from representation and prover obligations. Keep this classification as working analysis, not a manuscript ledger.
3. Recover a human proof architecture. Use the earlier proof where sound; otherwise build an explanation around the actual mathematical mechanism.
4. Draft using `math-proof-exposition`. Restore established mathematical vocabulary and appropriate notation rather than preserving formal variable names by default.
5. Check each compressed passage against the formal obligations it replaces. Keep every essential dependency and make the use of a repaired hypothesis visible.
6. Compare the resulting prose with both source and target statements. Report any unresolved mismatch without claiming that smooth prose constitutes verification.

## Boundary examples

```text
Repair retained; scaffolding removed:
Formalising a lemma showed that its cancellation step u = v from h(u) = h(v)
needs h injective, which the original statement omitted; the author has agreed
to add that hypothesis. Keep the hypothesis and identify the cancellation step.
Auxiliary names for the equality proof need not appear in the manuscript.

Do not over-infer:
A helper happens to assume compactness, but the formal target theorem does not.
Do not add compactness to the manuscript merely because that helper was read.
```

```text
Representation hidden; obligation retained:
A quotient construction uses representatives and proves independence of their
choice. The prose may describe the induced map directly, but it must still
explain why the map is well-defined when that is not already available.
```

```text
Useful measure retained:
An explicit ranking function is the natural explanation of termination.
Keep it. The fact that a prover also uses it does not make it disposable.
```

## Output and quality check

Return the requested human proof and a concise note of genuine statement/proof repairs and unresolved discrepancies, unless the task requests only the prose. Do not append a tactic trace or a catalogue of discarded variables.

The human proof must state the same agreed claim, preserve essential hypotheses and cases, expose every genuine repair, and give recoverable reasons for compressed steps. It must not depend on knowing formal helper names, another repository's manuscript, or the writing agent's private source context. Report evidence of formal checking accurately and separately from exposition quality.
