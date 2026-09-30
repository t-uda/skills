---
name: math-notation-consistency
description: Review mathematical documents during drafting or revision for undefined or conflicting notation, undeclared aliases, live-scope ambiguity, unrecoverable references, orphaned LaTeX macros, low-value abbreviations, and structural nouns that obscure their contextual referent or role. Use when notation or terminology changes, local names proliferate, or objects are described by generic coordinate/component labels. Do not verify proofs, impose an external notation style, or treat harmless reuse in a closed scope as a defect.
---

# Math Notation Consistency

Audit a mathematics document for internal notation consistency. The skill is field-agnostic and applies to documents in any language.

Preserve recoverable canonical meanings and useful notation. This skill owns notation bookkeeping, notation economy and contextual ambiguity of structural nouns. It does not verify mathematical claims or prescribe an external notation style. LaTeX checks apply when source is available.

Use `math-semantic-preservation` for an edit that changes source meaning, `math-claim-integrity` for claim support and substantive conceptual errors, and `wabun-math-style` for Japanese lexical choice when the referent is already clear. Report a defect at its owning layer rather than duplicating it.

## Design intent

This skill prevents revision-driven notation drift: language models revising a
document repeatedly lose track of whether a document-specific symbol still has
a single locatable canonical definition, letting undefined, conflicting, or
ambiguously reused notation accumulate across revisions. The "one definition
site" wording targets locating a canonical meaning and catching incompatible
redefinition — not counting every textual occurrence of a definition phrase.
Maintainer note: see
[`docs/skill-rationales/math-writing.md`](https://github.com/t-uda/skills/blob/main/docs/skill-rationales/math-writing.md)
in the source repository for the full design rationale (maintenance-only; not
required runtime context and not shipped with installed copies).

## Use when

- A LaTeX math paper has been through multiple revisions and may have notation drift (same object referred to by two names in different sections)
- A symbol or operator appears in a theorem but its definition is not clearly locatable
- Two LaTeX macros in the preamble appear to define the same object (e.g., `\R` and `\Reals` both for ℝ)
- A macro is defined in the preamble but never used in the document
- A named concept has accumulated multiple aliases (a full name, an abbreviation, and one or more symbols) without a declared equivalence
- A symbol introduced in section 2 reappears in section 5 with no reminder of its definition
- The same symbol is used for two different objects (e.g., r as a parameter in one section and as an index in another), or a local symbol invites a conventional competing parse (e.g., a scalar Γ written as Γ(d+2))
- A relation symbol or operator (e.g., ≺) appears only in the abstract or conclusion with no definition site anywhere in the body
- A term defined in the document's main language is later used in another language for the same concept (e.g., a defined Japanese term later written in English), or the same operator is written with two argument conventions (e.g., F(X,t) vs F(tX))
- Local names or abbreviations proliferate without doing mathematical work
- An object is described by a generic structural noun (coordinate, component, coefficient) that obscures its referent or role

## Do not use

- For quantifier scope errors, theorem hierarchy, or proof/computation distinction — use `math-claim-integrity`
- For prose inflation — use `deslop-prose`
- For prose assigning the wrong mathematical role to consistent notation (a family index read as an exponent, an argument position read as a tensor factor) — use `math-semantic-preservation`

## Inputs

- `artifact` — the document source, LaTeX when available (full document preferred; section range accepted)
- `preamble` — the LaTeX preamble (if separate; otherwise included in artifact)
- `known_aliases` — a list of intentional synonyms the author has declared equivalent (optional; also inspect equivalences declared in the artifact)

## Procedure

1. Extract all `\newcommand`, `\renewcommand`, `\DeclareMathOperator` definitions from the preamble; build a macro-definition table.
2. Extract all first-use-in-prose definitions (e.g., "let X denote …", 「\(f\) を〜とおく」); note section and location.
3. For each macro in the definition table, check whether it appears in the document body; flag unused macros (NC-2).
4. For each nonstandard or document-specific symbol used in a load-bearing claim (a theorem/proposition/lemma/corollary statement, a proof step it depends on, or a claim in the abstract or conclusion), locate its canonical definition. Flag a missing definition, or two or more definition sites that assign incompatible content (NC-1, BLOCKING). A second passage that only restates the same canonical meaning is not a finding.
5. Check declared relationships between names and alternate argument conventions under NC-3, using equivalences in the document as well as supplied aliases. Assess local names under NC-8 by their role and lookup cost, not by expression length or occurrence count alone.
6. At each load-bearing use, ask whether a reader could plausibly assign incompatible meanings: to a symbol under NC-4, including a competing parse prompted by established notation, and to a structural noun under NC-11.
7. For each symbol reused after a gap, check whether its canonical definition is still readily recoverable from local context; if not, flag for back-reference (NC-5).
8. Scan `\ref`, `\eqref`, `\autoref` for labels that do not match any defined `\label` in the document (NC-6).
9. Scan subscript/superscript conventions for the same family of objects; flag inconsistent mixtures (NC-7).
10. Produce a structured finding report.

## Rules

Each rule is tagged with a classification that sets a default severity: **invariant** — a violation is logically or structurally wrong — defaults to BLOCKING; **convention** — a strong norm with bounded exceptions — defaults to MINOR, escalating to BLOCKING when the violation obscures which meaning is canonical or creates a credible ambiguity in a load-bearing claim; **heuristic** — a review trigger requiring contextual judgement — defaults to ADVISORY, escalating per its own stated condition. A rule's own text overrides this default where it states a severity explicitly. When a defect triggers more than one rule, report each tag; the defect's severity for gating purposes is the maximum across triggered findings (BLOCKING > MINOR > ADVISORY > NOTE).

**NC-1 — Canonical-definition predicate.** *(invariant)*
Every nonstandard or document-specific symbol used in a load-bearing claim — a theorem/proposition/lemma/corollary statement, a proof step it depends on, or a claim in the abstract or conclusion — must have a locatable canonical definition somewhere in the document. Flag two failure modes: (a) *missing definition* — no definition site exists anywhere; (b) *incompatible competing definitions* — two or more definition sites assign the symbol different mathematical content. The predicate targets locating one canonical meaning per symbol, not counting textual definition occurrences: a second passage that restates the same canonical meaning without changing it is not a finding. Note: NC-1 governs existence and uniqueness of canonical meaning; `math-claim-integrity` rule R-J governs whether a symbol is defined *before* its first use in a theorem statement.

**NC-2 — No orphaned macros.** *(convention)*
Every macro defined in the LaTeX preamble via `\newcommand` or `\DeclareMathOperator` must appear at least once in the document body. A macro defined but never used is dead code that may represent a superseded notation — flag it for removal or documentation.

**NC-3 — One canonical term per concept.** *(convention)*
Every named mathematical concept must have one canonical term used consistently across the document. If an object is referred to by multiple names (a full name, an abbreviation, and a symbol), each name must appear in a declared-equivalence sentence ("we write R for the small-scale limit and abbreviate it SSL"). Without such a declaration, aliases are flagged as NC-3 findings. Cross-language aliases are a common revision artifact and fall under this rule: a concept defined with a term in the document's main language later referred to by an undeclared equivalent in another language (e.g., a defined Japanese term later written in English, or vice versa) is an NC-3 finding — unify to the defined term. Argument-convention variants of the same operator (F(X,t) in the definition vs F(tX) in a later section) are also NC-3 findings unless the second form is explicitly declared (e.g., tX as the rescaled object with F(tX) := F(X,t)). This rule works in tandem with `math-claim-integrity` rule R-I: R-I checks conceptual *correctness* of the name at introduction; NC-3 checks *consistency* of the name thereafter.

**NC-4 — No live ambiguity in a symbol's meaning.** *(heuristic)*
The same symbol must not carry two incompatible meanings within a live scope. The test: can the reader plausibly assign two different meanings to the same notation at the point of use? Common violations: r as both a continuous parameter and a discrete index while both are live; C as both a generic constant and a specific matrix in overlapping context; n as both dimension and index at once. Reuse in a scope that has genuinely closed (the earlier meaning is no longer live) is not a defect; explicit shadowing ("in this proof only, let r denote …") removes any remaining ambiguity outright. When assessing a live ambiguity, include an established meaning that the intended reader is likely to infer from the surrounding syntax. A local definition does not automatically prevent a credible competing parse, but resemblance to a conventional symbol alone is not a defect. Clarify the expression or rename only where that resolves an actual misreading; do not treat ordinary mathematical letters as globally reserved. Severity: MINOR when reuse creates a plausible misreading in a live scope; ADVISORY when disjointness is credible but arguable.

**NC-5 — Back-reference after a gap.** *(heuristic)*
A symbol's first reuse long after its definition is a review trigger, not a defect by itself. Flag the reuse when its canonical definition is no longer readily recoverable from local context at the point of reuse — e.g., enough intervening notation or subject matter that a reader would need to search back through the document. A short recap phrase ("with the notation of Definition 2.3", "the S of equation (3)") resolves the flag. Do not flag reuse solely because a fixed number of sections separates definition and reuse; recoverability, not section distance, is the trigger. Severity: MINOR when reuse is genuinely not recoverable from local context; no finding when it is.

**NC-6 — No dangling cross-references.** *(invariant)*
Every `\ref{label}`, `\eqref{label}`, `\autoref{label}` must resolve to a `\label{label}` defined elsewhere in the same document. After reordering sections or renaming theorem environments, dangling references are common (they produce "??" in the compiled PDF and may silently misdirect readers in draft form).

**NC-7 — Consistent subscript/superscript conventions.** *(convention)*
For a family of related objects, subscript and superscript placement must be consistent. Example: if eigenvalues are written λ_r in most places but λ^r in one section, flag the inconsistency. Similarly, ν_- and ν⁻ (minus as subscript vs. superscript) for the same object must be unified.

**NC-8 — Names must earn their lookup cost.** *(convention)*
A new name is useful when its conceptual role, reuse, or replacement of a genuinely unwieldy expression repays the cost of remembering its definition. Flag an alias that merely renames a readable expression and forces avoidable lookup. A short expression may deserve a name when it identifies a structural parameter, organises cases, or exposes a recurring relation. Repetition alone does not justify an alias, and a one-use name is not automatically wrong.

Compare the actual passages with and without the name. Do not impose a variable budget, display-count threshold or blanket requirement to inline expressions. Preserve the document's chosen function/index notation. Severity: MINOR; BLOCKING only when the notation also creates a credible ambiguity in a load-bearing claim.

**NC-11 — Structural nouns identify their contextual role.** *(convention)*
At a load-bearing use of a structural noun, the active context must make its referent and mathematical role recoverable. Flag competing live interpretations or a generic label that obscures the role actually used. Choose the precise noun per occurrence. Coordinate is the principal example; component, coefficient, entry, variable, index, factor and term illustrate the principle rather than define an exhaustive checklist.

Prior context can identify the space, basis, function or object. Do not require every sentence to repeat it, or flag clearly distinguished senses of a word merely because they coexist in a document. For a multi-index α, call α_k a component, not a coordinate: a tuple encoding or possible Euclidean embedding does not change its role in this argument.

Do not derive prose terms from identifier names or cited titles without checking their definitions and use. Preserve cited titles verbatim. For terminology migration use `math-semantic-preservation` MS-7 to classify occurrences before replacement. Severity: MINOR; BLOCKING in a statement or definition when the ambiguity affects what is claimed or defined.

## Examples

```
NC-1 (missing definition — undefined relation symbol in summary prose):
Conclusion: "the invariants are ordered I₁ ≺ I₂ ≺ I₃" — ≺ has no definition site
anywhere in the document.
Finding (BLOCKING): relation symbol ≺ used without a formal definition. Either define
         the order in the body, or replace with the explicit statement it abbreviates.
         Report the conclusion-level claim also to math-claim-integrity rule R-L.
```

```
NC-1 (incompatible competing definitions):
Section 2 (Definition 2.1): "let κ(X) denote the number of connected components of X"
Section 5 (used in Theorem 5.3's proof): "since κ(X) bounds the covering dimension of X"
         — the proof's argument only holds if κ(X) means the covering dimension
         defined nowhere else, contradicting Definition 2.1.
Finding (BLOCKING): κ has two incompatible meanings (component count vs. covering
         dimension). Rename one usage or reconcile which definition Theorem 5.3
         actually relies on.
```

```
NC-1 (must not flag — harmless explanatory restatement):
Section 2 (Definition 2.1): "let κ(X) denote the number of connected components of X"
Section 5: "recall that κ(X) counts the components of X, so κ(X) = 1 for connected X"
Finding: none — section 5 restates Definition 2.1's canonical meaning without changing
         it; this is not a second definition site.
```

```
NC-2:
Preamble defines: \newcommand{\Reals}{\mathbb R}
Body uses only:   \R (defined separately as \newcommand{\R}{\mathbb R})
Finding: \Reals is orphaned — defined but never used. Either remove \Reals or
         replace \R with \Reals for a single canonical macro.
```

```
NC-3 (accumulated aliases):
Section 2: "we write R for the small-scale limit"
Section 4: "the limit L(u) satisfies …"   (L(u) never declared equal to R)
Section 6: "the SSL value is …"           (SSL never declared)
Finding: Three aliases for the same quantity (R, L(u), SSL) without declared
         equivalence. Add a single declaration sentence and unify.
```

```
NC-3 (cross-language alias):
Section 2: 「条件 (3) を平衡条件と呼ぶ」
Conclusion: "the unbalanced case", "in the balanced regime"
Finding: 平衡/balanced and 非平衡/unbalanced are undeclared alias pairs for the same
         defined concept. Unify to the defined terms.
```

```
NC-4 (defect — same live scope):
Section 3, within one proof: "let r be the radius parameter fixed at the start of
this section" ... two paragraphs later, same proof: "let r index the eigenvalues
of A" — both meanings are live in the same argument.
Finding: r reused without explicit shadowing while the outer meaning is still live.
         Rename the index to ρ or add "in this step only, let r denote …".
```

```
NC-4 (must not flag — harmless reuse in a disjoint scope):
Section 1: r is defined as a continuous radius parameter, used throughout §1–2.
Section 3 (a self-contained lemma proof, §1–2's r never referenced again):
"let r be a root of the characteristic polynomial" — the proof neither uses nor
could be confused with the §1 radius, and the lemma's scope closes at proof's end.
Finding: none — §1's r is no longer live at the point of reuse, and the new r is
         confined to a proof that does not reference the earlier object.
```

```
NC-4 (conventional competing parse — flag):
A scalar constant Γ is defined earlier; a bound later reads "Γ(d+2) ≤ …".
The juxtaposition invites the Gamma-function reading despite the definition.
Finding (MINOR): write the product explicitly, Γ·(d+2), or rename the constant.
```

```
NC-4 (conventional letter — must not flag):
Γ is a clearly identified index set, and i is an ordinary summation index.
Finding: none — resemblance to the Gamma function or the imaginary unit alone
         is not a live ambiguity.
```

```
NC-5 (not recoverable — flag):
Definition 2.3 introduces S. Sections 3–6 develop unrelated machinery using
different notation throughout. Section 7 states "since S is nonempty, …" with no
recap and no notation shared with Definition 2.3's context.
Finding (MINOR): reuse of S in §7 is not locally recoverable — add "(the S of
         Definition 2.3)" or restate its defining property.
```

```
NC-5 (recoverable — must not flag):
Definition 2.3 introduces S in terms of a filtration {F_i} that section 4 (two
sections later) is still actively discussing using the same {F_i} notation; the
sentence reusing S reads "the resulting S, built from the same {F_i} as above, …".
Finding: none — the local context (shared {F_i} notation, explicit "as above")
         keeps Definition 2.3's meaning recoverable despite the section gap.
```

```
NC-6:
\eqref{eq:main-def} appears in section 4, but the label \label{eq:main-def} was
removed when the equation was merged into a displayed block labeled \label{eq:def}.
Finding (BLOCKING): dangling reference \eqref{eq:main-def} — update to \eqref{eq:def}.
```

```
NC-7:
Section 2: ν_- (subscript minus)   Section 5: ν⁻ (same quantity, superscript minus)
Finding: Inconsistent placement. Unify to the form matching the preamble macro.
```

```
NC-8 (harmful alias — flag):
b := a_n is introduced only to say b > 0, has no conceptual role and is
not reused.
Finding (MINOR): prefer a_n > 0 without changing the subscript notation.
```

```
NC-8 (useful short names — must not flag):
a := f(x)+t and b := f(y)+s are endpoint heights organising later intervals
and cases.
Finding: none — their conceptual role justifies the names.
```

```
NC-8 (no finding):
A function or sequence is consistently written c_i. Parenthesised function
application is possible but not required.
```

```
NC-8 (no blanket finding):
Two useful quantities have similar sums with different index sets.
Judge their meanings and the value of their names, not formula similarity.
```

```
NC-11 (generic label — flag):
"the coordinates of the multi-index α" — use "components", even though α
can be encoded as a tuple.
"change of feature coordinates" describes positive rescaling of individual
basis functions — name that rescaling instead of a broader generic operation.
"coordinate identity" is justified only by Coordinate in a Lean identifier —
describe the equality's actual mechanism, such as cancellation of row scaling.
```

```
NC-11 (must not flag):
Coordinates relative to a basis already identified in the active context;
chart coordinates; clearly distinguished vector and connected components.
```

## Output

Default: review-only. Produce a finding report listing:
- Rule tag (NC-1 to NC-8, NC-11)
- Classification (invariant / convention / heuristic — see Rules) and Severity: BLOCKING / MINOR / ADVISORY, following the default-severity mapping above unless the rule states otherwise
- Location: line number, section heading, or macro name
- One-sentence description
- Concrete fix suggestion

When the user asks to apply fixes: edit the LaTeX source in-place for NC-6 (dangling refs) and NC-7 (subscript unification) only — these are purely mechanical. For NC-1/NC-3/NC-4/NC-8/NC-11, produce a fix suggestion but do not edit without author confirmation, since renaming or removing notation requires author judgement and may require global replace.

## Quality Check

Before finishing, verify:
- NC-6 is checked against the *current* document's `\label` set, not a cached or partial read
- NC-2 findings distinguish unused macros from macros used only in other macros (a macro used only inside another `\newcommand` is technically "used" even if not directly in prose)
- NC-3 findings do not flag declared equivalences (where the author explicitly stated the alias)
- NC-1 findings do not merely count definition-phrase occurrences: a second passage restating the same canonical meaning is not a finding, only a genuinely incompatible second meaning is
- NC-4 findings turn on whether a competing meaning, including a credible conventional parse, is actually live at the point of use, not on whether the same character was ever reused anywhere in the document or resembles a standard symbol
- NC-5 findings turn on local recoverability, not on a fixed section-count gap
- Abbreviations earn their lookup cost; no display-count or function-notation prescription was imposed.
- NC-11 findings rest on contextual recoverability of the referent and role-appropriate wording, not on the coexistence of distinct senses of a word.

## Relationship to Other Skills

- Use `math-claim-integrity` for logical/structural issues: quantifier scope, theorem hierarchy, stale claims, proof/computation distinction. Rule R-I in that skill handles conceptual correctness of a symbol's *name at introduction*; NC-3 here handles consistency of that name *across the document*.
- Use `wabun-math-style` for Japanese-language anti-patterns.
- Use `deslop-prose` for prose inflation.
- NC-1 (existence/uniqueness of definition) complements `math-claim-integrity` rule R-J (defined-before-use in theorem statements): R-J checks completeness of theorem statements; NC-1 checks uniqueness of the definition site.
- NC-7 owns inconsistent typography for the same family of objects; `math-semantic-preservation` rule MS-6 owns an incorrect semantic reading of otherwise consistent notation (e.g. a family index described as a power).
