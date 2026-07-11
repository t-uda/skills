---
name: wabun-math-style
description: Detect and correct Japanese-language anti-patterns in mathematical writing — epistemic hedges weakening proved claims, incorrect verb tense, passive/active confusion in proofs, ambiguous particles, unjustified 明らか, decorative connectives, redundant meta-discourse, double negation, stacked の, generic/general conflation, borrowed non-mathematical vocabulary (証人・機構・検出・層別・統計量 and the like), vague category names for explicit formulas (閉形式), and full-width semicolons or untranslated English mixed into Japanese prose — without evaluating mathematical correctness or structural hierarchy.
---

# Wabun Math Style

A language-review skill for Japanese mathematics writing. It targets the class of errors that arise specifically in Japanese mathematical prose: epistemic hedges that misrepresent proved claims as uncertain, tense inconsistencies in theorem statements, voice confusion in proof steps, connectives that mark logical steps without logical warrant, bare 明らか/自明/容易に without justification, redundant meta-discourse openers, は/が particle ambiguity in theorem subjects, ならば/とき confusion in conditional hypotheses, double-negation hedging, and の-chains that obscure the main predicate. The skill is field-agnostic: the rules apply to any area of mathematics. It operates strictly at the language layer and does not evaluate mathematical correctness, quantifier scope, theorem hierarchy, or proof/computation honesty.

## Design intent

This skill preserves explicit logical roles (implication, standing assumption,
case selection) in Japanese mathematical prose against a recurring failure
mode: language models flatten these roles into near-interchangeable connective
words such as `ならば`/`とき`/`場合`, and separately import unnatural literal
translations or decorative metaphors (e.g. `証人`, `機構`, `検出する`) that
obscure the actual mathematical object, relation, or proof step. Maintainer
note: see
[`../../docs/skill-rationales/math-writing.md`](../../docs/skill-rationales/math-writing.md)
for the full design rationale (maintenance-only; not required runtime
context).

## Use when

- A Japanese mathematics paper or preprint (LaTeX with ltjsarticle, jarticle, or similar) needs language review
- Theorem statements or proof steps contain epistemic hedges (〜と思われる, 〜と考えられる) that weaken what should be unconditional mathematical assertions
- Connectives (すなわち, ゆえに, よって, したがって) appear without marking genuine logical steps
- Meta-discourse openers (本節では, 以下では) appear redundantly where the section heading already provides orientation
- Verb forms are inconsistent — past tense for timeless mathematical facts, or mixed passive/active in the same proof
- 明らか / 自明 / 容易に appear bare, without adjacent justification
- A sentence has four or more stacked の, obscuring the main predicate
- 「一般的な」or 「一般の」is used as a translation of the technical term "generic" (holds outside a proper closed subset or measure-zero set) — conflation with the non-technical "general"
- Vocabulary borrowed from physics, engineering, statistics, or machine learning (証人, 模型, 機構, 装置, 異常, 感知, 検出, 統計量, 層別, 帳簿, 病理, 余裕 …) appears in mathematical prose
- 「閉形式」(closed form) is used as a category name for a formula that the document states explicitly — instead of naming the formula by equation reference or calling it 明示式
- Full-width semicolons 「；」appear in Japanese prose, or English words (balanced, genuine, strictness …) are mixed in where a defined Japanese term exists

## Do not use

- For structural issues (theorem hierarchy, quantifier scope errors, proof/computation conflation) — use `math-claim-integrity`
- For symbol-table consistency — use `math-notation-consistency`
- For general prose inflation that is not Japanese-specific — use `deslop-prose`
- For removing process history from planning documents — use `deslop-history`

## Inputs

- `artifact` — the Japanese LaTeX source file or section range
- `register` — 論文 (formal paper), ノート (preprint/note), or 講義録 (lecture notes); conventions differ slightly
- `proof_sections` — proof environments where active-voice standards are strictest (optional; defaults to all \begin{proof}...\end{proof} blocks)

## Procedure

