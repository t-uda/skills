---
name: research-significance
description: Assess whether a mathematical or applied-mathematical research direction is locally significant — separating correctness, novelty, and scholarly value — before prose polishing or source-of-truth treatment.
---

# Research Significance

Evaluate a candidate research direction, conjecture, or cross-domain connection for scholarly significance. Exploration may be bold; evaluation must be severe. Do not promote a direction until it survives explicit per-field baseline comparison.

## Use when

Use this skill when:

- a mathematical research question, conjecture, or connection is being proposed or explored
- a cross-domain analogy might be correct but research-trivial
- the user asks whether a direction is worth pursuing
- semantic drift toward a user's known specialty (e.g. TDA, PDE, topology) is suspected
- the agent must choose one deep direction instead of cataloguing loose connections

## Do not use

Do not use this skill for:

- prose inflation, hype, or claim-evidence mismatch → use `deslop-prose`
- authority, sourcing, or trust-scope auditing of a summary artifact → use `sot-integrity`
- structural or logical integrity of a written paper → use `math-claim-integrity`
- symbol drift or notation consistency → use `math-notation-consistency`
- a complete systematic literature review
- guaranteeing novelty or replacing expert judgement

## Inputs

Gather or infer before proceeding. Ask only when missing inputs would change the verdict.

- `question` — the concrete research question or problem
- `candidate_direction` — the proposed connection, mechanism, conjecture, or theorem sketch
- `relevant_fields` — every field whose standard results must be consulted
- `sources` — literature, notes, or calculations supplied by the user
- `user_profile_context` — known specialties or prior work (use only to flag drift risk, not to justify a connection)

## Core principle

Separate **exploration** from **evaluation**.

Exploration may permit analogies and speculative bridges. Evaluation must then compare the candidate against known results and simpler alternatives in every relevant field. A connection is not a contribution until it passes that comparison.

Progression ladder:

```text
analogy
  -> candidate mechanism
  -> precise mathematical statement
  -> local significance map
  -> comparison with known results in each relevant field
  -> significance assessment
  -> retain, downgrade, or reject
```

## Procedure

### Phase 1 — Exploration

- Map plausible connections without claiming they are contributions.
- Label every step as exploratory until a precise statement exists.
- Prefer one mechanism over a catalogue of analogies.

### Phase 2 — Evaluation

Work through the five lenses below. For each lens, record pass, fail, or unresolved.

1. State or attempt a precise mathematical formulation (theorem, construction, invariant, algorithm, counterexample, or proof obligation).
2. Build the **local significance map** (required before any verdict):
   - **incumbent baseline** — what already solves or bounds the problem locally (cite `sources` or mark unverified)
   - **concrete bottleneck or gap** — the specific obstacle the candidate addresses
   - **minimum non-trivial improvement** — the smallest gain that would count as progress
   - **disqualifiers** — reformulation, profile drift, missing mechanism, or simpler route unnamed
3. For each relevant field, list what is already standard and whether the candidate adds anything beyond reformulation.
4. Apply the contribution test: does the direction yield a concrete gain (new theorem, weaker assumptions, stronger conclusions, new proof mechanism, computable method, new invariant, transfer to an uncovered case, or gap-filling synthesis)?
5. Classify evidence: source-supported, user-confirmed, derived in this analysis, model-knowledge only, or conjectural.
6. Check locality: does the direction stay centred on `question`, or did profile knowledge cause semantic drift?
7. Apply the source-sufficiency gate and deterministic verdict order below.

## Evaluation lenses

### Mathematical substance

- Is there a precise statement, construction, invariant, algorithm, counterexample, or proof obligation?
- Is the relationship stronger than metaphor or shared vocabulary?
- Are assumptions, conclusions, and implication direction explicit?

### Baseline comparison

- What is already standard in each participating field?
- Is the result trivial, immediate, or already known from either side?
- Can the same conclusion be obtained more directly without the new concept?
- Is this merely reformulation or notation change?

### Potential contribution

Does the direction plausibly provide at least one concrete gain:

- genuinely new theorem or conjecture
- weaker assumptions or stronger conclusions
- new proof or explanatory mechanism
- computable method or improved complexity
- new invariant, obstruction, classification, or counterexample
- transfer to a case not covered by existing methods
- synthesis that resolves a documented gap, not mere juxtaposition of terminology

