---
name: exposition-flow
description: Turn repository-grounded source material into a self-contained, audience-admissible document or presentation by modelling the intended audience, extracting information units with explicit discourse roles, and enforcing dependency-ordered exposition in which every load-bearing statement follows the prerequisites needed to interpret it — without factual verification or citation checking (use sot-integrity), prose polishing (use deslop-prose), mathematical-correctness review (use the mathematical-writing skills), or typography and slide layout.
---

# Exposition Flow

Transform source context into audience-admissible context. The skill treats the target artifact as a dependency graph of information units and enforces one central invariant: **every load-bearing statement appears only after the reader has been given the concepts, terms, assumptions, and prior claims required to interpret it.** It is field-agnostic and applies to reports, explanations, lecture notes, slide decks, external documentation, and summaries in any language.

## Design intent

Agents that build repository-wide context — files, history, issue and PR discussion — later write audience-facing artifacts as though the reader shares that context: repository-local terms appear undefined, coined terminology is used as if standard, claims precede the concepts needed to understand them, and definitions, claims, reasons, examples, and limitations flatten into visually similar fragments. Neighbouring skills clean prose, provenance residue, and correctness, but none forces a full forward-flow audit from the intended audience's knowledge boundary. This skill owns that audit and the reordering and rewriting it requires. The audience boundary applies even when the intended reader is the repository owner: ownership does not imply the reader has reconstructed the context the agent accumulated.

## Use when

- Creating an external report, explanation, lecture note, slide deck, documentation page, or summary from repository files, notes, or issue/PR discussion
- An audience-facing artifact opens with repository-local component names, acronyms, or coined abstractions and discusses them without introduction
- Results or claims are stated before the notation, concepts, or assumptions they depend on
- A contribution list or summary consists of bare noun phrases whose discourse role (definition, claim, decision, result) cannot be determined
- An artifact must be compressed under a page, slide, word, or speaking-time budget without breaking the reader's ability to follow retained claims
- An artifact that already passed correctness and style review still fails when read forward from the audience's entry point

## Do not use

- For sentence-level rhetorical inflation, hype, or metadiscourse in near-final prose → use `deslop-prose` (run it after this skill)
- For removing discussion provenance or process residue from a final artifact → use `deslop-history` (this skill consumes history as source material but does not own residue cleanup)
- For auditing the authority or evidentiary grounding of the source material itself → use `sot-integrity` (verify the source first; this skill decides how verified material is introduced to the audience)
- For quantifier scope, theorem hierarchy, or proof honesty → use `math-claim-integrity`; for notation bookkeeping → use `math-notation-consistency`; for Japanese mathematical language → use `wabun-math-style`
- For factual verification, citation checking, controlled-vocabulary design, typography, line breaking, visual layout, or slide rendering — out of scope entirely

## Inputs

- `source_material` — repository files, notes, issue/PR discussion, research artifacts, or other source context
- `artifact_type` — report, explanation, lecture note, slide deck, external documentation, summary, or similar
- `intended_audience` — the expected background and purpose of the readers or listeners
- `communication_goal` — what the audience should understand, decide, or be able to do
- `allowed_prerequisites` — concepts that may safely be assumed without explanation
- `terminology_sot` — canonical terminology or glossary, when supplied (optional)
- `length_or_time_budget` — page, slide, word, or speaking-time constraint (optional)

Gather or infer missing inputs before restructuring; state the inferred audience model explicitly so the user can correct it. Repository ownership or familiarity is never evidence that the intended audience knows repository-local concepts.

## Rule classification and severity

Each rule is tagged with a classification that sets a default severity: **invariant** — a violation breaks the reader's ability to interpret a load-bearing statement — defaults to BLOCKING; **convention** — a strong norm with bounded exceptions — defaults to MINOR, escalating to BLOCKING per the rule's own condition; **heuristic** — a review trigger requiring contextual judgement — defaults to ADVISORY. A rule's own text overrides this default where it states a severity explicitly. When a defect triggers more than one rule, report each tag; the defect's severity for gating purposes is the maximum across triggered findings (BLOCKING > MINOR > ADVISORY > NOTE).

## Procedure