1. Scan for epistemic hedge phrases (JP-1); flag each against the claim it modifies.
2. Scan for verb tense in theorem and proposition statements (JP-2).
3. Scan proof environments for passive-voice proof steps (JP-3, which subsumes JP-10).
4. Scan every occurrence of すなわち, ゆえに, よって, したがって (JP-4); verify each signals a deductive step.
5. Scan for 明らか / 自明 / 容易に (JP-5); check for adjacent justification.
6. Scan for redundant meta-discourse openers at paragraph and section boundaries (JP-6).
7. Scan theorem subjects for が/は ambiguity patterns (JP-7, advisory).
8. Scan lemma hypotheses for ならば vs とき/場合 (JP-8).
9. Scan for double-negation patterns (JP-9).
10. Scan for の-chains of length ≥4 (JP-11).
11. Scan for 「一般的な」/「一般の」used in a technical-generic sense (JP-12).
12. Scan for borrowed non-mathematical vocabulary and metaphors (JP-13).
13. Scan for full-width semicolons and untranslated English terms with defined Japanese equivalents (JP-14).
14. Scan every occurrence of 閉形式 (JP-15); classify as vague category name vs. exempt established term.
15. Produce a structured finding report.

## Rules

**JP-1 — Epistemic hedge ban on proved claims.**
The phrases 〜と思われる, 〜と考えられる, 〜のように見える, 〜らしい, 〜と予想される, 〜はずである must not appear in theorem statements, propositions, lemma statements, or in prose that summarizes what has been proved. In proof environments, they are permitted only inside a \begin{remark}...\end{remark} block that explicitly labels an unproved conjecture. This is the highest-priority rule: an epistemic hedge on a proved claim is a category error that misrepresents the paper's results to the reader.

**JP-2 — Present-tense invariance for mathematical facts.**
Mathematical statements assert timeless truths and use present tense: 〜する, 〜である, 〜が成り立つ, 〜が存在する. Past tense (〜した, 〜であった, 〜が成り立った) is permitted only for: (a) historical attribution (「Euler は〜を示した」), (b) referencing a specific step completed earlier in the same proof (「前節で示したように」). Flag past-tense verbs in theorem and proposition statements.

**JP-3 — Proof-step voice discipline (active for construction; passive only for citation).**
Within a proof, sentences that construct or advance the argument must use active constructions: 〜を示す, 〜とおく, 〜を用いると, 〜が従う, 〜が成り立つ. The passive 〜が示された / 〜が示されている, 〜が証明された / 〜が証明されている is appropriate only to cite a result proved outside this proof (e.g., in a prior lemma or external paper). The stative/resultative forms 〜が示されている and 〜が証明されている are the natural citation register in formal Japanese mathematical writing (e.g., 「[12] により〜が示されている」) and are explicitly permitted alongside the perfective forms. Using passive voice for the conclusion of a proof step that was just carried out here (e.g., 「ゆえに P が示された」 at the end of a proof that proved P) is acceptable only if the result was actually established by citing an external source; otherwise prefer 「ゆえに P が成り立つ」 or 「以上で P を示した」. Note: this rule subsumes the passive-scope restriction; no separate rule for 受動態 is needed.

**JP-4 — Connective discipline.**
Each logical connective must signal exactly what it claims:
- すなわち: restatement or clarification of the immediately preceding sentence. Must NOT introduce a new deductive step.
- ゆえに / よって: conclusion follows by logical necessity from what immediately precedes. Must NOT be used as a mere rhetorical transition or section introduction.
- したがって: same logical role as よって, more formal register; do not mix both in the same proof without a register reason.
- つまり: informal restatement; appropriate in notes but not in theorem proofs.

Flag any sentence beginning with ゆえに/よって/したがって that does not actually follow from the immediately preceding text — this marks a logical gap, not merely a style issue.

**JP-5 — Justify 明らか, 自明, 容易に.**
These words must be followed (in the same sentence or the immediately following sentence) by a one-clause justification or a reference (e.g., 「（補題 2.2 より）」, 「（定義から直接）」). Flag bare uses with no adjacent justification. The test: can a reader verify the claim without looking elsewhere? If the answer involves checking a sign inequality, boundary condition, or multi-step substitution, the claim is not 明らか.

