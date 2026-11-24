---
name: deslop-caveat
description: Use whenever writing or revising any text a human may read. Cut caveats and qualifications that tell a careful reader nothing new.
---

# Deslop Caveat

Apply while drafting or revising papers, proofs, notes, specifications, documentation, docstrings, code comments, commit messages, PRs, issues, changelogs, reports and chat replies, in any language. A handoff, prompt or specification written solely for agents is outside this skill; one intended for human review is in scope.

## The deletion test

Delete the qualification. **Given the text at the reader's entry point, could a careful reader now reasonably draw a wrong conclusion or act wrongly?** If not, leave it out. A reader may open a theorem or API entry on its own.

**Do not bring up a claim just to deny it when the text gives the reader no reason to infer it.**

Apply the same test to a denial (“No X is provided”), a positive exclusion (“Out of scope: X”), or a qualification hidden in a word or proof step (`only`, `exactly`, a repeated hypothesis, an unnecessary case split). None of these forms is itself a defect.

Keep what determines the claim or action: a hypothesis, a failing converse, what the evidence supports, an input constraint or a safety warning. State the useful distinction with the claim or instruction it qualifies. Use `math-claim-integrity` to settle the scope of a mathematical claim and `exposition-flow` to place a distinction whose prerequisites come later.

## Examples

- **Changelog:** “Adds the isomorphism `foo_iso`. No executable extraction is available.” → “Adds the isomorphism `foo_iso`.” A later addition elsewhere should not make this entry false.
- **API guide:** “`read_v1` accepts v1 snapshots. Other versions are rejected.” → “`read_v1` accepts v1 snapshots only.” A caller needs the format contract. In lasting text, describe the named object's scope rather than taking inventory of what is absent elsewhere.
- **Issue:** For a typo in the help text, drop “Out of scope: redesign the parser.” For a renamed option, keep “Continue accepting the old spelling in saved configurations.”
- **Paper body, convergence:** “For a nonempty finite graph with a piecewise-linear height function and a finite cover of its range by bounded open intervals, the geometric interleaving distance from the categorical Mapper reconstruction to the Reeb graph is bounded by the maximum width of the cover intervals with nonempty pullback. It therefore tends to zero as this width tends to zero. This result does not provide an algorithm for enumerating the components.” Delete the last sentence. The bound and convergence make no algorithmic claim.
- **Paper body, upper bound:** “Composing a 1/4-interleaving between the parallel-edge and single-edge graphs with a 1/2-interleaving between the single-edge graph and its midpoint gives a geometric interleaving at 1/4 + 1/2. Thus the distance from the parallel edges to the midpoint is at most 3/4; no exact value is claimed.” Delete the clause after the semicolon. The inequality already states what was proved.
- **Counterexample:** Keep both properties in “A surjection need not be injective: the constant map from a two-point set to a singleton is surjective but not injective.”
- **Japanese commit message:** “ヘルプの誤字を修正。他の動作に変更はない。” → “ヘルプの誤字を修正。”
