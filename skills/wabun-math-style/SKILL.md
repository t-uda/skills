---
name: wabun-math-style
description: Detect and correct Japanese-language anti-patterns in mathematical writing — epistemic hedges weakening proved claims, incorrect verb tense, passive/active confusion in proofs, ambiguous particles, unjustified 明らか, decorative connectives, redundant meta-discourse, double negation, stacked の, generic/general conflation, borrowed non-mathematical vocabulary, vague category names for explicit formulas, full-width semicolons or untranslated English, canonical-terminology drift, and translation-level concept conflation — without evaluating mathematical correctness or structural hierarchy.
---

# Wabun Math Style

A language-review skill for Japanese mathematics writing, field-agnostic in scope. It operates strictly at the language layer — epistemic certainty, tense and voice discipline, connective and particle logic, borrowed vocabulary and metaphor, vague category names, and concept-preserving terminology — and does not evaluate mathematical correctness, quantifier scope, theorem hierarchy, or proof/computation honesty. It consults definitions and a supplied source only to identify the concept a translation names; it does not validate the underlying mathematics.

## Design intent

This skill preserves explicit logical roles (implication, standing assumption,
case selection) in Japanese mathematical prose against a recurring failure
mode: language models flatten these roles into near-interchangeable connective
words such as `ならば`/`とき`/`場合`, and separately import unnatural literal
translations or decorative metaphors (e.g. `証人`, `機構`, `検出する`) that
obscure the actual mathematical object, relation, or proof step. Maintainer
note: see
[`docs/skill-rationales/math-writing.md`](https://github.com/t-uda/skills/blob/main/docs/skill-rationales/math-writing.md)
in the source repository for the full design rationale (maintenance-only; not
required runtime context and not shipped with installed copies).

## Use when

A Japanese mathematics paper, preprint, or lecture note (LaTeX with ltjsarticle, jarticle, or similar) needs language review against any of the patterns named in the frontmatter description and detailed under Rules below — epistemic hedges, tense/voice discipline, connective and particle logic, ならば/とき/場合 confusion, borrowed vocabulary and metaphor, 閉形式 misuse, terminology SoT drift, or translation-level concept conflation.

## Do not use / Boundaries

- Structural issues (theorem hierarchy, quantifier scope, proof/computation conflation, contribution-list inflation) — use `math-claim-integrity`.
- Symbol-table consistency, aliases, and definition locality — use `math-notation-consistency`. (JP-14's alias case cross-reports as NC-3.) JP-16 owns a conflict with a supplied terminology SoT; do not duplicate that conflict as NC-3.
- Language-agnostic prose inflation (hype, unsupported claims, decorative structure) — use `deslop-prose`; it composes with this skill rather than overlapping it.
- Removing process history from planning/notes documents — use `deslop-history`.

A wording pattern here may reveal a deeper claim defect; state which layer is actually broken rather than duplicating a finding across skills. Cross-report a distinct document-wide alias or definition-locality defect to `math-notation-consistency`, and a distinct claim-scope or truth-value defect to `math-claim-integrity`; JP-16/JP-17 own the terminology or translation event itself.

## Inputs

- `artifact` — the Japanese LaTeX source file or section range
- `register` — 論文 (formal paper), ノート (preprint/note), or 講義録 (lecture notes); conventions differ slightly
- `proof_sections` — proof environments where active-voice standards are strictest (optional; defaults to all \begin{proof}...\end{proof} blocks)
- `terminology_sot` — a supplied document or repository glossary that gives canonical terms and permitted aliases (optional)
- `source_artifact` — the English source text or corresponding source passages for a translation (optional)

## Rule classification and severity

Every rule carries one class, which fixes how its severity is derived:

- **invariant** — violating the rule misstates a proved claim's truth-value or is a conflation that produces a real logical/quantifier error; a defect wherever it occurs. Default BLOCKING; a rule may state a lower severity for a less consequential location, but never suppresses the finding.
- **convention** — a strong field norm with bounded, explicitly stated exceptions. BLOCKING within the context(s) the rule names (e.g. theorem statement, proof, abstract, contribution summary); MINOR outside that context; no finding when a stated exception applies.
- **heuristic** — requires contextual judgement using the rule's own stated test; severity follows that test's outcome.
- **advisory style** — a preference, never escalated beyond ADVISORY (JP-7 only).

Precedence when a span matches more than one rule tag: report every matching tag; the finding's headline severity is the maximum across matches (BLOCKING > MINOR > ADVISORY), ties broken by ascending rule number. Classification narrows *where* a rule applies at full force — it never erases the anti-pattern a rule targets; a convention can still produce a strong (BLOCKING) finding exactly where the rule says it obscures logical structure.

## Procedure

1. If `terminology_sot` is supplied, identify its canonical terms, scopes, and permitted aliases. If `source_artifact` is supplied, identify each source term from its definition, formula, and use before assessing its Japanese rendering.
2. Scan the artifact for each rule tag JP-1 through JP-17 (JP-10 is merged into JP-3), in the order listed under Rules.
3. For each match, determine class and severity per the mapping above, check stated exceptions before flagging, and record location, violation, and rewrite.
4. When JP-16 or JP-17 applies, record the relevant SoT, source, or definition evidence. Do not create a duplicate finding in another skill for the same terminology event.
5. Produce the structured finding report (see Output).
6. If asked to apply fixes, edit in place per Output's fix-mode instructions.

## Rules

**JP-1 (invariant) — Epistemic hedge ban on proved claims.**
〜と思われる, 〜と考えられる, 〜のように見える, 〜らしい, 〜と予想される, 〜はずである must not appear in theorem/proposition/lemma statements or prose summarizing what has been proved — misrepresenting a proved claim's certainty is a category error. Exception: permitted inside a `\begin{remark}` block that explicitly labels an unproved conjecture.

**JP-2 (convention) — Present-tense invariance for mathematical facts.**
Mathematical statements use present tense (〜する, 〜である, 〜が成り立つ, 〜が存在する). BLOCKING in theorem/proposition statements; MINOR elsewhere. Exceptions: historical attribution (「Euler は〜を示した」), referencing a step already completed earlier in the same proof.

**JP-3 (convention) — Proof-step voice discipline.**
Sentences that construct or advance an argument use active forms (〜を示す, 〜とおく, 〜が従う). Passive (〜が示された/〜が示されている) is for citing a result proved outside this proof. BLOCKING when the passive misattributes a result actually proved in this proof as if merely cited; MINOR otherwise. The stative citation register 〜が示されている／〜が証明されている with an external citation is always legitimate — never flag it.

**JP-4 (heuristic) — Connective discipline.**
すなわち restates the immediately preceding sentence and must not introduce a new deductive step; ゆえに/よって/したがって assert that the conclusion follows by logical necessity from what immediately precedes; つまり is informal restatement, appropriate in notes but not theorem proofs. Test: does the conclusion actually follow from the immediately preceding text? BLOCKING if not (a real logical gap); MINOR if the connective is merely used in the wrong register.

**JP-5 (heuristic) — Justify 明らか, 自明, 容易に.**
These require a same- or next-sentence justification or reference. Test: can a reader verify the claim without looking elsewhere? BLOCKING if verification needs a sign check, boundary condition, or multi-step substitution the reader cannot see; MINOR for milder unjustified compression.

**JP-6 (heuristic) — Redundant meta-discourse openers.**
本節では〜, 以下では〜, なお〜, ここでは〜 at a paragraph opening are MINOR findings only when the section/subsection heading already signposts the same content, i.e. deleting the opener loses no information. Not a density quota — one purposeful orientation sentence per section is fine.

**JP-7 (advisory style) — Particle が/は in theorem subjects.**
は marks an established topic; が marks new information or the logical subject of an existential claim (「X は存在する」 wrongly presupposes X; 「X が存在する」 correctly asserts existence). Always ADVISORY — choice is context-dependent and may be deliberate.

**JP-8 (convention) — Distinguish ならば, とき, and 場合 by context.**
Anti-pattern: collapsing logical implication, case selection, parameter regimes, and discourse transition into interchangeable ならば/とき/場合.
- *Theorem/proposition/lemma statements*: when a phrase silently carries the claim's logical antecedent, require explicit `A ならば B` (or an equivalent formal conditional); `このとき` is reserved for receiving already-introduced objects and standing assumptions. Anti-pattern: `X を…とする。A のとき B である。` where `A のとき` substitutes for `A ⟹ B`. Do not flag genuine case/regime labels (`n が偶数の場合`, `t > 0 のとき`, a named classification branch). Deciding test: does the phrase name a case under discussion, or silently carry the antecedent?
- *Proof context*: とき/場合 marking a case split or the current regime is valid. Flag tediously indirect progression that restates an already-available implication (`A ならば B である。いま A なので B である。`); prefer `A より B である。` or `補題 2.1 と A から B が従う。`. `A ならば B` is correct in a proof only when the implication itself is being proved, quoted, or isolated as a reusable subclaim — never require syllogistic restatement at every deduction.
- *Expository prose*: regime/comparison uses (`有限次元の場合`, `正則性を仮定しないとき`, `従来法を用いる場合`) remain valid unless the sentence is actually stating a theorem-like implication and obscures its antecedent/consequent.

Severity: BLOCKING when a theorem/proposition/lemma statement hides its antecedent this way, or a proof restates an available implication with full syllogistic redundancy across consecutive steps; MINOR for an isolated indirect phrasing in a proof; no finding for genuine case/regime/comparison uses in any context.

**JP-9 (convention) — Double-negation ban.**
〜でないとは言えない, 〜でないわけではない, 〜ないこともない read as hedged though logically equivalent to "possibly 〜". BLOCKING in theorem/proposition statements (replace with a direct affirmative or a precisely quantified partial statement); MINOR elsewhere.

**JP-11 (heuristic) — の-chain limit.**
A chain of four or more stacked の obscures the main predicate. MINOR; restructure into shorter nominal phrases or a predicate form.

**JP-12 (invariant) — Distinguish technical "generic" from 一般的な／一般の.**
"Generic" (outside a proper closed subset, outside a measure-zero set, or under an explicit non-degeneracy condition) must not be rendered 一般的な/一般の — those mean "general/typical," a non-technical qualification, and the conflation turns an outside-a-degenerate-subfamily claim into an apparent universal one. Use `generic な`, `一般位置の`, or spell out the non-degeneracy condition. BLOCKING in theorem statements, in the scope of a cited result, or where the generic/degenerate distinction is the introduction's main point; MINOR in expository or narrative framing. 一般の/一般的な remain correct for the non-technical sense ("for a general representative of the class").

**JP-13 (convention, strong) — Ban vocabulary and metaphors borrowed from outside mathematics.**
The test: would the word, with the same meaning and undefined, appear in a published Japanese mathematics journal article? If not, name the precise mathematical object or operation instead. Representative pairs (the rule targets the whole class):
- 証人 →「明示例」「具体例」「〜を満たす例」
- 模型（physics sense）→「例」「構成」
- 機構・装置・回路・エンジン・からくり・仕組み →「構成」「議論の構造」, or state the mechanism directly
- 異常・病理 →「退化した場合」「反例」
- 感知する・検出する（検出力を含む）→「区別する」「識別する」
- 層別（する・される, as a vague hierarchy/layering metaphor）→「分類」「階層」(only when the hierarchy is formally defined)
- 帳簿・台帳 →「計数」「対応」
- 余裕（as "margin" in an estimate）→ the relevant difference or strict inequality, stated directly
- 風景・地図・物語・旅・精神（"in the spirit of"）→ delete the metaphor; state the claim or make the analogy precise（「〜と同じ精神に立つ」→「〜の対応物である」）

`統計量` is not banned: valid for a genuine statistic in probability/statistics; flag it when used as a generic label for an arbitrary scalar quantity, invariant, score, or summary with no statistical meaning.

Narrow exceptions apply only when the term is established in the relevant field with that exact technical meaning, or is explicitly defined as a local technical term — e.g. 模型 in model theory, 検出 where detection is an established technical operation, 層別 in a recognised statistical procedure, or established terms sharing surface form with everyday/physics words (核, 流, スペクトル, 作用素, エネルギー法, 安定性). Never infer an exception from English usage or naturalness alone. BLOCKING in theorem statements, proofs, abstracts, and contribution summaries; MINOR elsewhere.

**JP-14 (convention) — No full-width semicolons; no untranslated English for defined Japanese terms.**
No「；」in Japanese prose (use 読点・句点, or split the sentence). A term the document defines in Japanese must not also appear in its English form (e.g. a defined 平衡条件 later written as balanced/unbalanced) — this is an undeclared alias; also report it as NC-3 to `math-notation-consistency`. Bare English adjectives (genuine, strict, …) qualifying Japanese nouns must be unpacked in Japanese. Terms the document itself introduces because no established Japanese translation exists (generic, well-posed) are exempt. MINOR for a semicolon; BLOCKING for an English alias of a defined term in a theorem statement or results summary.

**JP-15 (convention) — Ban the vague category name 閉形式 for formulas the document states explicitly.**
Test: does the document display the formula 閉形式 refers to? If yes, name the equation reference or call it 明示式 instead — 閉形式 forces the reader to guess where "closed" stops (elementary functions? rational expressions? finite sums?). Exemptions: closed differential forms (dω = 0) in differential geometry/de Rham theory; documents where closed-form solvability is itself the formally defined subject; cited titles (leave verbatim, do not change `\label{...}`). BLOCKING in theorem/proposition/lemma statements and titles, abstracts, and results summaries; MINOR elsewhere.

**JP-16 (convention) — Supplied terminology SoT has priority.**
When `terminology_sot` is supplied, use its canonical Japanese term and permitted aliases within its stated scope. Flag a local translation or alternate name that conflicts with that SoT. BLOCKING in theorem/proposition/lemma statements, abstracts, and results or contribution summaries; MINOR elsewhere. Do not flag an alias explicitly permitted by the SoT, a locally defined term that does not conflict with it, or compatibility-only Lean identifiers, LaTeX macros, labels, and citation keys. If the SoT conflicts with a definition or formula in the artifact, or with `source_artifact`, do not choose a replacement from the SoT: report one JP-17 semantic conflict instead, not both JP-16 and JP-17.

**JP-17 (invariant) — Preserve concept identity under translation.**
Identify a source term from its definition, formula, and use before translating it. Flag any rendering that collapses distinct mathematical concepts or operations into one Japanese term, assigns a name inconsistent with the defined concept, or invents a technical Japanese term for a source expression that identifies only an ordinary organisational role. This also applies without `source_artifact`: if `terminology_sot` conflicts with a definition or formula in the Japanese artifact, report that semantic conflict rather than mechanically choosing either label. A source term whose own label contradicts its definition is likewise a JP-17 finding; report the source-side naming inconsistency rather than translating the label. Every JP-17 finding is BLOCKING. Do not flag established Japanese technical terms used with their established meaning, English or katakana retained because no natural Japanese term is established, or an explicitly defined local technical term that preserves the identified concept and does not conflict with the supplied SoT. JP-17 owns the translation or source-naming event; cross-report only a separate document-wide alias/definition-locality defect to `math-notation-consistency` or a separate claim-scope/truth-value defect to `math-claim-integrity`.

## Examples

Decisive, non-obvious branches only — see Rules above for the full statement of each rule.

```
JP-3, legitimate citation passive — do not flag:
[12] により補題の条件が満たされていることが示されている。
```

```
JP-8, theorem-level anti-pattern:
Before: X を固定する。A のとき B である。
After:  X を固定する。このとき、A ならば B である。
```

```
JP-8, valid proof case split — do not flag:
n が偶数の場合、f(n) は次で与えられる。n が奇数の場合、…
```

```
JP-8, proof made tediously indirect:
Before: A ならば B である。いま A なので B である。
After:  A より B である。
```

```
JP-12, technical-generic conflation:
Before: 一般的な行列では固有値はすべて単純である。（判別式の零点集合の外で成り立つ generic な主張のつもりで書いた場合）
After:  generic な行列では固有値はすべて単純である。
```

```
JP-13, undefined metaphor to flag:
Before: 不変量 I の検出力は完全に層別される。
After:  不変量 I が区別する対象対の全体は、定理 6.5 の条件により特徴づけられる。
```

```
JP-13, established field-specific term — do not flag:
模型論において、この理論の任意の模型は可算飽和である。
（模型 = model theory's technical term for "model"; not the generic-translation anti-pattern）
```

```
JP-15, exempt differential form — do not flag:
ω は閉形式である（dω = 0）。
```

```
JP-17, source label inconsistent with its definition — flag:
Source: a simplex's threshold of entry into a filtration is called "birth value".
Before: 単体の誕生値を a とする。
Report: the defined concept is a filtration value, not a homology-class birth;
        correct the source name before choosing a Japanese rendering.
```

```
JP-17, distinct operations collapsed — flag:
Before: simplicial collapse と filtration-preserving reduction をともに「簡約」と呼ぶ。
After:  simplicial collapse は「単体崩壊」，filtration-preserving reduction は「フィルトレーションを保つ簡約」と呼び分ける。
```

```
JP-16, supplied SoT conflict — flag:
terminology_sot: simplex threshold = 「フィルトレーション値」
Before: 主定理では単体の生成値を用いる。
After:  主定理では単体のフィルトレーション値を用いる。
```

```
JP-17, invented technical literal translation — flag:
Source: "theorem layer" means only a grouping of theorem statements.
Before: 定理層を以下で示す。
After:  以下では，定理を確立済みの結果と条件付きの結果に区分する。
```

```
JP-16/JP-17, legitimate terminology — do not flag:
Do not flag established Japanese technical terms such as 「層」 in sheaf theory,
「核」 of a linear map, or 「台」 of a function or measure.
Do not flag `generic` when retaining English is more natural than an invented
Japanese rendering.
Do not flag an explicitly defined local technical term that does not conflict
with the SoT.
Do not flag Lean identifiers, LaTeX macros, labels, or citation keys retained
for compatibility.
```

## Output

Default: review-only. Produce a structured finding report listing:
- Rule tag (JP-1 through JP-17, skipping JP-10 which is merged into JP-3) and class
- Severity: BLOCKING / MINOR / ADVISORY, per the classification mapping above
- Location: environment label (e.g. `\begin{theorem}[thm:main]`), proof section, or paragraph identifier
- One-sentence description of the violation
- A concrete rewrite suggestion in Japanese

For a JP-17 terminology conflict — a source-side name or terminology SoT that contradicts a definition — replace the Japanese rewrite with the relevant source or SoT location, the definition evidence, and the required source-term or glossary repair. Do not invent a Japanese rendering before that repair. In fix mode, edit the source or terminology SoT only when it is supplied and in scope; otherwise leave the Japanese artifact unchanged and report the external repair needed.

When asked to apply fixes: edit the LaTeX source in place. Preserve all mathematical content, macro names, and theorem labels. Append a change log with rule tag, location, and before/after text.

## Quality Check

Before finishing, verify:
- JP-1 findings mark only proved claims, not open problems in remark/conjecture environments
- JP-3 findings never flag the legitimate citation passive
- JP-8 findings distinguish theorem/proof/exposition and pass the deciding test (case-label vs. silent antecedent) before flagging; genuine case/regime/comparison uses are never flagged in any context
- JP-13 findings respect the narrow established-term exceptions and the 統計量 genuine-statistic exception, and are never based on English naturalness alone
- JP-15 findings exempt the differential-form sense, closed-form-as-subject documents, and cited titles
- JP-16 findings compare only against a supplied SoT, honor its permitted aliases and scope, and defer a SoT-to-definition conflict to one JP-17 finding
- JP-17 findings identify the concept from a definition, formula, or source use before assessing its name; this includes a SoT-to-definition conflict when no `source_artifact` is supplied, preserves established technical terms, and never duplicates the same event in `math-notation-consistency` or `math-claim-integrity`
- Severities follow the classification mapping (§ Rule classification and severity), with deterministic precedence when multiple tags match one span
- No finding belongs to `math-claim-integrity` territory (quantifier scope, theorem hierarchy, proof/computation distinction). JP-14's English-alias case stays a finding of this skill (with its additional NC-3 cross-report to `math-notation-consistency`) — do not suppress it as out-of-territory