**JP-6 — Flag redundant meta-discourse openers.**
Flag 本節では〜, 以下では〜, なお〜, ここでは〜 at paragraph openings ONLY when the content is already signposted by the section or subsection heading, or when deleting the opener loses no information (「本節では f の性質を述べる。」 before a section titled 「f の性質」 is redundant). Do NOT enforce a density quota; one purposeful orientation sentence per section is acceptable. Replace redundant openers with a direct mathematical statement.

**JP-7 — Particle が/は in theorem subjects (advisory).**
In theorem statements: は marks the subject as the established topic (contrasting with alternatives); が marks the subject as new information or the logical subject of an existential claim. Common error: using は when introducing a new object for the first time, or は in an existential claim (「X は存在する」 reads as "as for X, it exists," implying X is already introduced; 「X が存在する」 correctly asserts existence of a new X). This is an advisory finding (severity: MINOR), not a blocking error, because は/が selection is context-dependent and may be deliberately chosen for emphasis.

**JP-8 — ならば for conditional lemma hypotheses.**
In lemma and theorem statements, conditional hypotheses must use ならば (or the equivalent formal conditional structure P ⟹ Q), not とき or 場合, which can be read as temporal. 「P のとき Q が成り立つ」 is acceptable in informal notes but may be ambiguous; 「P ならば Q が成り立つ」 is unambiguous for a logical conditional. Exception: do NOT flag とき/場合 when it introduces a genuine case-split or parameter range (e.g., 「t > 0 のとき」, 「n が偶数の場合」). Flag JP-8 only when とき/場合 connects a logical hypothesis to a conclusion (P のとき Q が成り立つ, where P is a logical condition, not a range label or case header).

**JP-9 — Double-negation ban.**
Patterns 〜でないとは言えない, 〜でないわけではない, 〜ないこともない are logically equivalent to "possibly 〜" but read as hedged. In mathematical writing, replace with a direct affirmative (「〜である（場合がある）」) or a precise partial statement with explicit quantification. Double negatives in theorem statements are almost always artifacts of draft hedging; eliminate them.

**JP-11 — の-chain limit.**
A chain of four or more stacked の (possessive/genitive markers) obscures the main predicate and the logical relationships between constituents. Example: 「解の一意性の証明の方針の説明を与える」 should be broken into shorter nominal phrases or rewritten with a predicate. Flag any の-chain of length ≥4 and suggest a restructured phrase.

**JP-12 — Distinguish technical "generic" from 一般的な／一般の.**
The technical term "generic" (holds outside a proper closed subset, outside a measure-zero set, or under an explicit non-degeneracy condition) must NOT be expressed as 「一般的な」 or 「一般の」. Those Japanese words mean "general / typical / widely applicable" — a non-technical qualification — and do not carry the algebro-geometric or measure-theoretic precision of "generic." Conflation creates a logical error: 「一般的な X では P が成立する」 reads as "P holds for a typical/arbitrary X" (i.e., universally), whereas the intended claim is "P holds for X outside a specific degenerate subfamily."

Correct substitutes:
- **technical generic** → 「generic な」(recommended: preserves the term, unambiguous), or 「一般位置の」(for algebraic-geometry-style general-position conditions), or an explicit description of the non-degeneracy condition
- **technical non-generic** → 「非 generic な」, 「退化した」(when degeneracy is the focus), or 「特殊な（対称性の高い）」(when special structure is the focus)
- **non-technical general** → 「一般の」, 「一般的な」 remain correct for "for a general [arbitrary representative of the class]"

Severity: BLOCKING when the conflation appears in theorem statements, in the scope of a cited result, or in the introduction when the distinction between the generic and degenerate case is the main point. MINOR in expository prose or narrative framing.

