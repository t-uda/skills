---
name: math-notation-consistency
description: Audit a LaTeX mathematics document for notation drift — symbols used under different names across sections, orphaned macros, undeclared aliases (including cross-language pairs such as 平衡/balanced), symbols or relation signs used with no definition site anywhere, symbol reuse across scopes, and first-use-after-gap without back-reference — without evaluating mathematical correctness or prose style.
---

## Use when

- A LaTeX math paper has been through multiple revisions and may have notation drift (same object referred to by two names in different sections)
- A symbol or operator appears in a theorem but its definition is not clearly locatable
- Two LaTeX macros in the preamble appear to define the same object (e.g., `\R` and `\Reals` both for ℝ)
- A macro is defined in the preamble but never used in the document
- A named concept (e.g., "small-scale limit", "SSL", "L(u)", "R") has multiple aliases without a declared equivalence
- A symbol introduced in section 2 reappears in section 5 with no reminder of its definition
- The same symbol is used for two different objects (e.g., r as a parameter in one section and as an index in another)
- A relation symbol or operator (e.g., ≺) appears only in the abstract or conclusion with no definition site anywhere in the body
- A defined Japanese term and an English word are used interchangeably for the same concept (e.g., 平衡 vs balanced/unbalanced), or the same operator is written with two argument conventions (e.g., Mag(X,t) vs Mag(tX))

## Do not use

- For evaluating whether a notation choice is mathematically optimal or conventional — this skill checks internal consistency, not external convention
- For quantifier scope errors, theorem hierarchy, or proof/computation distinction — use `math-claim-integrity`
- For Japanese-language anti-patterns — use `wabun-math-style`
- For prose inflation — use `deslop-prose`

## Inputs

- `artifact` — the LaTeX source file (full document preferred; section range accepted)
- `preamble` — the LaTeX preamble (if separate; otherwise included in artifact)
- `known_aliases` — a list of intentional synonyms the author has declared equivalent (optional; if omitted, any alias is flagged)

## Procedure

1. Extract all `\newcommand`, `\renewcommand`, `\DeclareMathOperator` definitions from the preamble; build a macro-definition table.
2. Extract all first-use-in-prose definitions (e.g., 「\(p_r = |S_r|^2\) と書く」, 「\(X\) を有限距離空間とする」); note section and location.
3. For each macro in the definition table, check whether it appears in the document body; flag unused macros (NC-2).
4. For each mathematical symbol appearing in a theorem statement or proof, check that it has a formal definition site earlier in the document (NC-1).
   Also scan the abstract and conclusion for symbols — especially relation symbols such as ≺, ⊏ — that have no definition site anywhere in the document (NC-1, BLOCKING).
5. Scan for multiple names applied to the same object (NC-3); compare against `known_aliases` if provided.
6. Scan for the same symbol applied to different objects across the document's live scopes (NC-4).
7. For each symbol whose definition site and first re-use are separated by more than one section, flag for back-reference check (NC-5).
8. Scan `\ref`, `\eqref`, `\autoref` for labels that do not match any defined `\label` in the document (NC-6).
9. Scan subscript/superscript conventions for the same family of objects; flag inconsistent mixtures (NC-7).
10. Produce a structured finding report.

## Rules

**NC-1 — One formal definition site per symbol.**
Every mathematical symbol used in the document must have exactly one formal definition site: either a `\newcommand` in the preamble with a corresponding prose definition in the body, or an explicit inline definition ("let X denote…", "〜を X とおく"). A symbol with two definition sites (e.g., re-defined partway through the paper) is flagged BLOCKING. Note: NC-1 governs the *existence and uniqueness* of the definition; `math-claim-integrity` rule R-J governs whether a symbol is defined *before* its first use in a theorem statement.

**NC-2 — No orphaned macros.**
Every macro defined in the LaTeX preamble via `\newcommand` or `\DeclareMathOperator` must appear at least once in the document body. A macro defined but never used is dead code that may represent a superseded notation — flag it for removal or documentation. Severity: MINOR.

**NC-3 — One canonical term per concept.**
Every named mathematical concept must have one canonical term used consistently across the document. If an object is referred to by multiple names (e.g., "small-scale limit", "SSL", "L(u)", and "R" all for the same quantity), each name must appear in a declared-equivalence sentence ("以下では R = lim_{t→0+} |tX| を小スケール極限と呼ぶ"). Without such a declaration, aliases are flagged as NC-3 MINOR findings. Cross-language aliases are a common revision artifact and fall under this rule: a concept defined with a Japanese term (平衡条件) later referred to by an undeclared English word (balanced / unbalanced), or vice versa, is an NC-3 finding — unify to the defined term. Argument-convention variants of the same operator (Mag(X,t) in the definition vs Mag(tX) in a later section) are also NC-3 findings unless the second form is explicitly declared (e.g., tX as the scaled space with Mag(tX) := Mag(X,t)). This rule works in tandem with `math-claim-integrity` rule R-I: R-I checks conceptual *correctness* of the name at introduction; NC-3 checks *consistency* of the name thereafter.

**NC-4 — No symbol reuse across scopes.**
The same symbol (same LaTeX command or same rendered character) must not be used for two different mathematical objects within any live scope. Common violations: r used as both a continuous parameter and a discrete index; C used as both a constant and a specific matrix; n as both dimension and an index. When a symbol is deliberately reused in a new scope (e.g., a local variable in a proof), the new introduction must explicitly shadow the old one ("この証明中のみ r を〜とおく").

