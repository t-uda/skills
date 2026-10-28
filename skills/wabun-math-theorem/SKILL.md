---
name: wabun-math-theorem
description: Draft, translate, review or revise Japanese wording inside explicitly structured definitions, lemmas, propositions, theorems, corollaries, proofs and remarks, including explicit Markdown equivalents. Preserve statement and proof roles; excludes narrative prose.
---

# Wabun Math Theorem

Apply within the named mathematical blocks, whether LaTeX environments or explicitly labelled Markdown blocks. Read each sentence by its role: a proof goal, definition, conclusion, citation and conjecture need different wording. Use `wabun-math-style` for narrative passages.

Read the [shared Japanese language rules](../wabun-math-style/references/language.md) before drafting or review, and [drafting preferences](../wabun-math-style/references/drafting.md) for new prose, translation or a requested stylistic rewrite. Resolve the `wabun-math-style` companion from the available skill catalog if a sibling path is absent; report a missing required reference. For every terminology operation, use `wabun-math-terminology` and its evidence record. Use `deslop-prose` for redundant explanation and rhetorical guard phrases, and elected `math-writing-preferences` for personal conventions.

## Rules

**JP-3 (convention) — Proof-step voice.**
Construct and advance the argument with forms such as `〜を示す`, `〜とおく` and `〜より従う`. Reserve `〜が示された` or `〜が示されている` for citing a result proved outside the current proof. Severity: BLOCKING when a passive misattributes a result proved here as merely cited, MINOR otherwise. A stative citation passive with an external citation is always legitimate: `[12] により補題の条件が満たされていることが示されている`.

**JP-5 (heuristic) — Justify compressed claims.**
`明らか`, `自明` and `容易に` require a same- or next-sentence justification or reference. Test whether a reader can verify the claim without looking elsewhere. Severity: BLOCKING if a needed sign check, boundary condition or multi-step substitution is not visible, MINOR for milder unjustified compression. Use `math-proof-exposition` PE-3/4 for the sufficient reason; report the same defect only once.

**JP-8 (convention) — Implications, assumptions and cases.**
In theorem/proposition/lemma statements, require `A ならば B` or an equivalent formal conditional when the phrase carries the logical antecedent. `このとき` receives objects and standing assumptions already introduced: `X を固定する。このとき、A ならば B である`. Flag `X を固定する。A のとき B である` when the latter phrase silently substitutes for the implication. Genuine case/regime labels such as `n が偶数の場合`, `t > 0 のとき` and named classification branches remain valid. Decide whether the phrase names a case under discussion or carries the antecedent.

In proofs, preserve `とき`/`場合` for case splits and regimes. Prefer direct progression (`A より B である`, `補題 2.1 と A から B が従う`) to restating an available implication and then its application (`A ならば B である。いま A なので B である`). An implication may itself be proved, quoted or isolated as a reusable subclaim; never require a syllogistic restatement at every deduction.

Severity: BLOCKING for the hidden antecedent in a theorem/proposition/lemma statement or full syllogistic redundancy across consecutive proof steps; MINOR for isolated indirect proof phrasing. No finding for genuine case/regime labels.

**JP-9 (convention) — Avoid unnecessary proof double negation.**
Prefer a direct affirmative to unnecessary double negation in a proof when logically equivalent. Severity: MINOR. Do not eliminate double negation when the logic does not permit it, strengthen an epistemic reservation into an assertion, or remove necessary negation or proof by contradiction.

**JP-20 (convention) — Universal assertions and arbitrary selection.**
In theorem, proposition, corollary and definition statements, express universal quantification with `全ての` or an equivalent explicit universal quantifier, not `任意の` as a general substitute, even when the intended universal meaning is recoverable. In proofs, `任意に ... をとる` selects an arbitrary object. Preserve quantifier order, domains and dependencies. Severity: MINOR for the wording violation, BLOCKING when a load-bearing statement's quantifier role is genuinely obscured.

Example: a theorem's `任意の $\varepsilon>0$ に対して` becomes `全ての $\varepsilon>0$ に対して`; keep the proof selection `$\varepsilon>0$ を任意にとる`.

**JP-21 (convention) — Announce and close proof modes.**
Apply `math-proof-exposition` PE-1 with explicit Japanese wording: before the first case branch, state the partition criterion (`$v$ と $w$ が隣接するか否かで場合を分ける`), then label each branch by its condition. Before a contradiction argument, announce contradiction or the contrary assumption. After the branches or contradiction discharge, state the common conclusion with `以上より` or an equally explicit closing sentence. A genuine case label that is already the announced branch is valid. Severity: BLOCKING when proof structure is difficult to reconstruct, MINOR for a merely unclosed local split. Report one finding for JP-21/PE-1.

## Procedure and output

Read the block, live assumptions, references and source text for a translation. Apply the shared rules and the rules above by sentence role. Preserve mathematics, claim strength, notation, macro names and theorem labels. Use `math-claim-integrity` for proof support, quantifier scope and result hierarchy; `math-notation-consistency` for notation; `math-semantic-preservation` for meaning drift.

For drafting or translation, check and revise the prose before returning it, reporting unresolved source or evidence problems. For review, give each finding's rule, class, severity, location, reason and concrete Japanese repair. Edit only when fixes are requested, then give a compact before/after change log. Report one defect at its owning layer; drafting preferences alone are not findings.
