---
name: deslop-caveat
description: Use whenever writing or revising any text a human may read. Cut caveats and qualifications that tell a careful reader nothing new.
---

# Deslop Caveat

Apply while drafting or revising papers, proofs, notes, specifications, documentation, docstrings, code comments, commit messages, PRs, issues, changelogs, reports and chat replies, in any language. Text that stays agent-internal, such as a private handoff, is outside this skill. Mixed-audience text, such as an issue body with instructions for an agent, is in scope.

## The deletion test

Delete the qualification. **Given the text at the reader's entry point, could a careful reader now reasonably draw a wrong conclusion or act wrongly?** If not, leave it out. A reader may open a theorem or API entry on its own.

**Do not bring up a claim just to deny it when the text gives the reader no reason to infer it.**

Apply the same test to a denial (“No X is provided”), a positive exclusion (“Out of scope: X”), or a qualification hidden in a word or proof step (`only`, `exactly`, a repeated hypothesis, an unnecessary case split). None of these forms is itself a defect.

Keep what determines the claim or action: a hypothesis, a failing converse, the scope of a proof or measurement, an input constraint or a safety warning. State the useful distinction with the claim or instruction it qualifies. Use `math-claim-integrity` to settle the scope of a mathematical claim and `exposition-flow` to place a distinction whose prerequisites come later.

When deleting a redundant qualifier, preserve the term it qualifies and the established notation, index origin and mathematical convention. In mathematical prose review, mark redundancy alone as MINOR.

## Examples

- **Changelog:** “Adds the isomorphism `foo_iso`. No executable extraction is available.” → “Adds the isomorphism `foo_iso`.” A later addition elsewhere should not make this entry false.
- **API guide:** “`read_v1` accepts v1 snapshots. Other versions are rejected.” → “`read_v1` accepts v1 snapshots only.” A caller needs the format contract. In lasting text, describe the named object's scope rather than taking inventory of what is absent elsewhere.
- **Issue:** For a typo in the help text, drop “Out of scope: redesign the parser.” For a renamed option, keep “Continue accepting the old spelling in saved configurations.”
- **Paper body, convergence:** Take a nonempty finite graph with a piecewise-linear height function and cover its range by finitely many bounded open intervals. “The geometric interleaving distance from the categorical Mapper reconstruction to the Reeb graph is bounded by the largest full width of a cover interval with nonempty pullback. The distance tends to zero as this width does. This result does not provide an algorithm for enumerating the components.” Delete the last sentence.
- **Paper body, upper bound:** “Compose the 1/4-interleaving between the parallel-edge and single-edge graphs with the 1/2-interleaving between the single edge and its midpoint. This bounds the geometric interleaving distance between the parallel edges and the midpoint by 3/4; no exact value is claimed.” Delete the clause after the semicolon.
- **Counterexample:** Keep both properties in “A surjection need not be injective: the constant map from a two-point set to a singleton is surjective but not injective.”
- **Japanese commit message:** “ヘルプの誤字を修正。他の動作に変更はない。” → “ヘルプの誤字を修正。”