**NC-5 — Back-reference after section gap.**
When a symbol is first defined in section M and reused in section N where N ≥ M+2, the first reuse in section N should include a back-reference to the definition (e.g., "（定義 2.3 の記号を用いる）", "（式 (3) の S_r）"). Flag first-reuse sites that lack any back-reference. Severity: MINOR. The gap threshold is two or more sections (not two pages or two paragraphs).

**NC-6 — No dangling cross-references.**
Every `\ref{label}`, `\eqref{label}`, `\autoref{label}` must resolve to a `\label{label}` defined elsewhere in the same document. After reordering sections or renaming theorem environments, dangling references are common. Severity: BLOCKING (since they produce "??" in the compiled PDF and may silently misdirect readers in draft form).

**NC-7 — Consistent subscript/superscript conventions.**
For a family of related objects, subscript and superscript placement must be consistent. Example: if eigenvalues are written λ_r in most places but λ^r in one section, flag the inconsistency. Similarly, ν_- and ν⁻ (minus as subscript vs. superscript) for the same object must be unified. Severity: MINOR.

## Examples

```
NC-1 example (undefined relation symbol in summary prose):
Conclusion: 「不変量は magnitude ≺ ν₋ ≺ σ ≺ 等長型 と並ぶ」 — ≺ has no definition
site anywhere in the document.
Finding (BLOCKING): relation symbol ≺ used without a formal definition. Either define
         the order in the body, or replace with the explicit implication it abbreviates
         (「隣接する各対について，前者が一致し後者が異なる配置対が存在する」).
         Report the conclusion-level claim also to math-claim-integrity rule R-L.
```

```
NC-2 example:
Preamble defines: \newcommand{\Reals}{\mathbb R}
Body uses only:   \R (defined separately as \newcommand{\R}{\mathbb R})
Finding: \Reals is orphaned — defined but never used. Either remove \Reals or
         replace \R with \Reals for a single canonical macro.
```

```
NC-3 example:
Section 2: 「small-scale limit を R と書く」
Section 4: 「小スケール極限 L(u) は…」  (using L(u) without declaring it equals R)
Section 6: 「SSL の値として…」           (using SSL without declaring it equals R)
Finding: Three aliases for the same quantity (R, L(u), SSL) without declared equivalence.
         Add: 「本稿では R = L(u) = lim_{t→0+} |tX| を小スケール極限 (SSL) と呼ぶ。」
```

```
NC-3 example (cross-language alias):
Section 2: 「条件 2μ₁ = (n−1)(α+β) を平衡条件と呼ぶ」
Conclusion: 「unbalanced な組により実現する」「balanced 計量における極」
Finding: 平衡/balanced and 非平衡/unbalanced are undeclared alias pairs for the same
         defined concept. Unify to the defined terms 平衡／非平衡（平衡条件を満たさない）.
```

```
NC-4 example:
Section 1: r ∈ ℤ/nℤ is defined as the Fourier index (continuous parameter over n values)
Section 3: "let r be a root of the characteristic polynomial" (r as a fresh variable)
Finding: r reused without explicit shadowing. In section 3, rename to ρ or add
         「この証明中のみ r を特性多項式の根とおく」.
```

```
NC-6 example:
\eqref{eq:magnitude-def} appears in section 4, but the label \label{eq:magnitude-def}
was removed when the equation was merged into a displayed block labeled \label{eq:mag}.
Finding (BLOCKING): dangling reference \eqref{eq:magnitude-def} — update to \eqref{eq:mag}.
```

```
NC-7 example:
Section 2: ν_- (negative inertia index, subscript minus)
Section 5: ν⁻ (same quantity, minus as superscript)
Finding: Inconsistent placement. Unify to ν_- (subscript) throughout, matching the
         \nm macro definition in the preamble.
```

## Output

Default: review-only. Produce a finding report listing:
- Rule tag (NC-1 through NC-7)
- Severity: BLOCKING (NC-1 multi-definition, NC-6 dangling refs) / MINOR (NC-2, NC-3, NC-5, NC-7) / ADVISORY (NC-4 when shadowing is arguable)
- Location: line number, section heading, or macro name
- One-sentence description
- Concrete fix suggestion

When the user asks to apply fixes: edit the LaTeX source in-place for NC-6 (dangling refs) and NC-7 (subscript unification) only — these are purely mechanical. For NC-1/NC-3/NC-4, produce a fix suggestion but do not edit without author confirmation, since renaming a symbol requires global replace.

## Quality Check

Before finishing, verify:
- NC-6 is checked against the *current* document's `\label` set, not a cached or partial read
- NC-2 findings distinguish unused macros from macros used only in other macros (a macro used only inside another `\newcommand` is technically "used" even if not directly in prose)
- NC-3 findings do not flag declared equivalences (where the author explicitly stated the alias)
- NC-4 findings do not flag standard multi-use notation (e.g., i as imaginary unit in one context and index in another within separate, non-overlapping sections) — only flag within a live scope

## Relationship to Other Skills

- Use `math-claim-integrity` for logical/structural issues: quantifier scope, theorem hierarchy, stale claims, proof/computation distinction. Rule R-I in that skill handles conceptual correctness of a symbol's *name at introduction*; NC-3 here handles consistency of that name *across the document*.
- Use `wabun-math-style` for Japanese-language anti-patterns.
- Use `deslop-prose` for prose inflation.
- NC-1 (existence/uniqueness of definition) complements `math-claim-integrity` rule R-J (defined-before-use in theorem statements): R-J checks completeness of theorem statements; NC-1 checks uniqueness of the definition site.
