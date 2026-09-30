---
name: math-claim-integrity
description: Audit the structural and logical integrity of a mathematics paper — quantifier scope, domain-of-definition guards, proof/computation honesty, theorem hierarchy, contribution-list discipline (mapping every claimed contribution to its formal result, prior baseline, concrete gain, and independent significance), stale claims, notation accuracy at introduction, standing assumptions, and undefined relation symbols or coined terms in summary prose — without touching prose style or rhetorical prose inflation. Before reporting counterexamples or proof gaps, recover the exact contextual claim and distinguish an identified defect from incomplete verification. For claims presented as machine-checked, inspect the formal declarations that actually support them.
---

# Math Claim Integrity

Audit a mathematics paper for structural and logical integrity defects: quantifier scope errors, missing domain-of-definition guards, conflation of analytic proofs with numerical evidence, theorem-hierarchy misclassification, stale open-problem claims, notation mislabeling at introduction, define-before-use violations, and standing-assumption drift. The skill is language-agnostic and field-agnostic: the rules apply to any area of mathematics and to papers written in any language. It does not touch prose style or rhetorical inflation and hype at the sentence level (use `deslop-prose`) — structural inflation of the contribution list or result hierarchy is in scope here (R-F, R-M) — and does not track symbol drift across sections (use `math-notation-consistency`).

## Design intent

