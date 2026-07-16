---
name: math-semantic-preservation
description: Review or rewrite mathematical prose so an edit, paraphrase, terminology migration, or explanatory description preserves the exact mathematical meaning fixed by its semantic source — referent identity, operation versus result, domain/codomain and representation level, quantifier and equality mode, role and provenance, notation role, and classified-before-replacement terminology migration with concept-cluster synchronization — without auditing claim-versus-proof strength (use math-claim-integrity), notation bookkeeping (use math-notation-consistency), Japanese style or translation events (use wabun-math-style), or audience prerequisites and ordering (use exposition-flow).
---

# Math Semantic Preservation

Review or rewrite mathematical prose while preserving the exact mathematical meaning of the source. An edit can be linguistically smoother, internally consistent, and mechanically valid while no longer describing the same mathematics; this skill detects and repairs that failure. It is field-agnostic and language-agnostic: it audits semantic fidelity against definitions, formulas, formal declarations, and source passages, not prose style or mathematical correctness of the source itself.

## Design intent

Live review of a large mathematical prose corpus exposed a recurring failure mode: locally plausible wording changes silently altered the object being discussed, conflated an operation with its result, changed an almost-everywhere assertion into an apparent pointwise one, reused an established term for a different operation, misread an index as an exponent, or replaced one overloaded term uniformly across occurrences that denoted distinct objects. Natural language fluency is never evidence that mathematical meaning was preserved. Maintainer note: see
[`docs/skill-rationales/math-writing.md`](https://github.com/t-uda/skills/blob/main/docs/skill-rationales/math-writing.md)
in the source repository for the full design rationale (maintenance-only; not
required runtime context and not shipped with installed copies).

## Use when

- Paraphrasing, smoothing, or restructuring mathematical prose against an authoritative source (definitions, formulas, theorem statements, formal declarations)
- Reviewing a diff or edit of mathematical prose for meaning drift
- Performing or reviewing a document- or corpus-wide terminology migration, especially of an overloaded term
- Generating documentation or explanatory prose from formal sources (Lean, Coq, Isabelle, Agda, or similar)
- Synchronizing the statement, proof explanation, notes, link labels, glossary, and audit records that describe one mathematical concept
- An explanatory description assigns a role to notation, an argument position, or a datum whose definition should be checked first

## Do not use

- For whether a claim is supported at the strength its proof establishes, theorem hierarchy, or claim/proof boundaries → use `math-claim-integrity`
- For definition sites, aliases, symbol reuse across scopes, subscript/superscript typography, or dangling references → use `math-notation-consistency`
- For Japanese-language anti-patterns, terminology SoT conflicts, and translation or source-naming events (JP-16/JP-17) → use `wabun-math-style`
- For audience prerequisites, dependency ordering, and self-containment of an exposition → use `exposition-flow`
- For prose inflation or hype → use `deslop-prose`

One defect, one layer: report the skill whose invariant is actually broken, never duplicate findings. `wabun-math-style` JP-17 owns the translation or source-naming event; this skill owns the corresponding language-agnostic defect when it arises during **monolingual** paraphrase, corpus editing, documentation generation, or terminology migration rather than translation.

## Inputs

- `artifact` — the mathematical prose, documentation, annotation corpus, or document section to review
- `edit_base` — the wording before the edit, when reviewing a change or diff (optional)
- `semantic_source` — definitions, formulas, theorem statements, formal declarations, source-language passages, or other authoritative material that fixes the intended meaning
- `related_artifacts` — linked statements, proofs, notes, glossary entries, labels, or audit records that describe the same concept (optional)
- `terminology_sot` — canonical terminology and permitted aliases (optional)
- `formal_source` — Lean, Coq, Isabelle, Agda, or other formal declarations used as semantic evidence (optional)

Never assume an identifier name is semantically authoritative when its type, definition, formula, or use says otherwise: definitions, formulas, types, and uses outrank labels and identifier names as semantic evidence.

## Rule classification and severity

Each rule is tagged with a classification that sets a default severity: **invariant** — a violation means the prose no longer describes the source's mathematics — defaults to BLOCKING; **convention** — a strong norm with bounded exceptions — defaults to MINOR, escalating per the rule's own condition. A rule's own text overrides this default where it states a severity explicitly. When a defect triggers more than one rule, report each tag; the defect's severity for gating purposes is the maximum across triggered findings (BLOCKING > MINOR > ADVISORY).

## Procedure

1. **Identify the semantic anchor.** Determine which definition, formula, formal declaration, theorem statement, or source passage fixes the meaning of the edited or reviewed text.
2. **Build a compact semantic record.** For each load-bearing edited span, record only the relevant fields: referent, operation or relation, domain and codomain, quantifier or equality mode, assumptions and provenance, notation role.
3. **Classify overloaded terminology by occurrence.** Before any repository-wide or document-wide replacement, classify each occurrence by the mathematical object it denotes. Do not begin with a one-to-one lexical substitution table.
4. **Compare the edit with the semantic record.** Check whether the new prose preserves every load-bearing field. Natural wording is not evidence of semantic equivalence.
5. **Inspect the concept cluster.** When the same concept appears in a statement, proof explanation, note, link label, glossary, or audit record, verify that all members of the cluster use compatible terminology and describe the same object.
6. **Report or repair only the semantic defect.** Do not broaden the task into general prose polishing, theorem proving, or document-wide notation cleanup.

## Rules

**MS-1 — Preserve referent identity.** *(invariant)*
The edited text must refer to the same mathematical object as the semantic source. Flag an edit that replaces one object with a related but distinct object, including: a function with its equivalence class, a subspace with one of its elements, a coefficient family with its sum, or a formal argument position with a tensor factor. Default severity: BLOCKING.

**MS-2 — Distinguish operations from results.** *(invariant)*
An operation and the object produced by that operation must not be conflated. Examples: restriction versus the restricted part, projection versus the projected component, truncation versus truncation residual, composition versus pushforward, convolution as an integral operation versus the resulting curve. Default severity: BLOCKING.

**MS-3 — Preserve domain, codomain, and representation level.** *(invariant)*
The edit must preserve where an object lives and at what representation level a statement is made. In particular: distinguish an L^p equivalence class from a chosen representative, distinguish the value space from the function space, and do not describe a map as acting on a domain different from the one fixed by its definition. Default severity: BLOCKING.

**MS-4 — Preserve quantifier and equality mode.** *(invariant)*
The edit must preserve universal, existential, and eventual quantification; pointwise versus almost-everywhere equality; equality versus convergence; implication versus case selection; and fixed-parameter versus uniform assertions. `math-claim-integrity` remains responsible when the claim itself exceeds what the proof establishes; this rule is responsible when an edit or explanatory description changes the source claim's mode. Default severity: BLOCKING.

**MS-5 — Preserve role and provenance.** *(invariant)*
The edit must correctly identify which assumption, structure, package, field, or previous result supplies a datum; which numbered position is an argument, coordinate, factor, component, or stage; and which construction a later property belongs to. Do not infer ownership from nearby implementation structure or identifier names alone. Severity: BLOCKING when the wrong source changes the mathematical dependency; MINOR when the dependency remains unambiguous but the explanation is locally inaccurate.

**MS-6 — Interpret notation by definition, not typography alone.** *(invariant)*
A superscript is not automatically a power, a subscript is not automatically an index, and a number in an identifier is not automatically the number of a displayed factor. Determine the role from the definition, type, formula, and use. `math-notation-consistency` owns inconsistent typography for the same family (NC-7); this rule owns an incorrect semantic interpretation of otherwise consistent notation. Default severity: BLOCKING.

**MS-7 — Classify before terminology migration and synchronize the concept cluster.** *(convention for cluster synchronization; invariant when the replacement itself collapses distinct concepts)*
A terminology migration must classify occurrences by referent before replacement. After choosing the context-specific terms, update all relevant members of the concept cluster: statement, proof explanation, note, link display text, glossary, and audit or migration record. Do not require every repository metadata field or compatibility identifier to be renamed — the scope is human-facing mathematical content and records that claim to describe the applied migration. Severity: cluster-synchronization defects default MINOR, escalating to BLOCKING when inconsistent terms identify different mathematical objects; a replacement that collapses distinct concepts into one term is BLOCKING.

## Examples

```
MS-1 (argument position read as tensor factor):
Source: B(u, v, w) is a trilinear form applied to the two-factor product u ⊗ v.
Edit:   "w is the third factor of the tensor product."
Finding (BLOCKING): the third argument of the trilinear form was rewritten as a
         third tensor factor; the displayed product has only two factors.
```

```
MS-4 (a.e. assertion made pointwise):
Source: f = g in L^2, i.e. f(x) = g(x) for almost every x.
Edit:   "f(x) equals g(x) at every point x."
Finding (BLOCKING): almost-everywhere equality rewritten as unqualified
         pointwise equality. Restore the a.e. qualifier or the L^2 statement.
```

```
MS-2 (established term reused for a different operation):
Source: T ∘ f, composition of f with a continuous linear map T.
Edit:   "the pushforward of f under T."
Finding (BLOCKING): "pushforward" names an established, different operation.
         Say "the composition T ∘ f" (or "post-composition with T").
```

```
MS-2 + MS-3 (operation conflated with its result):
Source: the restriction of the field to the complement of the ball, yielding
        the exterior part.
Edit:   "the exterior part is the restriction domain."
Finding (BLOCKING): the restriction operation, its domain, and the resulting
         restricted object are three different things; name each correctly.
```

```
MS-7 (lexical migration without occurrence classification):
Plan: replace every occurrence of "tail" with one chosen term.
Corpus: "tail" denotes a Fourier truncation residual in §2, an out-of-box
        coefficient sum in §3, a physical-space exterior part in §5, and
        eventual sequence behaviour in §7.
Finding (BLOCKING): one-to-one substitution collapses distinct objects.
         Classify each occurrence by referent, then choose per-context terms.
```

```
MS-6 (index read as exponent):
Source: Δ^j denotes the j-th member of a family of operators (j an index).
Edit:   "Δ raised to the power j."
Finding (BLOCKING): the superscript is a family index, not exponentiation;
         describe it per the family's definition.
```

```
MS-7 (audit record out of sync):
Glossary records "residual" as the applied replacement; the corpus edit
actually used "remainder term" throughout.
Finding (MINOR, escalating if the terms denote different objects): the record
         claims a migration different from the one applied; synchronize it.
```

```
MS-5 (property attributed to the wrong structure):
Source: the boundedness constant is supplied by the assumption on the measure,
        not by the operator's own definition.
Edit:   "by the definition of the operator, the constant is bounded."
Finding (BLOCKING if the dependency changes, MINOR otherwise): the datum's
         provenance was reassigned; cite the supplying assumption.
```

```
MS-2 (must not flag — established term with its standard meaning):
"the kernel of the map", "the support of the measure", "the pushforward of the
measure under a measurable map" — each used with its standard meaning.
Finding: none — established terminology matching the established operation.
```

```
MS-7 (must not flag — intentional context-specific split):
Two distinct objects that shared one ambiguous source word are deliberately
given two different terms, with the split recorded in the glossary.
Finding: none — the split preserves referent distinctions; that is the goal.
```

```
MS-3 / MS-4 (must not flag — explicit representative selection):
"Fix Borel representatives of f and g; then f(x) = g(x) for a.e. x."
Finding: none — the representation level is explicit and the equality mode
         is stated.
```

```
MS-7 (must not flag — compatibility-only identifier retained):
A formal-source identifier keeps a historical name for compatibility while all
human-facing prose uses the canonical terminology.
Finding: none — compatibility identifiers are out of the synchronization scope.
```

```
MS-7 (must not flag — scoped informal alias in the glossary):
The glossary permits both the precise formal term and a clearly scoped
informal explanation of the same concept.
Finding: none — permitted, scoped aliases are not drift.
```

```
MS-3 (must not flag — codomain detail omitted next to the displayed map):
"the map sends u to its average" immediately below the displayed map
u ↦ (1/|Q|)∫_Q u with explicit codomain.
Finding: none — the omitted detail is explicit in the immediately displayed
         map and cannot be misread.
```

## Output

Default: review-only. Produce a structured finding report listing:
- Rule tag (MS-1 through MS-7)
- Classification (invariant / convention — see Rules) and Severity: BLOCKING / MINOR / ADVISORY, following the default-severity mapping above unless the rule states otherwise
- Location: section heading, environment label, or line
- Semantic anchor: the definition, formula, declaration, or source passage that fixes the intended meaning
- Field that changed: `referent`, `operation`, `domain`, `quantifier`, `provenance`, or `notation role`
- A concrete correction

In fix mode, edit only the affected mathematical prose and synchronized concept-cluster entries. Do not rename formal identifiers, theorem labels, file names, or compatibility APIs without explicit instruction.

## Quality Check

Before finishing, verify:
- Every finding names its semantic anchor and the field that changed
- No finding rests on fluency or naturalness judgments — only on comparison with the semantic record
- Any terminology migration classified occurrences by referent before replacement was assessed
- No duplicate finding for an event owned by `wabun-math-style` (JP-16/JP-17 translation or SoT events), `math-notation-consistency` (bookkeeping), or `math-claim-integrity` (claim strength)
- No compatibility identifier, theorem label, file name, or metadata field was demanded renamed
- Pointwise, almost-everywhere, eventual, and uniform statements remain distinct in every proposed correction

## Relationship to Other Skills

- `math-claim-integrity` owns whether a claim is supported at the strength its proof establishes; this skill owns whether an edit changed the source claim's meaning or mode (MS-4 defers claim-strength defects there).
- `math-notation-consistency` owns document-wide notation bookkeeping — definition sites, aliases, scope, typography (NC-7); this skill owns whether prose assigns the correct mathematical role to otherwise consistent notation (MS-6).
- `wabun-math-style` owns Japanese language review, terminology SoT conflicts, and translation or source-naming events (JP-16/JP-17); this skill owns the language-agnostic semantic defect in monolingual paraphrase, corpus editing, documentation generation, or terminology migration.
- `exposition-flow` owns audience prerequisites and dependency order; it does not determine whether a local mathematical paraphrase preserves the source meaning — that is this skill.
- Do not emit duplicate findings for one defect: report the layer whose invariant is actually broken.
