# Design rationale: mathematical-writing skills

Maintenance-only document. It is not runtime skill context and is not copied into
installed skill directories; it exists so a maintainer or reviewer can recover why
a rule exists without reconstructing issue history.

Covers the Japanese mathematical-writing family and its semantic neighbours:

- `skills/wabun-math/SKILL.md`
- `skills/wabun-math-theorem/SKILL.md`
- `skills/wabun-math-style/SKILL.md`
- `skills/wabun-math-terminology/SKILL.md`
- `skills/math-writing-preferences/SKILL.md`
- `skills/math-notation-consistency/SKILL.md`
- `skills/math-claim-integrity/SKILL.md`
- `skills/math-semantic-preservation/SKILL.md`

Original implementation: PR [#118](https://github.com/t-uda/skills/pull/118).
Terminology revision: [#149](https://github.com/t-uda/skills/issues/149).
Japanese-writing split and evidence contract: [#201](https://github.com/t-uda/skills/issues/201).
`math-semantic-preservation` added: [#153](https://github.com/t-uda/skills/issues/153).
Future semantic rewrites need their own issue. This document
preserves *design intent*; it must not silently weaken any target behaviour or
drop any "Protected behaviour" clause when edited.

## 1. `wabun-math-theorem` and `wabun-math-style`: implication, cases, and discourse roles

### Originating failure mode

AI-generated Japanese mathematical prose often flattens distinct logical and
discourse roles — logical implication, introduction of standing assumptions,
case selection, parameter regimes, proof progression, and comparison with prior
work — into near-interchangeable connective words: `ならば`, `とき`, `場合`. The
result is formally plausible Japanese whose logical structure is difficult to
recover.

### Theorem-level anti-pattern

In theorem, proposition, and lemma statements, the logical antecedent and
consequent should be explicit.

Clear intended form:

```text
X を固定する。このとき、A ならば B である。
```

Here `このとき` receives the object and standing assumptions introduced before
it, and `A ならば B` states the actual implication.

Clear anti-pattern:

```text
X を固定する。A のとき B である。
```

when `A のとき` is merely substituting for the implication `A → B`. The problem
is not that every occurrence of `とき` is forbidden — it is that theorem-level
implication has been hidden inside a case-like phrase.

### Valid theorem-level uses of `とき` and `場合`

Do not flag genuine parameter regimes or cases, for example: `n が偶数の場合`,
`t > 0 のとき`, `境界を含む場合と含まない場合`. The deciding question is whether
the phrase names a case under discussion or silently carries the theorem's
antecedent.

### Proof context

Inside proofs, `とき` and `場合` usually have stronger case-split or
current-regime roles. Conversely, repeatedly restating an already available
implication can make the proof indirect and tedious. Natural proof
progression: `A より B である。` or `補題 2.1 と A から B が従う。` A
potentially tedious progression: `A ならば B である。いま A なので B である。`
Use `A ならば B` in a proof when the implication itself is being proved,
quoted, or isolated as a reusable subclaim — do not require full syllogistic
restatement at every deduction.

### Expository prose

In introductions and comparison prose, `とき` and `場合` often correctly
describe a regime or relative position (`有限次元の場合`, `正則性を仮定しない
とき`, `従来法を用いる場合`). These remain valid unless the sentence is actually
presenting a theorem-like implication and obscures its antecedent/consequent
structure.

### Protected behaviour

Future compression or generalisation must preserve the ability to distinguish
theorem statements, proofs, and exposition. The rule must not collapse into
either bad extreme: globally replacing every `とき`/`場合` with `ならば`, or
allowing `A のとき B` everywhere because it is colloquially understandable.

## 2. `wabun-math-terminology`: unnatural Japanese literal translations and AI metaphors

### Originating failure mode

Language models repeatedly import English mathematical or technical wording
into Japanese through unnatural literal translation. The corresponding English
concept may be legitimate, but the Japanese expression is often alien to
mathematical papers, semantically vague, or metaphorical where the text should
name a concrete object or relation. The rule targets Japanese mathematical
usage and must not be weakened merely because the English source expression
sounds natural.

### Strong default anti-patterns

The following remain strong default findings when unexplained in theorem
statements, proofs, abstracts, or contribution summaries: `証人`, `模型` (as a
generic translation of "model" rather than an established technical term),
`機構`, `装置`, `回路`, `エンジン`, `からくり`, `仕組み`, `異常`, `病理`,
`感知する`, `検出する`, `層別` (as a vague hierarchy/layering metaphor), `帳簿`,
`台帳`, `余裕` (when substituting for a quantitative difference or strict
inequality), `風景`, `地図`, `物語`, `旅`, `精神`. These words commonly hide the
mathematical content instead of expressing it.

### Typical repairs

- `この不変量は差異を検出する` → `この不変量は指定された二つの対象を区別する`
- `証明の機構` → identify the actual map, estimate, induction, decomposition, or
  correspondence
- `評価式には余裕がある` → state the relevant difference, bound, or strict
  inequality
- `反例の証人` → identify an explicit example, element, counterexample, or
  object satisfying the required property

### Narrow technical-term exceptions

A narrow exception applies when the Japanese term is established in the
relevant field and used with that exact technical meaning — e.g. `模型` in model theory,
`統計量` for a genuine statistic in probability/statistics, `検出` where
detection is an established technical operation in that field, `層別` in an
established technical expression (e.g. a recognised statistical procedure). Do
not infer an exception from English usage alone. Issue #201 removes the former
local-definition shortcut: defining a Japanese label locally does not establish
its usage or authorize an invented translation. Preserve the definition's
mathematical meaning while resolving its name through evidence.

### Special handling of `統計量`

`統計量` should not be banned categorically — it is valid for a genuine
statistic. Flag it when used as a generic label for an arbitrary scalar
quantity, invariant, score, or summary with no statistical meaning.

### Protected behaviour

Future maintainers must not reinterpret JP-13 as a generic ban on
interdisciplinary concepts. Its purpose is to reject unnatural Japanese
literal translations and decorative AI metaphors while preserving established
Japanese technical terminology.

## 3. `wabun-math-terminology`: canonical terminology and concept-preserving translation

### Originating failure mode

A translation can be linguistically fluent and still alter the mathematics. A
model may translate an unsuitable English label literally, flatten distinct
operations into one Japanese term, ignore a repository glossary, or invent a
technical-sounding Japanese noun where the source names only an ordinary
organisational role.

### Identify the concept before translating its label

Definitions, formulas, and use determine the concept; an English label is not
decisive evidence. If a source identifies a simplex filtration threshold with
homology-class birth, report that concept conflict rather than endorse `誕生値`.
The shared English word alone does not establish a conflict: simplex entry is
also called birth time in [Cavanna, Jahanseir and Sheehy, Section 2](https://arxiv.org/html/1506.03797v1#S2).
Preserve genuinely distinct scoped uses, while requiring separate evidence for
their Japanese renderings. Natural English is not enough to justify a literal
Japanese translation.

### Terminology SoT is authoritative but not infallible

When a document or repository supplies a glossary, it controls project canonical
wording and permitted aliases in its scope, subject to external evidence of
Japanese usage. The reviewer must not introduce an unsupported local alternative.
A project editorial choice is not proof that another attested term is wrong. A glossary does not override a conflicting
definition, however, whether the definition is in the Japanese artifact or a
supplied source: report the conflict and resolve the terminology at its source
rather than mechanically replacing the prose.

### Preserve distinctions and established usage

Distinct concepts and operations must retain distinct names in Japanese. This
is a semantic requirement, not a stylistic preference. Conversely, do not ban
established Japanese mathematics terms such as `層`, `核`, or `台`, and retain
English or katakana where that is the field's established usage. All terminology
operations require research into meaning and Japanese usage, or reuse of a
matching inspected record. If completed research finds no established Japanese
translation, retain English; do not invent provisional Japanese or unsupported
katakana. Preserve local definitions without treating them as usage evidence.
Inaccessible research is unresolved evidence, not a completed negative search.

### Ownership boundary

`wabun-math-terminology` owns a SoT conflict and translation-level concept
conflation. `math-notation-consistency` owns a separate document-wide alias or
definition-locality defect; `math-claim-integrity` owns a separate claim-scope
or truth-value defect. Do not emit duplicate findings for one terminology
event.

## 4. `math-notation-consistency`: canonical definitions and live scope

### Originating failure modes

The skill was created to catch document-level notation degradation: a
document-specific symbol used in a theorem or conclusion with no locatable
definition; the same object acquiring multiple undeclared aliases across
revisions; a symbol silently changing meaning within a live scope;
cross-language name drift; a relation sign appearing in the abstract or
conclusion without a definition in the body; old notation reappearing after a
long gap with no locally recoverable meaning; dangling LaTeX references and
orphaned macros.

### Meaning of the canonical-definition rule

The original strong wording around "one definition site" was intended to
force the agent to locate a canonical meaning and detect incompatible
redefinition — it was not intended to count every textual occurrence of a
definition phrase. The desired operational principle:

> Every nonstandard or document-specific symbol used in a load-bearing claim
> has a locatable canonical definition. Flag missing definitions and
> incompatible competing definitions.

This preserves pressure against undefined symbols and silent redefinition
without filling the skill with obvious exception lists.

### What must remain strong

Undefined document-specific symbols in load-bearing claims; incompatible
competing definitions; undeclared aliases for the same object; cross-language
or argument-convention drift; same-symbol reuse that creates a credible
ambiguity within a live scope; dangling references.

### Scope behaviour

The live-scope concept should remain central. The audit should not treat the
entire paper as one undifferentiated namespace, but the skill also should not
accumulate a long catalogue of ordinary local-variable exceptions. The key
question is whether the reader can plausibly assign two incompatible meanings
to the same notation at the point of use.

### Back-reference after a gap

A long section gap is a review trigger, not a defect by itself. The
underlying failure is that language models often revive a symbol after
substantial intervening material without restoring enough local context for
the reader. Flag when the old definition is no longer readily recoverable
from the local context — do not require a mechanical back-reference solely
because two section numbers differ by a fixed amount.

### Protected behaviour

A rewrite must continue to catch undefined and conflicting document-specific
notation. It must not weaken the skill into a generic suggestion to "check
context," nor turn it into a mechanical count of definition occurrences.

## 5. `math-claim-integrity`: theorem inflation and contribution inflation

### Originating failure mode

Language models produce many intermediate mathematical results and tend to
promote all of them because each consumed substantial reasoning or token
budget. This creates papers containing many theorem-like statements and long
contribution lists with little hierarchy. The reader then cannot determine
which result is the main scholarly contribution, which statements are proof
infrastructure, which claims are routine consequences, which results are
examples/computations/reformulations, and which contribution-list items are
merely different granularities of the same result. The skill must preserve a
visible distinction between main results and supporting machinery.

### Theorem hierarchy is functional, not merely nominal

The rule is not based on a simplistic claim that every theorem is important
and every proposition is minor. Evaluate the result's function: Does it carry
independent scholarly significance? Is it advertised by the title, abstract,
or introduction? Is it independently reusable or citable? Is it used solely as
input to another main result? Is it an immediate corollary, routine
calculation, worked example, or known-result reformulation? Does its
environment name and presentation match that role? A result used solely as
proof infrastructure should normally be a lemma or proposition and should not
be presented as an independent main theorem unless a concrete independent
significance is stated. This remains a strong paper-structure finding even
though the mathematical statement itself may be true.

### Contribution-list anti-pattern

A common AI-generated contribution list treats all obtained outputs as
parallel achievements — e.g. one main theorem, two lemmas used only in its
proof, a direct corollary, a numerical example, and a reformulation of a known
result, listed as five independent contributions. This is not merely verbose
prose; it materially misrepresents the paper's scholarly hierarchy.

### Required contribution mapping

For every main contribution item, require an identifiable relation to: the
corresponding formal result; the incumbent or prior baseline; the concrete new
gain; the reason the item is independently significant; whether it duplicates
another item at a different level of granularity. Unless independent
significance is established, the following should not appear as parallel main
contributions: infrastructure lemmas, routine corollaries, direct
computational observations, worked examples, known-result reformulations,
several proof components of one main result counted separately. Recommend
moving such material to a proof, remark, example, auxiliary proposition, or
omission, as appropriate.

### Important exception

An intermediate result may remain theorem-level when it has independent
significance, independent reuse, or value beyond its role in the main proof.
The skill should evaluate that role rather than demote results mechanically by
environment name.

### Protected behaviour

Future edits must not reduce theorem hierarchy or contribution hierarchy to
cosmetic naming preferences. The skill exists to prevent flat, inflated
presentations of AI-generated results and to make the paper's genuine
scholarly contribution legible.

## 6. `math-semantic-preservation`: meaning-preserving mathematical edits

### Originating failure mode

Live review of a large mathematical prose corpus exposed edits that were
linguistically smoother, internally consistent, and mechanically valid while
no longer describing the same mathematics. Representative failures: the third
argument of a trilinear form described as the third factor of a two-factor
tensor product; an almost-everywhere assertion rewritten as apparent pointwise
equality; composition with a continuous linear map renamed "pushforward";
convolution described as an operation performed separately at each point; a
restriction operation conflated with the restricted object; one overloaded
term replaced uniformly although its occurrences denoted a Fourier truncation
residual, an out-of-box coefficient sum, an orthogonal residual, a
physical-space exterior part, and eventual sequence behaviour; a superscript
index read as a power; a statement, proof explanation, link label, glossary,
and audit record edited inconsistently for one concept; a property attributed
to the wrong structure while the final conclusion stayed superficially
plausible. These are semantic-preservation defects, not prose-style defects.

### Ownership boundary

`math-claim-integrity` owns whether a claim is supported at the strength its
proof establishes; `math-notation-consistency` owns document-wide notation
bookkeeping; `wabun-math-terminology` JP-16/JP-17 own terminology SoT conflicts and
translation or source-naming events. `math-semantic-preservation` owns whether
an edit, monolingual paraphrase, terminology migration, or explanatory
description preserves the semantic content fixed by its source anchor. One
defect is reported at exactly one layer — the layer whose invariant is
actually broken. MS-7 retains occurrence classification and concept-cluster
synchronization; `wabun-math-terminology` researches and records Japanese term
choices. Both reuse the same record rather than duplicate searches or findings.

### Compact live examples

Maintenance evidence and realistic validation material (full
`owner/repository#number` form; not copied into the runtime skill):

- `uda-lab/lean-pde-notes#51` — source proofreading campaign; umbrella context
  for the mathematically unsafe paraphrases and migrations reviewed.
- `uda-lab/lean-pde-notes#55` — the overloaded Japanese 尾部 problem that
  motivated a corpus-wide terminology decision over mechanical replacement.
- `uda-lab/lean-pde-notes#56` — explicit terminology decision and
  classification task distinguishing Fourier truncation residuals, out-of-box
  coefficient sums or families, orthogonal residuals, physical-space exterior
  parts, and eventual sequence behaviour; primary live example for MS-7.
- `uda-lab/lean-pde-notes#57` — MS-2 and MS-4 examples: composition described
  as pushforward; time convolution described as if points were convolved; a
  definition sentence completed only once its data and predicate were explicit.
- `uda-lab/lean-pde-notes#58` — MS-1, MS-3, MS-5, MS-7 examples: trilinear-form
  argument confused with a tensor factor; an a.e. representative statement
  rewritten with an unclear pointwise referent; mechanical replacements
  introducing pseudo-technical wording; an audit ledger recording wording
  different from the change it documented.
- `uda-lab/lean-pde-notes#59` — MS-2 and MS-7 examples: restriction to a ball
  complement separated from the resulting exterior part; the canonical pair
  球内部分/球外部分 kept synchronized; migration completed with glossary and
  lint protection while compatibility-only identifiers containing `tail` were
  intentionally retained.

### Protected behaviour

Future compression or generalisation must preserve the following:

1. Natural language fluency must never be treated as evidence that
   mathematical meaning was preserved.
2. Definitions, formulas, types, and uses outrank labels and identifier names
   as semantic evidence.
3. Terminology migrations must classify occurrences before replacement.
4. Pointwise, almost-everywhere, eventual, and uniform statements must remain
   distinct.
5. Argument positions, tensor factors, coordinates, indices, and exponents
   must remain distinct.
6. Operations must remain distinct from their results.
7. Related human-facing descriptions of one concept must be synchronized
   without requiring compatibility identifiers to be renamed.
8. The skill must not become a general theorem prover or duplicate Japanese
   style, notation bookkeeping, or paper-level claim-integrity review.

## 7. Ownership across the writing skills

Ownership boundaries to preserve:

- `wabun-math` routes by passage role and terminology task without repeating rules.
- `wabun-math-theorem` owns Japanese wording within explicitly structured
  definitions, lemmas, propositions, theorems, corollaries, proofs and remarks,
  including explicit Markdown equivalents. It excludes narrative prose.
- `wabun-math-style` owns narrative Japanese prose and the shared Japanese
  language and default drafting references used by structured blocks.
- `wabun-math-terminology` owns evidence-backed terminology selection,
  unnatural Japanese calques, terminology SoT conflicts and translation-level
  concept identity across both passage types.
- `math-writing-preferences` holds scoped personal natural-number/index
  conventions for drafting, translation and revision in all languages; it does not define general review defects.
- `math-notation-consistency` owns document-level symbol identity, aliases,
  definition locality, and notation reuse.
- `math-claim-integrity` owns claim structure, proof/evidence boundaries,
  result hierarchy, and contribution hierarchy.
- `math-semantic-preservation` owns semantic fidelity of edits, paraphrases,
  explanatory descriptions, and terminology migrations against their semantic
  anchor.

A wording pattern may reveal a deeper claim defect, but a finding should state
which layer is actually broken instead of duplicating the same finding across
skills.


## 8. Issue #201 migration and preservation decisions

The split moves rules and examples to one owner rather than copying the old
monolithic skill. Shared runtime files stay inside installed skill directories;
this maintenance document is not a runtime dependency. Companion skills are
separately installed or resolved from an available catalog.

### Historical rule correspondence

| Former rule | Current owner and disposition |
| --- | --- |
| JP-1 | Style's shared `references/language.md`, used by theorem and narrative style; judge sentence role, including proved summaries, clear definitions, proof goals and explicitly identified conjecture/interpretation. |
| JP-2 | Shared language reference; retain present-tense norm, BLOCKING in theorem/proposition statements, MINOR elsewhere, and historical/completed-proof-step exceptions. |
| JP-3 | Theorem; keep construction/progression distinct from external citation and protect legitimate stative citation passives. |
| JP-4 | Shared language reference; retain immediate restatement/inference test and register norm. The immediately preceding text can invoke existing assumptions or results. |
| JP-5 | Theorem; retain same-/next-sentence justification or reference and visible sign/boundary/substitution checks; coordinate with proof exposition. |
| JP-6 | Narrative style; retain heading-redundancy test, purposeful orientation and proof signposts; general metadiscourse stays in `deslop-prose`. |
| JP-7 | Deleted as approved; no replacement particle audit. The old claim that an existential topic with `は` inherently presupposes existence was false. |
| JP-8 | Theorem for structured statements/proofs; narrative style retains implication clarity and genuine regime/comparison uses. Preserve explicit antecedents, standing assumptions, legitimate cases and direct proof progression. |
| JP-9 | Theorem, narrowed as approved to unnecessary proof double negation with the logical-equivalence exception; retain proof-context MINOR severity. Rhetorical guard phrases use existing `deslop-prose` coverage. |
| JP-10 | Already merged into JP-3; remains retired. |
| JP-11 | Style's shared language reference; retain four stacked `の` test and MINOR severity across passage roles. |
| JP-12 | Terminology; always inspect technical `generic`, retain English and reject `一般位置の` as its translation. Preserve nontechnical general/typical uses. |
| JP-13 | Terminology plus `references/usage.md`; preserve every individual recurrence example and established-usage exception, including shorthand and genuine statistics. Local definition no longer substitutes for usage evidence. |
| JP-14 | Semicolon ban in shared language reference; lexical aliases/adjectives/English retention in terminology. Macro-generated-English inspection deleted. Report one terminology alias defect; NC-3 covers only a distinct notation-wide defect. |
| JP-15 | Terminology; preserve strong ban on vague `閉形式` where an explicit formula or equation reference expresses the intended content, its severities and all three exemptions. |
| JP-16–17 | Terminology; evidence contract governs project choices, source/definition conflicts and English retention. No invented-Japanese/local-definition workaround. |
| JP-18 | Shared language reference; quantities use Arabic numerals, lexical items remain, style alone stays MINOR. |
| JP-19 | Absorbed into `deslop-prose` redundant-explanation guidance with MINOR severity and informative-clarification exceptions; no dedicated natural-number notation prescription. |
| JP-20 | Theorem; mandatory universal-assertion/arbitrary-selection wording norm, including recoverable meanings, preserving quantifier order and dependencies. Not an optional personal preference. |
| JP-21 | Theorem's Japanese realization of PE-1; preserve pre-branch announcement, branch labels and explicit closure with existing severities. |
| JP-22–24 | Style's shared `references/drafting.md`, applied by default to new prose, translation and requested stylistic rewrites; never review findings solely from the words used. |
| JP-25 | Shared language reference; recoverability and purposeful reference, no distance or frequency cutoff, existing ambiguity severities. |
| JP-26 | Terminology; a multi-index has components even with tuple representation; preserve actual chart/basis-coordinate usage and NC-11 boundary. |

Unsettled first-batch proposals were resolved conservatively for implementation:
JP-2's severity, JP-4's locality/register test, JP-5's placement test, JP-6's
heading test and JP-11's count threshold remain. The count threshold is retained
behavior, not a newly established empirical criterion. No rule was weakened on
an unsupported claim that current models no longer need it.

### Drafting and personal conventions

JP-23 retains a concrete recurrence-prevention purpose: formal systems such as
Lean make conventions and technical scaffolding explicit, and their prose
translations can mechanically narrate that scaffolding. Prefer `空和は0である`
or `空和は0だから` to unnecessary provenance/definition procedure. Preserve the
fact and reasoning needed in the empty case, nonstandard conventions,
consequential boundary conditions and every necessary argument. Clear uses of
`規約` are not defects. JP-22's order/enumeration preference and JP-24's
construction wording likewise remain drafting defaults, not review findings.

The personal convention uses `N = {0, 1, 2, ...}` and
permits `0 行目`, `0 列目`, `0 番目`, “row 0”, “column 0” and “zeroth” in
all languages. Explanations and translations must preserve mathematics, code
and array indices without silently adding 1. This strong preference applies automatically when trusted context establishes the user
as uda/t-uda OR the target repository owner is t-uda/uda-lab. A known user needs
no repository; a matching repository needs no matching user. Unknown identity
is not presumed to match; other contexts require an explicit request. It is not a general
mathematical-correctness test and does not authorize silently changing a source's
mathematics or judging another author's convention mathematically wrong.

### Evidence and validation limits

The first-ten rules originate collectively in #117 / PR #118. JP-8's later
role refinements are documented in #126, #131, #132 and PR #137. Individual
originating failure logs and responsible models have not been identified for
the other first-ten rules. Current-model effectiveness and the effect of
removing JP-7 are unmeasured.

Before/after size measurements establish compression, not semantic equivalence.
Focused behavioral checks should cover citation passives, existing-context
justifications, proof signposts, case/regime roles, necessary negation,
quantifier wording, source/glossary conflicts, all JP-13 cases, English
retention, evidence-unavailable versus negative-search outcomes, zero-based
translation and concise empty-case proofs. Keep test results separate from
claims about general model efficacy.