### Evidence and uncertainty

- Which claims are supported by literature or supplied sources?
- Which depend only on model knowledge?
- Which are conjectural or unverified?
- What targeted search or calculation would decide the question?

### Locality and drift control

- Does the response remain centred on `question`?
- Is a cross-domain transition justified by a specific mathematical mechanism?
- Did `user_profile_context` motivate an irrelevant or weak connection?
- Would narrowing the question yield more than adding another domain?

## Verdict

### Source-sufficiency gate

Model recollection alone must not establish field-standard status, novelty, equivalence to known work, or a `promising` verdict.

- `promising` requires at least one source-supported baseline claim or user-supplied calculation confirming a non-trivial gain.
- `known/reformulation` requires a source-supported, user-confirmed, or explicitly derived identification of the simpler or known route.
- `derived in this analysis` may establish a mathematical identity, implication, counterexample, or equivalence when the derivation is shown.
- `derived in this analysis` must not establish literature absence, novelty, historical priority, or field-standard status.
- When a material baseline claim rests on model-knowledge only, cap the verdict at `plausible but unverified` or lower and name the deciding search.

### Decision order

The verdicts are categories, not a severity scale. Apply in order; assign the first match.

1. **`incoherent`** — precise formulation fails.
2. **`exploratory analogy only`** — no mechanism beyond metaphor or shared vocabulary (even if a loose statement exists).
3. **`known/reformulation`** — source-supported, user-confirmed, or explicitly derived equivalence to standard or simpler work.
4. **`research-poor`** — contribution test fails, and no established equivalence to standard or simpler work is available.
5. **`plausible but unverified`** — mathematically coherent and contribution plausible, but novelty, literature status, or baseline claims remain unresolved or source-insufficient.
6. **`promising`** — precise statement, contribution test passes, and source-supported or user-supplied evidence confirms a non-trivial gain.

| Verdict | Definition | Agent guidance |
|---|---|---|
| `promising` | Precise direction with an identifiable non-trivial gain | May be promoted as a research direction; state the gain and what remains to prove or verify |
| `plausible but unverified` | Mathematically coherent, but novelty or literature status unresolved | Keep; label uncertainty; name the deciding search or calculation |
| `exploratory analogy only` | Useful intuition, not yet a research claim | Do not present as a contribution; keep labelled exploratory |
| `known/reformulation` | Correct but established as standard or equivalent to known work | Downgrade; cite or derive the simpler or known route |
| `research-poor` | No concrete gain over simpler or incumbent approaches, without established equivalence | Reject as a research direction; name the missing gain or simpler path |
| `incoherent` | Does not survive precise formulation | Reject; explain the formulation failure |

Do not soften a verdict to avoid friction. Negative and downgraded outcomes are valid results.

## Required output

Produce these sections in this order.

### A. Verdict

State exactly one verdict from the table.

### B. Local significance map

State incumbent baseline, bottleneck or gap, minimum non-trivial improvement, and disqualifiers.

### C. Precise statement

Give the candidate as a precise mathematical statement, construction, or explicit failure note if formulation failed.

### D. Per-field baseline

For each field in `relevant_fields`:

- what is already standard
- whether the candidate is trivial, known, reformulation, or genuinely new from that field's perspective

### E. Contribution test

State whether the direction passes the contribution test and name the concrete gain, or explain why it fails.

### F. Evidence status

Classify each material claim as: source-supported, user-confirmed, derived in this analysis, model-knowledge only, or conjectural. Name what would close open gaps.

### G. Drift check

State whether the direction stayed local to `question` or drifted; note any profile-driven connection.

### H. Next action

Output a single final line of the form `Next action: <value>`, where `<value>` is exactly one of:

- `pursue` — develop the promising or plausible direction
- `narrow question` — refocus before adding domains
- `keep exploratory` — retain analogy only, no research claim
- `reject` — abandon this direction; name the simpler or known alternative

## Working rules

