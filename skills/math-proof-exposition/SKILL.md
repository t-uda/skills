---
name: math-proof-exposition
description: Draft or review human-readable mathematical proofs when case splits or contradiction arguments are unannounced, introduced objects have no apparent purpose, routine calculations obscure the key step, or compression hides the actual reason. Apply to ordinary and formalisation-derived proofs in any language; do not substitute exposition review for mathematical verification.
---

# Math Proof Exposition

Write around the mathematical argument the reader needs, not around the order in which calculations or auxiliary objects were produced. The reader should recognise the active proof mode, the purpose of a construction, and the step carrying the mathematical difficulty before being asked to interpret its bookkeeping.

## Use when

- Drafting or revising a proof, whether or not a proof assistant was involved.
- A branch, contrary assumption, or auxiliary object appears before its role is announced.
- A proof narrates many local manipulations but obscures their objective.
- A revision is longer without clarifying the delicate step, or shorter only because necessary reasons were removed.

## Boundaries

This skill owns local proof exposition. Use `math-claim-integrity` for correctness, exact claim scope and result/contribution hierarchy; `math-semantic-preservation` for edits that change their source meaning, including probability and measure context; `math-notation-consistency` for definitions, aliases and notation economy; `exposition-flow` for the agreed audience model, reader needs, document structure and transitions between results; `wabun-math-style` for Japanese expression, including the Japanese realisation of proof-mode announcements; and `deslop-prose` for paragraph grouping, which must keep meaningful proof boundaries.

Use `formal-proof-exposition` when formal code or a formalisation repair is a source of the prose. A proof assistant is not a prerequisite for this skill.

## Inputs

Read the claim being proved, the proof and its surrounding live assumptions, the agreed audience model, and any existing proof version or requested edit boundary. Use supplied terminology and notation. Do not assume that the reader knows a construction merely because the writing agent knows it from another file or conversation.

## Rules

**PE-1 — Announce the proof mode before entering it.**
Before a proof by cases, identify the partition criterion. Before adopting an assumption for contradiction, identify that proof mode and the proposition being negated. Make each branch's condition and the eventual common conclusion or contradiction discharge identifiable.

An announcement can be part of an ordinary sentence; no fixed wording, heading format, or separate introductory paragraph is required. A useful signpost is not decorative metadiscourse. Do not make the reader discover several lines later that an unexplained variable or assumption was introduced only for a case split or contradiction.

**PE-2 — Introduce an object with its mathematical job.**
When a new variable, witness, construction, or auxiliary claim has a purpose that is not immediate, expose that purpose before the ensuing manipulations. Distinguish the goal from the details used to achieve it. Naming the object is not the same as explaining why it is needed.

Whether an abbreviation earns its lookup cost is `math-notation-consistency` NC-8; do not duplicate it as a variable budget. A structurally necessary object can deserve a name even if its formula is short or it is used only once.

**PE-3 — Detail follows mathematical difficulty.**
Make the delicate inference visible, especially a step using a newly required hypothesis, boundary condition, or construction property. Compress routine surrounding work when its reason is recoverable for the intended audience. Finding one genuine gap is not a reason to expand every other step to the same granularity.

Do not replace missing reasoning with `by construction`, `clearly`, or `the same argument`. Such compression is justified only when the referenced construction or argument makes the particular conclusion recoverable. If the earlier argument has changed, restate the reason instead of pointing to text that no longer supplies it.

**PE-4 — Compress by identifying a sufficient reason.**
Replace a derivation with the structural reason that establishes its conclusion, not with one long sentence containing the same variables and equations. State the property of the actual configuration that does the work. Do not introduce a stronger general claim merely because it would be one route to the desired conclusion.

An established general theorem or an elementwise argument may be the clearest explanation. Use it when its hypotheses and purpose are clear; do not prohibit element chases or require abstraction for its own sake. Shortness and abstraction are not correctness criteria. Preserve the local mechanism rather than substituting a broader slogan.

**PE-5 — Write at a useful mathematical level.**
Use established names for notions already introduced unless the current step needs their definitions unfolded. Choose grammatical subjects that identify the mathematical objects and relations, not incidental coordinates or indices through which the writer happened to reason.

Representation-level details remain appropriate when they carry the actual argument. For a sequence, chain, cycle, or other visible combinatorial pattern, choose notation that exposes its structure when that improves recoverability; do not mechanically replace meaningful role-based names with indexed ones.

**PE-6 — Preserve useful architecture and result roles.**
When a sound existing proof needs a local repair, preserve its mathematical idea and repair that point rather than automatically replacing it with a different derivation. Restructure when the architecture is wrong or does not serve the reader.

An auxiliary verification is not automatically a separately advertised result. Conversely, a useful intermediate result need not be hidden merely because it supports a later theorem. Result hierarchy is decided under `math-claim-integrity`; judge placement and emphasis by mathematical role, not the effort spent deriving it or a fixed reuse count.

## Procedure

1. Identify the exact claim, live assumptions, the audience model, and the mathematical idea of the proof.
2. Locate the proof modes and the places where objects are introduced. Check whether their purpose is available before their use.
3. Identify the delicate inference and the surrounding routine work. Reconstruct a sufficient reason for any proposed compression.
4. Revise locally or propose a clearer architecture while preserving the claim, assumptions, and actual mechanism. Coordinate notation changes with the notation skill.
5. Read the proof forward. Verify that branches and contrary assumptions are announced and discharged, new objects have roles, and compressed steps remain recoverable.

## Boundary examples

```text
Unannounced case split:
An English proof writes "If n is even, ..." and later "If n is odd, ...",
with a variable m defined only inside the first branch, and never states that
the argument splits on the parity of n or that both branches give the claim.

Repair:
"We distinguish the cases n even and n odd." Label each branch by its
condition, introduce m where its branch opens, and close with the common
conclusion.
```

```text
Unannounced contradiction:
A proof suddenly introduces a larger admissible set, manipulates its elements,
and only at the end says this contradicts maximality.

Repair:
First state that maximality is being proved by contradiction and specify the
assumed larger admissible set. Then expose the property contradicting maximality.
Do not add unrelated variables merely to narrate every elementary obligation.
```

```text
Honest compression:
h is injective and the previous argument establishes h(u) = h(v).
"Injectivity of h gives u = v" states the sufficient reason.

Dishonest compression:
The proof needs h(u) = h(v), but that equality has not been established.
Replacing the missing step by "by construction" does not repair the argument.
```

```text
Keep useful detail:
An element chase is the shortest transparent proof of equality of two sets,
or an explicit decreasing measure explains why an algorithm terminates.
Do not remove it merely because it involves elements or a numerical measure.
```

## Output and quality check

For review, give each finding's rule tag (PE-1 to PE-6), location, the exposition defect (an obscured proof mode or purpose, misplaced detail, compression without a sufficient reason, an unhelpful level, or a lost architecture), and a concrete repair. Keep an exposition defect distinct from a proof gap or a verification not completed, as `math-claim-integrity` R-N distinguishes them.

For authorised rewriting, provide the revised proof and a compact account of substantive structural changes, unless only prose was requested. A change to the theorem or its hypotheses requires an explicit author decision, not a silent exposition edit.

The revised proof must preserve the actual claim and local hypotheses; expose its argument before bookkeeping; retain necessary cases, witnesses, and reasons; avoid empty signposting; and make its key step easier to see without turning the proof into either a formal trace or an unsupported slogan.