**JP-13 — Ban vocabulary and metaphors borrowed from outside mathematics.**
Pure-mathematics prose must not use loanwords from physics, engineering, statistics, or machine learning, nor narrative or anthropomorphic metaphors. The test: would the word appear, with the same meaning and without a definition, in a published Japanese mathematics journal article? If not, replace it with the precise mathematical object or operation. Representative pairs (the rule targets the whole class, not only this list):
- 証人（witness）→「明示例」「具体例」「〜を満たす例」
- 模型（model, physics sense）→「例」「構成」
- 機構・装置・回路・エンジン・からくり・仕組み →「構成」「議論の構造」, or delete and state the mechanism directly
- 異常・病理 →「退化した場合」「反例」
- 感知する・検出する（検出力を含む）→「区別する」「識別する」
- 統計量 →「不変量」「量」
- 層別（する・される）→「分類」「階層」(only when the hierarchy is formally defined)
- 帳簿・台帳（bookkeeping）→「計数」「対応」
- 余裕（as a translation of "margin" in an estimate）→「差」, or state the inequality directly
- 風景・地図・物語・旅・精神（"in the spirit of"）→ delete the metaphor; state the claim or the analogy precisely（e.g., 「〜と同じ精神に立つ」→「〜の対応物である」 with the correspondence made explicit）

Do NOT flag established mathematical terms whose surface form coincides with everyday or physics words: 核 (kernel), 流 (flow), スペクトル, 作用素, エネルギー法 (when citing the named method), 安定性. Severity: BLOCKING in theorem statements, abstracts, and introductions; MINOR elsewhere.

**JP-14 — No full-width semicolons; no untranslated English for defined Japanese terms.**
Japanese mathematical prose must not use the full-width semicolon 「；」. Express parallelism or contrast with 読点・句点 or by splitting the sentence, and end enumerate items with 句点. A concept the document defines with a Japanese term must not also be used in its English form (e.g., a defined 平衡条件 later written as balanced / unbalanced) — this creates an undeclared alias; report it also as NC-3 to `math-notation-consistency`. English adjectives such as genuine or strict must not qualify Japanese nouns bare; unpack the intended condition in Japanese（e.g., 「genuine な極」→「分子が同時に零にならない極」）. Terms the document itself introduces because no established Japanese translation exists (e.g., generic, well-posed) are exempt. Severity: MINOR for semicolons; BLOCKING for an English alias of a defined Japanese term in a theorem statement or summary of results.

**JP-15 — Ban the vague category name 閉形式 for formulas the document states explicitly.**
「閉形式」(closed form) is a category name that does not say *which* form: each use forces the reader to guess where the boundary of "closed" lies (elementary functions? rational expressions? finite sums?). When the document displays the formula the word points to, that guess is unnecessary — point to the equation number or call it 明示式. The test: does the document display the formula the word refers to? If yes, the category name is strictly less informative than the reference. Replacement guide:
- Noun use naming the formula（「X の閉形式」）→「X の明示式」 plus an equation reference（「X の明示式 \eqref{eq:...}」）, or the equation itself / equation number alone
- 「同一の閉形式 X をもつ」→ state what coincides（「同一パラメータから定まる同一の X」,「明示式 \eqref{…} により同一の X」）
- Adverbial use（「閉形式で確認する／計算する／一致する」）→「明示的に計算して確認する」「直接計算により」「明示式 \eqref{…} として一致する」
- In theorem/proposition/lemma titles（「[X の閉形式]」）→「[X の明示式]」; do not change `\label{...}` identifiers

Exemptions: (a) closed differential forms（\(d\omega=0\)）in differential geometry and de Rham theory — an established term; nearby mentions of exact forms or cohomology are the cue; (b) documents where closed-form solvability is itself the subject and 「閉形式」 is formally defined (differential Galois theory, Liouville-style elementary-function theory); (c) cited titles and theorem names — leave verbatim. Severity: BLOCKING in theorem/proposition/lemma statements and titles, abstracts, and summaries of results; MINOR elsewhere.

## Examples

```
Before（JP-1）: したがって I は X と Y を区別すると考えられる。
After:          したがって I は X と Y を区別する（系 2.3）。
```

```
Before（JP-2）: A(t) は正則行列であった。
After:          A(t) は正則行列である。
```

```
Before（JP-3）: ゆえに補題 2.1 の条件が満たされたことが示された。
After:          ゆえに補題 2.1 の条件が満たされる。
                （または，外部結果を引用した場合：「[12] により条件が満たされていることが示されている。」）
```

```
Before（JP-4）: したがって，次節では Fourier 分解を導入する。
After:          （削除；節の遷移は見出しで十分）
```