- Do not let model-memory baseline claims drive a `promising` or `known/reformulation` verdict.
- Do not use a derivation in the current analysis to assert novelty, literature absence, priority, or field-standard status.
- Do not infer scholarly significance from mathematical correctness alone.
- Do not infer novelty from unfamiliar terminology or cross-domain presentation.
- Do not present a result as non-trivial without checking every relevant field.
- Do not manufacture an application to the user's known specialty merely because it is semantically available.
- Do not conceal missing domain knowledge behind fluent exposition.
- Do not require prior publication before allowing speculation; label speculation and state what would validate it.
- Prefer one deep, falsifiable direction over a catalogue of loose connections.

## Examples

```
Cross-domain, research-trivial — Candidate advertises
c(t) = #π₀(K_t) as a new topological summary; user notes β₀(K_t) is already computed
in the filtration.

Local significance map:
- Incumbent baseline: β₀(K_t) from persistent homology (user-supplied notes).
- Bottleneck: none stated beyond relabelling an existing count.
- Minimum gain: invariant or theorem not recoverable from β₀(K_t).
- Disqualifier: c(t) = β₀(K_t) by definition once components are identified.

Verdict: known/reformulation
Contribution test: fails — no gain beyond renaming β₀(K_t).
Evidence: user-confirmed and derived in this analysis — c(t)=#π₀(K_t)=β₀(K_t)
once components are identified; no literature search is needed for the identity.
Next action: reject
```

```
Exploratory analogy — Candidate maps a PDE stability question to a Morse-theoretic
landscape without a quantitative link.

Local significance map:
- Incumbent baseline: energy method for the PDE (user notes).
- Bottleneck: uniform stability bound — mechanism not stated.
- Minimum gain: Lipschitz or spectral lemma connecting operator to Morse data.
- Disqualifier: analogy only; no correspondence lemma.

Verdict: exploratory analogy only
Evidence: coherence of the analogy is conjectural; no source supplies the link.
Next action: keep exploratory
```

```
Survives baseline (source-supported) — Candidate conjectures a lower bound on
parameter τ(G) via invariant I(G). User supplies Paper A (upper bound U) and
Paper B (related invariant with a weaker bound).

Local significance map:
- Incumbent baseline: Paper A gives upper bound U; Paper B bounds a related quantity.
- Bottleneck: documented gap between known upper and lower bounds on τ.
- Minimum gain: bound strictly below U not immediate from Paper B.
- Disqualifier: I(G) a routine transform of Paper B's invariant (unresolved).

Verdict: plausible but unverified
Per-field baseline: combinatorics — gap documented in Paper A; whether I coincides
with a standard invariant needs search.
Contribution: concrete bound target stated; novelty of I unresolved.
Next action: pursue
```

```
No gain, no established equivalence — Candidate defines a weighted variant W(G)
of an existing invariant but gives no theorem, sharper bound, or computable method;
available sources do not identify W(G) with a standard object.

Local significance map:
- Incumbent baseline: existing invariant and bounds from supplied notes.
- Bottleneck: no bottleneck named beyond changing weights.
- Minimum gain: new bound, obstruction, or algorithm not recovered from the baseline.
- Disqualifier: contribution test fails; equivalence to known work is unresolved.

Verdict: research-poor
Contribution test: fails — no concrete gain is identified.
Evidence: source-supported baseline; equivalence status remains conjectural.
Next action: reject
```

## Quality check

Before finishing, verify:

- a local significance map is recorded before verdict assignment
- source-sufficiency gate applied; no model-memory-only `promising` verdict
- verdict assigned via deterministic decision order, not subjective severity
- `known/reformulation` remains reachable before generic no-contribution rejection
- evidence provenance supports the verdict and does not use derivation for scholarly-status claims
- correctness, novelty, and significance are distinguished in the report
- every field in `relevant_fields` received baseline comparison
- the contribution test explicitly addresses reformulation and triviality
- the verdict supports negative or downgraded outcomes when warranted
- drift and profile-driven connections were checked
- the skill was applied to a concrete question, not a generic methodology essay
- examples and output are in English

## Relationship to other skills

Recommended sequence (advisory):

```text
research-significance
  -> targeted source collection / research summary
  -> sot-integrity when that summary becomes authoritative
  -> deslop-prose for the final written artifact
```

- `sot-integrity` audits whether an artifact can be trusted as authoritative; it does not judge research worthiness.
- `deslop-prose` cleans finished prose after the substantive direction is chosen.
- `math-claim-integrity` audits structural integrity of a written paper, not whether a direction is worthwhile.