This skill prevents logically weak or structurally inflated papers by
preserving claim/evidence boundaries and a legible hierarchy between genuine
main contributions and proof infrastructure. It targets a recurring failure
mode where a language model promotes every intermediate result it produced —
lemmas, routine corollaries, worked examples, known-result reformulations — to
theorem status or an independent contribution-list entry, because each
consumed substantial reasoning budget, leaving the reader unable to identify
the paper's actual scholarly contribution. Maintainer note: see
[`docs/skill-rationales/math-writing.md`](https://github.com/t-uda/skills/blob/main/docs/skill-rationales/math-writing.md)
in the source repository for the full design rationale (maintenance-only; not
required runtime context and not shipped with installed copies).

## Use when

Use this skill when:
- A math paper draft needs pre-submission structural review
- A theorem was reorganized and surrounding text may not reflect the new hierarchy
- A §1 contribution list enumerates lemmas, routine corollaries, worked examples, or known-result reformulations as if they were parallel main results
- A quantifier scope error (for-all vs exists, iff vs implies, general vs special-case) is suspected
- The introduction or abstract may over-claim or misstate what the theorems actually prove
- A proof section may be conflating analytic argument with numerical/computational evidence
- An open problem claim may have been resolved by a theorem proved later in the same document
- A symbol or concept may be named in a way that misrepresents its mathematical role
- A report or note presents claims as machine-checked against a formal source
- The abstract, introduction, or conclusion uses a relation symbol (≺, ⊏, an ad hoc ordering) or a coined comparative term ("strictly finer than", "detection hierarchy", or an equivalent coinage in any language) that is never formally defined in the body

## Do not use

Do not use this skill for:
- Sentence-level prose inflation, hype, or AI-generated decoration → use `deslop-prose` (but structural contribution/hierarchy inflation belongs here: R-F, R-M)
- Symbol-table drift across sections → use `math-notation-consistency`
- Japanese-specific language anti-patterns → use `wabun-math-style`
- How a valid proof is exposed to readers → use `math-proof-exposition`; translating a formal proof into prose → use `formal-proof-exposition`
- Discussion-history artifacts in planning docs → use `deslop-history`
- Whether an edit, paraphrase, or terminology migration preserves the semantic content of its source (referent identity, operation vs result, quantifier or equality mode changed by an edit) → use `math-semantic-preservation`

## Inputs

Gather or infer these before starting:
- `artifact` — the LaTeX file or section range to audit
- `main_theorem` — the result the paper is organized around (if known)
- `citation_boundary` — what is credited to cited works vs. new in this paper
- `proof_mode` — analytic/algebraic, numerical/computational, or mixed
- `formal_source` — the relevant formal source or an accessible reference, when claims are presented as machine-checked (optional; formal source already supplied in the task context counts)

## Procedure

1. Read the abstract and introduction. List all informal theorem descriptions and every contribution-list item.
2. Locate every theorem-level environment (theorem, proposition, lemma, corollary) in the body.
3. Before diagnosing a suspected defect, reconstruct the exact contextual claim and its live hypotheses under R-N.
4. For a claim presented as machine-checked, inspect the formal declaration that actually supplies its stated bound, hypotheses or conclusion; a headline theorem does not substitute for an intermediate result being quoted. Follow helper declarations only as needed to resolve that correspondence, including asserted matches in a correspondence table. Compare complete statements and instantiations, not identifier names or exponents in isolation. If the source cannot be inspected, report the unchecked scope rather than asserting either agreement or a defect.
5. Apply rules R-A through R-N; record findings.
6. Produce a structured finding report, keeping review limits separate from findings.

## Rules

Each rule is tagged with a classification that sets a default severity: **invariant** — a violation makes the claim logically, structurally, or operationally wrong — defaults to BLOCKING; **convention** — a strong scholarly norm with bounded exceptions — defaults to MINOR, escalating to BLOCKING when the violation obscures logical structure, contribution hierarchy, or the reader's ability to identify the paper's main result; **heuristic** — a review trigger requiring contextual judgement — defaults to ADVISORY, escalating per its own stated condition. A rule's own text overrides this default where it states a severity explicitly. When a defect triggers more than one rule (e.g., an inflated theorem that is also miscounted in the contribution list), report each tag; the defect's severity for gating purposes is the maximum across triggered findings (BLOCKING > MINOR > ADVISORY > NOTE).

**R-A — Quantifier exactness.** *(invariant)*
Every claim must be stated at exactly the quantifier strength the proof establishes. Flag: "iff" when only one implication is proved; "for all t" when the proof only establishes "for sufficiently small t" or "for fixed t"; "for any input" when the result depends on a specific instance; a general formula when only a special case was derived. The quantifier structure of the statement must match the quantifier structure of the proof.

**R-B — Domain-of-definition guard.** *(invariant)*
Any quantity defined via a potentially-failing operation (matrix inverse, division, limit, logarithm) must: (a) name its failure locus at the point of definition, and (b) have every subsequent universal claim over that quantity guarded by the same condition. Example: a quantity defined via the inverse of a parameter-dependent matrix A(t) must state that it is defined only where A(t) is invertible; every "for all t" claim about it must be guarded by "for all t where A(t) is invertible" or equivalent.

**R-C — Attribution boundary.** *(convention)*
Each theorem/proposition must be unambiguously classifiable as: (i) cited verbatim, (ii) restated/repackaged from a citation, or (iii) original to this paper. Infrastructure from cited works (constructions, prior existence results) must not be presented as the paper's own novel contribution. Conversely, genuinely original results must carry an explicit claim of novelty or must not be attributed to prior work by passive or vague phrasing. For the voice mechanics of attribution in Japanese (passive 〜が示されている vs active 〜を示す), cross-reference `wabun-math-style` rule JP-3. When the `citation_boundary` input is not supplied, all R-C findings are automatically severity NOTE ("unverifiable attribution") rather than BLOCKING or MINOR — flag the location but do not assert novelty or citedness without the boundary information.

**R-D — Proof/computation honesty.** *(invariant)*
Analytic/algebraic proofs and numerical/computational verifications must be strictly separated. Rules: every decimal value must be labeled as approximate or as a convenience form of an exact quantity; a load-bearing numerical claim must either have a closed-form analytic companion OR an explicit statement that the result is a certified numerical result (interval arithmetic, exact-arithmetic computation, rigorous exhaustive finite case enumeration with exact decision) with a statement of why a closed form is unavailable; grid-search or script output may be labeled as motivation or corroboration but not as a proof step. A claim presented as machine-checked is supported only by the declaration inspected under Procedure step 4.

**R-E — Stale-claim elimination.** *(invariant)*
Scan for claims labeled open, unresolved, conjectural, or under investigation. For each, check whether the paper itself contains a theorem that resolves the claim. A claim labeled "open" that is resolved by a theorem proved elsewhere in the same document is a hard error. A condition listed as an assumption in a theorem that the paper later proves is universally satisfied should be flagged for the author to confirm removal (MINOR severity), as authors sometimes intentionally retain explicit hypotheses for modularity or citability.

**R-F — Theorem hierarchy (functional, not nominal).** *(convention)*
Evaluate each theorem-level result by function, not by environment label: Does it carry independent scholarly significance? Is it advertised as a main result by the title, abstract, or introduction? Is it independently reusable or citable on its own? Or is it used solely as input to another result (proof infrastructure), an immediate corollary, a routine calculation, a worked example, or a reformulation of a known result? A result used solely as proof infrastructure should normally be labeled Lemma or Proposition, not Theorem, and should not be enumerated independently in the §1 contribution list. Conversely, the paper's central result — the one the title and abstract advertise — must appear as a named Theorem in the body, not only as an unemphasized corollary of a more general statement. An intermediate result may legitimately remain theorem-level when it has independent significance, reuse, or value beyond its role in the main proof — evaluate the role, never demote mechanically by environment name alone. Severity: escalates to BLOCKING when naming/presentation flattens the actual result hierarchy enough that a reader cannot identify the paper's genuine main result, even though every individual statement is mathematically true.

**R-G — Introduction–body consistency.** *(invariant)*
Every informal theorem description in §1 (introduction, contributions list) must match the actual formal statement in the body. Check: quantifier direction, domain of validity, what is assumed vs. what is concluded, and what is credited to prior work vs. original. Discrepancies are most often in the introduction; fix there. Note: §1 descriptions may be informal paraphrases but must not be strictly stronger or weaker than the formal statement.

**R-H — Worked example placement.** *(heuristic, advisory by default)*
When the paper's proof strategy is "construct an explicit family, then abstract to a general theorem," the worked example should appear before the general theorem so readers can verify the mechanism concretely. Flag only if a worked example is referenced in the proof before it is introduced, or if the general theorem is cited in the example section in a circular way. Stays ADVISORY unless the placement causes a circular reference, a use-before-definition problem, or a concrete readability failure, in which case it escalates to MINOR.

**R-I — Notation conceptual accuracy at introduction.** *(invariant)*
When a symbol is introduced, its name, LaTeX macro, and description must match its mathematical role. A symbol described as "an invariant" that in fact depends on a varying parameter or an auxiliary choice (a basis, an ordering, an embedding) is a mislabeling. A macro whose name suggests a standard operator but denotes a nonstandard variant is confusing. Flag at the point of introduction, not later uses. Later-use consistency across sections is out of scope for this skill.

**R-J — Define before use.** *(invariant)*
Every symbol appearing in a theorem statement, proof step, or displayed formula must have a formal definition or explicit introduction earlier in the document (not in a later remark or footnote). Check that every LaTeX macro used in theorem environments is either a standard math symbol or explicitly defined in the preamble or body before its first theorem-context use. Cross-section symbol bookkeeping (single definition site, back-references after gaps) is handled by `math-notation-consistency`. R-J owns completeness of theorem statements; `math-notation-consistency` owns cross-section consistency.

**R-K — Standing assumption inheritance.** *(invariant)*
When a section or theorem relies on standing assumptions declared earlier (e.g., "throughout this section, X is a compact metric space"), every theorem in that section must either inherit those assumptions explicitly or state explicitly that it holds without them. After a structural revision (reordering sections, splitting a theorem), check that standing assumptions have not been silently dropped or silently over-applied. Flag any theorem whose hypothesis list differs from the standing assumptions without explanation.

**R-L — No undefined relation symbols or coined terms in claims.** *(invariant)*
Every relation symbol (≺, ⊏, ⋖, an arrow used as an ordering, or any ad hoc comparative notation) and every coined comparative term ("strictly finer/coarser than", "detection power", or an equivalent coinage in any language) that appears in the abstract, introduction, or conclusion must either (a) have a formal definition in the body before (or explicitly referenced at) the point of use, or (b) be replaced by the explicit logical statement it abbreviates. The standard unpacking of "invariant I₁ is strictly coarser than I₂" is: every pair distinguished by I₁ is distinguished by I₂, and there exists a pair on which I₁ agrees while I₂ differs — state both halves with references to the theorems that prove them. An undefined ≺ in a summary section is BLOCKING even when the intended meaning is guessable, because the reader cannot verify the claim against a definition. Division of labour: `math-notation-consistency` NC-1 owns the bookkeeping of definition sites; R-L owns the requirement that abstract/intro/conclusion claims be expressible entirely in defined terms.

**R-M — Contribution-list mapping discipline.** *(convention; primary requirement)*
Every item in a §1 contribution list must map to: (a) the formal result it corresponds to; (b) the incumbent or prior baseline; (c) the concrete new gain over that baseline; (d) why the item is independently significant rather than merely supporting another listed item; (e) whether it duplicates another listed item at a different level of granularity. Unless independent significance is established, the following must not appear as parallel main contributions: infrastructure lemmas, routine corollaries, direct computational observations, worked examples, known-result reformulations, or several proof components of one result counted separately. Repair: move such material into a proof, remark, example, or auxiliary proposition, or omit it from the list. Escalates to BLOCKING when the abstract or introduction materially misrepresents the paper's main scholarly contribution, even though every individual statement is mathematically true. R-F and R-M often co-fire on the same underlying inflation — R-F concerns the theorem-environment label in the body, R-M concerns whether the §1 list conflates that result with genuine main contributions; report both tags rather than treating them as duplicates.

**R-N — Target the exact contextual claim.** *(invariant; also governs the review itself)*
Before reporting a refutation or gap, recover the proposition as used, its construction history, live hypotheses and established properties. Determine whether it concerns a particular constructed object, a stated class, or every object of a type. Demonstratives can retain the context of the construction they identify.

Do not discard that context or refute a stronger unstated proposition as though it were the manuscript's claim. Conversely, do not invent helpful hypotheses or import restrictions the manuscript does not inherit.

Distinguish four outcomes:
- Refutation: an example satisfies the actual hypotheses and falsifies the actual conclusion.
- Identified gap: a specific required inference or justification is missing after checking the available context; this does not itself refute the conclusion.
- Review incomplete: neither a refutation nor a gap has been established. State the verification limit separately, not as a manuscript defect.
- No finding: the concern is resolved, or only an irrelevant stronger generalisation has been refuted.

A counterexample finding states the claim, live hypotheses, example and failed conclusion. A gap finding identifies the unsupported transition and needed justification. Failure to complete verification or the counterexample fields is not evidence of a gap. A refutation is BLOCKING; an identified gap is BLOCKING when load-bearing and MINOR otherwise. An invalid counterexample or incomplete review cannot justify blocking the manuscript as mathematically defective: it invalidates the review finding, not the manuscript.

## Examples

```
R-I — Before: φ_r is an invariant of X.
      After:  φ_r depends on the choice of basis used to compute it; it is a
              coordinate, not an invariant of X.
```

```
R-B — Before: The quantity M(t) is defined for every t > 0.
      After:  M(t) is defined for every t > 0 at which A(t) is invertible.
```

```
R-F — Before: [In §1 contributions list] Theorem A, Theorem B, Theorem C are proved.
              [In body] Theorem C is used only in the proof of Theorem B.
      After:  [In §1] Theorem B (main result) is proved, using Proposition C as
              infrastructure.
```

```
R-F (must not flag — legitimately theorem-level intermediate result):
[In body] Theorem 3.2 is proved as a step toward the paper's main Theorem 5.1, but
Theorem 3.2 also settles a special case that was independently open in prior work
and is cited on its own by a later paper in the same field.
Finding: none — Theorem 3.2 carries independent scholarly significance (it resolves
         a previously open special case) beyond its role as infrastructure for
         Theorem 5.1, so theorem-level presentation is warranted; do not demote it
         to Proposition merely because it is also used in another proof.
```

```
R-M (contribution list double-counting proof infrastructure):
[§1] "Our contributions: (1) Theorem A, the main classification result; (2) Lemma B,
used in the proof of Theorem A; (3) Corollary C, an immediate consequence of Theorem
A; (4) a numerical illustration of Theorem A on a sample instance."
Finding (MINOR): items (2)-(4) are proof infrastructure, a routine corollary, and a
         worked example of item (1), not independent contributions at the same
         granularity. Demote to remarks/examples inside the discussion of Theorem A,
         leaving one main-contribution item.
```

```
R-M (must not flag — correct contribution list):
[§1] "Our main contribution is Theorem A, which improves the prior bound of O(n²)
(Smith 2019) to O(n log n). The proof uses a new decomposition lemma (Lemma B,
§3), stated separately because it applies beyond this paper to related sieving
problems." Lemma B's independent applicability is stated and used in a later
worked application in the same paper.
Finding: none — one clearly identified main result with its baseline and gain (a),
         (b), (c); Lemma B is presented as infrastructure but with a stated,
         demonstrated independent significance (d), not as a parallel contribution.
```

```
R-M + R-F (true statements, misrepresented hierarchy — BLOCKING):
[§1] "We make three equally important contributions: a new invariant (Theorem 1), a
computation of the invariant for the trefoil knot (Theorem 2), and a restatement of
the invariant's known additivity property in our notation (Theorem 3)." Every
statement in Theorems 1-3 is mathematically correct.
Finding (BLOCKING, R-F + R-M): Theorem 2 is a worked example and Theorem 3 is a
         known-result reformulation; presenting all three as equally weighted
         "theorems" and "contributions" misrepresents which result is the paper's
         actual scholarly contribution, even though nothing stated is false. Demote
         Theorems 2-3 to Example/Remark and rewrite §1 around the single main result.
```

```
R-D — Before: A grid search confirmed that f(θ) < 0 for all θ in the parameter region.
      After:  [NUMERICAL/coarse-grid] A grid search observed f(θ) < 0 on the sampled
              points; the rigorous proof is the analytic argument in §3.
```

```
R-E — Before: The general case remains open.
              [Later in the same paper] Theorem 4.1 (General case): ...
      After:  [Remove the "remains open" claim; update all cross-references to point
              to Theorem 4.1.]
```

```
R-L — Before: The invariants are ordered I₁ ≺ I₂ ≺ I₃. (≺ never defined anywhere)
      After:  I₁, I₂, I₃ distinguish strictly more pairs in this order: for each
              adjacent pair, every instance distinguished by the former is
              distinguished by the latter (Prop. 5.2), and an instance exists on
              which the former agrees while the latter differs (Thm. 6.5).
```

```
R-N — Context: A proof constructs a particular path with a separation property
      and then asserts that the resulting loop is nontrivial.
      Invalid finding: Replace this by the stronger claim "every simple closed
      path is nontrivial," refute that stronger statement, and conclude that the
      original proof fails.
      Required review: Test whether the constructed path with the separation
      property has the asserted nontriviality.
```

```
R-N outcomes:
Refutation: the manuscript claims x^2 > 0 for every real x, with no nonzero
      guard; x = 0 satisfies the stated domain and falsifies the conclusion.
      Report the claim, domain, example and failed strict inequality.
Invalid counterexample: a proof constructs x = 1 + t^2 for real t and
      concludes x ≠ 0; x = 0 is not an instance of the constructed object.
      No finding.
Identified gap: a step invokes a lemma requiring compactness of K, but the
      context establishes only closedness in an arbitrary metric space and
      supplies no replacement argument. Report the missing justification,
      not a false theorem.
Review incomplete: the reviewer has not checked a long preceding
      construction that may establish compactness. Report the unchecked
      dependency as a review limit, not a gap.
Imported restriction: a formal source proves the result under an extra
      hypothesis the manuscript does not inherit. Do not import it to rescue
      the manuscript's claim; assess the claim as stated.
```

```
Machine-checked support (Procedure step 4):
Flag: a note displays a bound as machine-checked and cites the main theorem,
      but the quoted exponent comes from an intermediate lemma whose statement
      gives a different bound. Inspect that lemma and compare the complete
      statements.
Corrected: the displayed bound cites and matches the lemma that states it.
No finding: the lemma bounds the squared error and the note the unsquared
      norm, with the exponent correctly halved; compare full statements, not
      exponents alone. A clearly identified prose derivation is assessed as a
      derivation, not as a false machine-verification claim.
```

## Output

Default: review-only. Produce a structured finding report listing:
- Rule tag (R-A through R-N)
- Review limits (incomplete verification, uninspected formal source) are listed separately and carry no defect severity
- Classification (invariant / convention / heuristic — see Rules) and Severity: BLOCKING / MINOR / ADVISORY / NOTE, following the default-severity mapping above unless the rule states otherwise
- Location: section heading, theorem label, or equation reference
- One-sentence description of the violation
- A concrete rewrite suggestion

When the user explicitly asks to apply fixes: edit the LaTeX source in-place and append a change log with rule tag, location, and before/after text. Do not change notation macros or theorem numbering without explicit instruction.

## Quality Check

Before finishing, verify:
- Every finding has a rule tag, classification, severity, and location
- No finding overlaps with deslop-prose territory (sentence-level prose inflation/hype); structural contribution/hierarchy inflation findings are correctly tagged R-F/R-M here
- No finding reports a symbol-table issue that belongs to math-notation-consistency
- R-H findings default to ADVISORY and only escalate to MINOR under its stated condition (circularity, use-before-definition, or a concrete readability failure) — never to BLOCKING
- R-F and R-M findings identify the actual scholarly gain and hierarchy the paper misrepresents, not merely the environment label used
- R-M findings are not raised merely because a contribution list is long; they require an item that fails the (a)-(e) mapping or duplicates another item's granularity
- A paper is not penalized under R-F/R-M for stating true results — the finding is about hierarchy and presentation, not mathematical correctness
- R-N findings target the exact contextual claim with its construction history and live hypotheses, and neither discard context nor import restrictions the manuscript does not inherit
- Each R-N concern ends as refutation, identified gap, review incomplete, or no finding; counterexample findings state claim, live hypotheses, example and failed conclusion; gap findings name the unsupported transition; incomplete verification is never reported as a gap or used to block

## Relationship to Other Skills

- Use `deslop-prose` when the problem is inflated prose, hype, or AI-generated decoration.
- Use `wabun-math-style` for Japanese-language anti-patterns (epistemic hedges, verb tense, particle misuse).
- Use `math-notation-consistency` for symbol drift across sections, orphaned macros, or alias detection.
- Use `deslop-history` when a planning or notes artifact leaks process history or prior-draft residue.
- Use `math-semantic-preservation` when an edit or explanatory description changed a source statement's meaning or mode; this skill remains responsible when the claim itself exceeds what the proof establishes (its rule MS-4 defers claim-strength defects here).
