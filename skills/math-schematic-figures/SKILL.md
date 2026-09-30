---
name: math-schematic-figures
description: Plan, draw, revise and review explanatory mathematical figures in manuscripts, notes and presentations, including proof-dependency diagrams. Use when symbolic relations need a visual explanation, supplied figures must be incorporated or redrawn, or existing figures need an audit of content and legibility. Preserve mathematical correspondences and require independent inspection of the actual rendered figure in context. Not for empirical data analysis or independent proof verification.
---

# Math Schematic Figures

Produce figures whose geometry exposes mathematical information that is harder to perceive from prose or formulas alone. A figure may make the same mathematics easier to see; it need not introduce a new claim. Moving prose, formulas or a symbolic diagram already in the text into a figure environment does not by itself add explanatory value.

This skill covers planning, drawing, polishing and acceptance of a correct, informative and legible figure. The creating agent may perform the visual refinement. Independent visual review is mandatory in every use, including a single small figure.

## Use when

- A manuscript, note or presentation needs an explanatory drawing of a mathematical object, construction, correspondence, obstruction or change.
- A proof-dependency diagram is drawn, revised or audited.
- Supplied sketches or reference figures must be included, redrawn or used in a specified role.
- Existing figures need an audit of mathematical fidelity, explanatory value or legibility.

## Boundaries

Plotting measured or computed data and its statistical interpretation belong to a data-visualisation workflow. Classify by purpose, not by file format or whether code generated the picture.

Use `math-claim-integrity` for the validity of the underlying claim and for retrieving the formal declarations that support machine-checked claims; `math-notation-consistency` for label meanings; `wabun-math-style` for Japanese wording; `exposition-flow` for the agreed reader needs and surrounding exposition order; and `deslop-prose` for caption prose. This skill still checks that the figure and caption faithfully represent the intended mathematics. A figure does not replace a missing proof, and visual review does not authorise changing a theorem to fit a picture.

## Inputs

Establish the mathematical anchor and surrounding context; the figure's explanatory purpose and the agreed reader needs; supplied references and their intended roles; canonical notation; the intended page or slide size and rendering method; and an independent reviewer able to inspect images.

Reference roles include direct inclusion, content-preserving redrawing, required composition, comparison material and style guidance. Take the role from the brief and relevant owner decisions, not from an attachment's presence or format. Return consequential ambiguity to the user before omitting or repurposing required material.

## Rules

**1. Decide what the geometry must communicate.**
Identify the distinction, operation, obstruction or correspondence the reader should perceive, and the spatial feature that expresses it: position, adjacency, containment, branching, identification, deformation, direction, thickness, correspondence or a before/after change. A commutative, categorical or order diagram copied from the text is still symbolic syntax; either leave it in the text or translate it into a visual model whose geometry carries information the symbolic form does not. Retain labels that identify the mathematics; reject decoration that leaves the reader to reconstruct the subject from text inside the drawing.

When another figure serves a similar purpose, identify the feature that makes the new figure necessary. Do not schematise away the feature that distinguishes the example, including a foundation the author has stated.

**2. Preserve reference roles.**
A figure requested for inclusion or reproduction must not silently become inspiration only, and a style reference must not become a deliverable merely because it was attached. Preserve required content when redrawing, and use an existing accepted rendering as the comparison baseline; do not replace it with a less informative approximation and call that restoration.

**3. Encode the operative structure, not a default convention.**
Choose layout according to the mathematics being explained. A conventional vertical orientation of an order diagram is not a scalar height function; draw actual heights, axes, thickenings or paired layouts only when that structure is part of the mathematics. Do not introduce a fictitious metric or height coordinate to make a diagram look geometric, and do not prescribe axis placement or dimensions universally. When a scalar parameter or function is operative, use one consistent orientation for it and make transformations visible in that coordinate.

A schematic instance has incidental properties. Do not imply that its spacing, symmetry or extra properties are hypotheses or conclusions of the general statement.

**4. Draw changes and correspondences honestly.**
Before/after panels share enough layout and conventions for the intended change to be visible; paired figures that share objects adopt the same conventions. Preserve positions where the transformation allows it, but do not force an unchanged layout that misrepresents the operation.

A process arrow or phrase such as "obtained from" requires the later panel to be the stated transformation of the earlier one; otherwise present the panels as parallel comparisons. When panels depict the same example in different representations, check the correspondence feature by feature, including the events and relations relevant to the statement.

**5. Check the mathematics the picture asserts and the render.**
Verify explicit parameters, coordinates, incidences, inequalities, labels and transformations against the mathematical anchor. Then inspect the actual render in its intended page or slide context. Source correctness and build success do not establish legibility; visual plausibility does not establish correct example data.

For a proof-dependency diagram, establish what its arrows mean and check each asserted dependency against the relevant proof and active assumptions. Distinguish direct use, a deliberately summarised dependency and a mere presentation sequence. Proximity, pipeline order or matching types do not establish a proof dependency; a keyword match is neither necessary nor sufficient. After a relevant proof or diagram change, recheck the affected relationships as well as the rendered figure. A schematic graph may intentionally omit intermediate nodes or redundant transitive arrows; do not demand an exhaustive call graph unless that is its stated purpose. Do not preserve a false arrow because the diagram looks plausible. Report an established false dependency for mathematical-content review; uncertainty about the underlying proof is not automatically a false-edge finding.

