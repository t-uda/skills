---
name: deslop-caveat
description: Use whenever writing or revising any text a human may read. Cut caveats and qualifications that tell a careful reader nothing new.
---

# Deslop Caveat

Apply while drafting or revising papers, proofs, notes, specifications, documentation, docstrings, code comments, commit messages, PRs, issues, changelogs, reports and chat replies, in any language. A handoff, prompt or specification written solely for agents is outside this skill; one intended for human review is in scope.

## The deletion test

Delete the qualification. **Given the text at the reader's entry point, could a careful reader now reasonably draw a wrong conclusion or act wrongly?** If not, leave it out. A reader may open a theorem or API entry on its own. Judge what that reader has been told, not what the author knows.

Apply the same test to a denial (“No X is provided”), a positive exclusion (“Out of scope: X”), or a qualification hidden in a word or proof step (`only`, `exactly`, a repeated hypothesis, an unnecessary case split). None of these forms is itself a defect.

Keep what determines the claim or action: a hypothesis, a failing converse, what the evidence supports, an input constraint or a safety warning. State the useful distinction with the claim or instruction it qualifies. Use `math-claim-integrity` to settle the scope of a mathematical claim and `exposition-flow` to place a distinction whose prerequisites come later.

## Examples

- **Changelog:** “Adds the isomorphism `foo_iso`. No executable extraction is available.” → “Adds the isomorphism `foo_iso`.” A later addition elsewhere should not make this entry false.
- **API guide:** “`read_v1` accepts v1 snapshots. Other versions are rejected.” → “`read_v1` accepts v1 snapshots only.” A caller needs the format contract. In lasting text, describe the named object's scope rather than taking inventory of what is absent elsewhere.
- **Issue:** For a typo in the help text, drop “Out of scope: redesign the parser.” For a renamed option, keep “Continue accepting the old spelling in saved configurations.”
- **Estimate:** “Fix n ≥ 1. For fₙ(x) = nx on the real line, the optimal Lipschitz constant is n (the case n = 0 is excluded).” Delete the parenthesis; keep the dependence on n.
- **Counterexample:** Keep both properties in “A surjection need not be injective: the constant map from a two-point set to a singleton is surjective but not injective.”
- **Japanese commit message:** “ヘルプの誤字を修正。他の動作に変更はない。” → “ヘルプの誤字を修正。”