1. **Model the audience.** From `intended_audience`, `communication_goal`, and `allowed_prerequisites`, state what may be assumed. Everything else requires introduction, explanation, or omission.
2. **Extract information units.** From the source material and target artifact, identify terms, concepts, notation, assumptions, constructions, claims, reasons or proofs, examples, caveats, limitations, and open questions.
3. **Assign discourse roles.** Classify each load-bearing unit as a definition or explanation, claim, justification, example, consequence, limitation, or outlook. A fragment whose role cannot be determined must be rewritten or removed.
4. **Build prerequisite edges.** Add an edge `A -> B` when understanding or evaluating `B` requires `A` — because `B` uses a term, notation, or assumption introduced by `A` (definitional), or because the reader must see why `B` follows from `A` (explanatory or derivational). Repository file order, commit order, and implementation order must not override this dependency order. An edge whose source unit is absent from the artifact marks an omitted prerequisite branch: add the missing unit or remove its dependents.
5. **Resolve cycles.** Merge mutually dependent concepts into an explicit simultaneous-definition block, or introduce a provisional informal explanation before the formal definitions. Do not silently leave cyclic dependencies in the exposition.
6. **Topologically order the material.** Present prerequisites before dependent concepts and claims. Reintroduce context after a long gap when local recoverability has been lost. Correct global order is not sufficient: adjacent units joined by an unexplained jump need a local bridge stating why one leads to the next.
7. **Rewrite for self-containment.** Replace repository-local shorthand with standard terminology or direct explanation. Introduce a local technical term only when repeated reference genuinely requires it, and define it explicitly at first use.
8. **Audit the final flow.** Perform a strict forward read: starting with only the allowed prerequisites, verify for every load-bearing sentence or slide that the reader can identify what is being defined or asserted, what prior information it depends on, why it is present, and whether it is established, illustrative, conditional, or unresolved.

## Rules

**EF-1 — Audience boundary.** *(invariant)*
Repository knowledge is source material, not audience knowledge. Internal names, architecture labels, issue shorthand, acronyms, and coined abstractions are unknown unless explicitly included in `allowed_prerequisites`. The artifact includes only the source detail needed for the communication goal; provenance, formalisation status, and repository metadata may remain in a sidecar source-of-truth artifact instead of the audience-facing artifact.

**EF-2 — Define or explain before use.** *(invariant)*
Every nonstandard term, symbol, abbreviation, relation, or local concept used in a load-bearing statement must be introduced beforehand. A glossary elsewhere in the repository is not sufficient unless the audience-facing artifact explicitly points to it and may reasonably require the audience to consult it. A term may be introduced informally before formal treatment when the text makes that provisional role clear.

**EF-3 — No unexplained coinages.** *(convention)*
Prefer established terminology. Replace repository-local or improvised terms with ordinary descriptive language when possible. Permit a new local term only when it denotes a genuinely recurring concept, has a precise definition, and reduces rather than increases cognitive load. A terminology SoT controls canonical wording within its scope but does not by itself make a term known to the audience. Severity: MINOR; BLOCKING when the coined term carries a load-bearing statement the audience cannot interpret.

**EF-4 — Complete load-bearing statements.** *(convention)*
Definitions, hypotheses, conclusions, causal relations, limitations, and central claims must be expressed as complete propositions or complete explanatory sentences. Headings, labels, and compact list items may be fragments when their role is visually and contextually unambiguous. Severity: BLOCKING when a noun-phrase fragment leaves the reader unable to distinguish a definition, claim, evidence item, instruction, or topic label; no finding for unambiguous compact labels.

**EF-5 — Discourse-role separation.** *(convention)*
Definitions or explanatory introductions, claims, reasons or proofs, examples, consequences, and limitations must be distinguishable by wording and structure. Do not present all of them as parallel bullets with equal rhetorical weight. Severity: MINOR; BLOCKING when the epistemic status of a statement is obscured — e.g. a limitation presented in the same visual and grammatical form as an established result.

**EF-6 — Compression preserves dependency closure.** *(invariant)*
When a page, word, or slide limit is tight, remove lower-priority branches of the dependency graph rather than deleting prerequisites while retaining dependent claims. A shorter artifact must remain closed under the prerequisites of every retained load-bearing statement.

## Examples

```
EF-1 (repository-local component exposed):
An external report opens: "The RouteBroker refactor eliminates stale hand-backs"
— RouteBroker is an internal component never defined, and the problem it solves
is never stated.
Finding (BLOCKING): repository-local name used as audience knowledge. Introduce
         the problem and the component in audience terms, or drop the internal name.
```

```
EF-2 (use before introduction):
Slide 4 states the main result using the operator ⊞ and the parameter t_max;
⊞ is defined on slide 7 and t_max is never introduced.
Finding (BLOCKING): load-bearing statement precedes its prerequisites. Move the
         definitions before the result, or state the result informally first and
         mark the formal version as forthcoming.
```