```
Before（JP-5）: 不等式 (4) が成立することは明らかである。
After:          不等式 (4) は両辺を比較して直ちに従う（補題 2.2）。
```

```
Before（JP-6）: 本節では f の性質を述べる。f を次で定義する。[section heading: "f の性質"]
After:          （「本節では…」の行を削除）f を次で定義する。
```

```
Before（JP-8）: P のとき Q が成り立つ。（補題の仮説として）
After:          P ならば Q が成り立つ。
```

```
Before（JP-9）: この場合，f が u に依存しないとは言えない。
After:          この場合，f は u に依存する可能性がある。
                （または確定している場合：「この場合，f は u に依存する。」）
```

```
Before（JP-11）: 解の一意性の証明の方針の説明を与える。
After:           解の一意性の証明方針を述べる。
```

```
Before（JP-12）: 一般的な行列では固有値はすべて単純である。
                 （判別式の零点集合の外で成り立つ generic な主張として書いた場合）
After:           generic な行列では固有値はすべて単純である。
```

```
Before（JP-13）: この例の組が定理の証人である。
After:          この例の組が定理の主張を満たす明示例である。
```

```
Before（JP-13）: 不変量 I の検出力は完全に層別される。
After:          不変量 I が区別する対象対の全体は，定理 6.5 の条件により特徴づけられる。
```

```
Before（JP-14）: 等号は unbalanced な場合に実現する；他の場合は balance が成り立つ。
After:          等号は平衡条件を満たさない場合に実現する。他の場合は平衡条件が成り立つ。
```

```
Before（JP-15）: \begin{proposition}[母関数の閉形式]\label{prop:closed}
After:          \begin{proposition}[母関数の明示式]\label{prop:closed}
                （ラベルは変更しない）
```

```
Before（JP-15）: この状況を閉形式で確認する。
After:          この状況を明示的に計算して確認する。
```

```
Exempt（JP-15）: ω は閉形式である（dω = 0）。 — closed differential form; do not flag.
```

## Output

Default: review-only. Produce a structured finding report listing:
- Rule tag (JP-1 through JP-15, skipping JP-10 which is merged into JP-3)
- Severity: BLOCKING (epistemic hedge on proved claim, logical-gap connective) / MINOR (verb tense, meta-discourse) / ADVISORY (JP-7 only)
- Location: environment label (e.g., `\begin{theorem}[thm:main]`), proof section, or paragraph identifier
- One-sentence description of the violation
- A concrete rewrite suggestion in Japanese

When the user asks to apply fixes: edit the LaTeX source in-place. Preserve all mathematical content, macro names, and theorem labels. Append a change log with rule tag, location, and before/after text.

## Quality Check

Before finishing, verify:
- JP-1 findings mark only proved claims, not open problems in remark/conjecture environments
- JP-3 findings do not flag the legitimate citation passive (〜が示されている, 〜が証明されている + external citation)
- JP-5 findings include the rewrite suggestion, not just a flag
- JP-7 findings are all marked ADVISORY
- JP-13 findings do not flag established mathematical terms that share surface form with everyday or physics words (核, 流, スペクトル, …) — the test is published-journal usage
- JP-14 findings exempt terms the document itself introduces without an established Japanese translation
- JP-15 findings do not flag 閉形式 in the differential-form sense (dω = 0), in documents where closed-form solvability is itself the formally defined subject, or inside cited titles
- No finding belongs to `math-claim-integrity` territory (quantifier scope, theorem hierarchy, proof/computation distinction)

## Relationship to Other Skills

- Use `math-claim-integrity` for structural and logical quality issues (quantifier scope, theorem hierarchy, proof/computation honesty, stale claims).
- Use `math-notation-consistency` for symbol drift, orphaned macros, and alias detection.
- Use `deslop-prose` for language-agnostic prose inflation (hype, decorative structure, claim-evidence mismatch). Note: `deslop-prose` is language-agnostic; `wabun-math-style` handles Japanese-specific patterns that `deslop-prose` does not target.
- Use `deslop-history` when a planning or notes document leaks process history or prior-draft residue.