Check purpose, fidelity, readability at use size, overlap, clipping, overflow, label density and cross-panel consistency. A magnified standalone preview does not replace the intended-size check.

**6. Independent visual acceptance is required.**
The creator's own render inspection is iteration, not acceptance. A reviewer other than the creator must actually view the rendered version being accepted, in its page or slide context. An agent reviewer must have working visual input and exercise it. Source inspection, build logs, another worker's PASS and an asserted but unused image capability do not satisfy this gate.

Give the reviewer the mathematical anchor, explanatory purpose, reference instructions and the current render with its location. The reviewer judges the figure itself, not the creator's account of it. A later change affecting content, appearance or layout requires renewed inspection of the affected figures. If no independent visual review is available, the figure remains unaccepted; report that unmet condition rather than self-certify.

**7. Expose limitations of visual judgement.**
If a reviewer cannot reliably resolve an acceptance-relevant feature, name that feature and the uncertainty, then obtain a clearer render, a detail view or a check that addresses it. Do not manufacture a numerical confidence estimate or repeat reviews until one returns PASS.

If material uncertainty or disagreement remains, return it to the user with the render, the checks performed and the unresolved question. User-mediated review or refinement by a design specialist is an optional escalation route for a concrete concern, not a mandatory role or a capability inferred from an agent's name. A handoff is not acceptance.

**8. Preserve the surrounding mathematics.**
Captions identify what is drawn and what to notice, in the document's vocabulary; their length follows purpose and publication constraints. Do not introduce an unverified claim or hide essential qualifications in unexplained labels. Reference the figure from the text. Do not delete a definition, theorem, proof obligation or authorial motivation because a picture was added; report a concern about the mathematical anchor for mathematical review rather than repairing it silently in the illustration.

## Anti-patterns

Each is a finding under the rule named:

- formula or condition panels that only box text; symbolic diagram promoted to figure (1)
- undifferentiated thumbnails; a vacuous example that loses the distinguishing feature (1)
- required content ignored; degraded "restoration" (2)
- a fictitious height or metric imposed on an order (3)
- false correspondence or process arrow between panels; false dependency arrow (4, 5)
- label overload, unreadable density, overlap, clipping or overflow at use size (5)
- a PASS unsupported by independent inspection of the current render (6)

## Procedure

1. State the figure's purpose and the reader needs it serves, and resolve the roles of supplied material. Decide whether a new figure is warranted or an existing one should be revised or reused.
2. Choose an example and visual encoding that expose the intended phenomenon; for a dependency diagram, fix what its arrows mean. Plan only the panels, labels and conventions needed.
3. Draw in a suitable editable format, reusing document-level style conventions where they help; no particular drawing language or file layout is required.
4. Check construction data and depicted dependencies; render in context; inspect and revise. Keep meaning independent of colour alone when the medium requires it, and omit decorative depth or panels that add no information.
5. Obtain independent visual review of the current version. Resolve defects and re-render as needed; escalate unresolved visual or mathematical uncertainty rather than declare an unsupported PASS.
6. Deliver the accepted source and render, or identify the result as a draft awaiting the unmet acceptance step.

## Boundary examples

```text
Wrong role:
The user asks to reproduce a sketch's content. The agent extracts its colours
but omits the depicted construction.
Repair: restore the required content; style resemblance is not fulfilment.

Different legitimate role:
The same image is supplied only to illustrate a restrained visual style.
Do not insert or reproduce its unrelated mathematical subject.
```

```text
Misleading process:
Two panels show plausible graphs, but contracting the marked edge in the first
does not produce the second.
Do not connect them with a contraction arrow. Correct the example or label the
panels as a comparison that does not claim that transformation.
```

```text
False dependency arrow:
A diagram draws "Lemma A -> Proposition B" because A sits upstream in the
pipeline, but B's proof never uses A; A is used directly in the proof of
Theorem C. Redirect the arrow to C.

Arrow truth is not a keyword match:
B's proof mentions A's label only in a remark, so a label search finds it, but
the argument does not use A. Conversely, B's proof uses A through an unlabelled
restatement of it. Read the proof to decide either case.

Valid summary — keep:
A diagram intended as an overview draws "Lemma A -> Theorem C" where A enters
through an intermediate lemma that the figure deliberately omits. Do not expand
it into the full call graph.
```

```text
Acceptance:
The creator re-renders and judges its own figure correct: not accepted.
A different reviewer with working visual input views the current page render
and reports no defects: accepted for that version.
At the delivered size, the reviewer cannot tell whether two curves meet or
cross: not accepted until resolved; otherwise report that specific limitation.
```

## Outputs

Provide the editable figure source and the intended-context render, and state for the delivered version whether independent visual acceptance was obtained or which acceptance condition is unmet. Use the consuming project's existing review and delivery channels and its explicit notification policy; no status document or fixed per-figure record is required.

For an escalation, include the current source and render, the intended mathematics, the reference role, the unresolved feature and enough rendering information to continue. No particular source-header syntax or service-specific handoff format is required.

## Quality check

The geometry contributes explanatory value; required references have not been demoted; distinguishing content survives schematisation; example data, panel correspondences and dependency arrows agree with the mathematics; the current delivered render has been inspected independently; and no acceptance-relevant uncertainty has been concealed by a PASS.