```
EF-4 + EF-5 (role-ambiguous fragments):
Contribution list: "• Deterministic routing • Trust boundary • Failure semantics"
— the reader cannot tell whether these are definitions, properties, design
decisions, or results.
Finding (BLOCKING): rewrite each as a complete proposition stating its role,
         e.g. "We prove that routing is deterministic under …" vs. "We define a
         trust boundary that …".
```

```
EF-3 (coinage kept out of habit):
A document uses "context rectification" (a term coined inside the repository)
where "reordering explanations so prerequisites come first" is clearer to the
intended audience.
Finding (MINOR): replace the coinage with the direct description, or define it
         explicitly at first use if it genuinely recurs.
```

```
EF-6 (compression broke closure):
A compressed deck removed the definition of the filtration value but retained
three later slides whose claims quantify over it.
Finding (BLOCKING): retained claims depend on a deleted prerequisite. Restore the
         definition or remove the dependent branch entirely.
```

```
EF-5 (limitation dressed as result):
A bullet "Convergence in the degenerate case" appears in the same list and form
as proved results, but the source marks it unresolved.
Finding (BLOCKING): epistemic status obscured. State it as an explicit limitation
         or open question, visually and grammatically distinct from results.
```

```
EF-1 (must not flag — declared prerequisites):
A specialist paper assumes measure-theoretic probability, listed in
allowed_prerequisites, and uses "martingale" without definition.
Finding: none — standard concepts within the declared audience background need
         no introduction.
```

```
EF-4 (must not flag — unambiguous label):
A slide titled "Two-object case" above a worked example, with the explanation
present on the slide.
Finding: none — the noun phrase is a topic label whose role is visually and
         contextually unambiguous.
```

```
EF-3 (must not flag — earning a local term):
A report defines "anchor unit" once, precisely, and uses it eleven times where
the expanded description would be unwieldy.
Finding: none — the term is recurring, precisely defined, and load-reducing.
```

```
EF-2 (must not flag — recall after a gap):
Section 8 briefly restates a section-2 definition ("recall that an anchor unit
is …") because six sections of unrelated material intervene.
Finding: none — reintroduction after lost local recoverability is required
         behaviour, not redundancy.
```

```
EF-6 (must not flag — closed compression):
An executive summary omits the entire numerical-methods branch and every claim
that depended on it, keeping only conclusions whose prerequisites it retains.
Finding: none — the compressed artifact is closed under the prerequisites of its
         retained statements.
```

## Output

Two modes; review mode is the default.

**Review mode** — report dependency-order defects, undefined audience-facing concepts, ambiguous discourse roles, and proposed restructuring. Each finding lists:
- Rule tag (EF-1 through EF-6), classification, and severity
- Location (section, slide, or line)
- Affected audience assumption (what the text wrongly assumes the reader knows)
- Missing or misplaced prerequisite
- Discourse-role problem, if any
- Required repair or relocation

**Rewrite mode** — when asked to apply fixes, reorder and rewrite the target artifact directly while preserving factual content, qualifications, terminology constraints, and evidence boundaries. Append a change log mapping each change to its rule tag and location.

Avoid producing a large abstract taxonomy in ordinary use. Prefer a small number of actionable findings tied to the target artifact.

## Quality Check

Before finishing, verify:
- No cyclic dependency was left silently unresolved (merged block or marked provisional introduction only)
- Every retained load-bearing statement's prerequisite closure survives any compression applied
- No finding demands a definition for a standard concept covered by `allowed_prerequisites`
- Findings did not drift into prose polishing, factual verification, or correctness review owned by neighbouring skills
- Rewrite mode changed order, framing, and introduction — not facts, qualifications, or evidence boundaries
- The forward-read audit (Procedure 8) was performed from the audience's entry point, not from the source material's order

## Relationship to Other Skills

- Run `exposition-flow` before `deslop-prose`: this skill determines structure and prerequisite order; `deslop-prose` cleans near-final prose.
- Use `deslop-history` when process history leaks into the final artifact; this skill may consume that history as source context but does not expose it without communicative value.
- Use `sot-integrity` to verify authority and evidence boundaries of the source; this skill decides how verified material is introduced to the audience.
- For mathematics, compose with `math-claim-integrity`, `math-notation-consistency`, and the relevant language-style skill (e.g. `wabun-math-style`). Those skills audit correctness, claim structure, notation, and language; this skill owns audience prerequisites and information order.
- Do not expand this skill into factual verification, citation checking, typography, or generic slide design.
