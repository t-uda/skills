---
name: wabun-math-style
description: Draft, review or revise narrative Japanese mathematical prose, including motivation, section introductions and explanations of results. Check certainty, connective roles, redundant openings, noun chains, numerals and references while preserving mathematical meaning.
---

# Wabun Math Style

Use for narrative prose in papers, notes and lecture materials. Read [shared Japanese language rules](references/language.md) for every passage; those rules also serve structured mathematical blocks. For explicitly structured definitions, lemmas, propositions, theorems, corollaries, proofs and remarks, use `wabun-math-theorem`.

For any terminology selection, translation, glossary work or terminology audit, use `wabun-math-terminology` and its evidence record before adopting a term. Use `deslop-prose` for general metadiscourse, redundant explanation and rhetorical guard phrases. Read [drafting preferences](references/drafting.md) for new prose, translation or a requested stylistic rewrite. Apply `math-writing-preferences` only when the user or project elects its personal conventions.

## Narrative rules

**JP-6 (heuristic) — Redundant openings.**
Flag paragraph openings such as `本節では`, `以下では`, `なお` and `ここでは` only when the heading already signposts the same content and deleting the opener loses no information. Severity: MINOR. One purposeful orientation sentence per section is fine; preserve useful signposts such as `まず〜を示す`.

**Conditional roles in narrative.**
Keep genuine regime and comparison expressions such as `有限次元の場合`, `正則性を仮定しないとき` and `従来法を用いる場合`. When a sentence actually asserts a theorem-like implication, make its antecedent and consequent explicit; do not let a case-like phrase silently carry the antecedent. Severity: MINOR for obscured implication wording in narrative. Do not apply proof-progression restrictions to ordinary narrative.

## Procedure and output

Read the passage, intended register, live assumptions and supplied source for a translation. Apply the shared rules and the narrative rules to the passage's actual role. Do not change mathematics, notation, labels or claim strength to repair language.

For drafting or translation, check and revise the written text before returning it; report unresolved source or evidence problems. For review, give each finding's rule, class, severity, location, reason and concrete Japanese rewrite. Review alone does not request edits. For requested fixes, edit in place and give a compact before/after change log. Do not turn a drafting preference into a finding.

Use `math-claim-integrity` for claim support, quantifier scope and result hierarchy; `math-notation-consistency` for notation; `math-semantic-preservation` for an edit's fidelity to its source. Report each defect at its owning layer, without duplicate findings.
