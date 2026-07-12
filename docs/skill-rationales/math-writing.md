# Design rationale: mathematical-writing skills

Maintenance-only document. It is not runtime skill context and is not copied into
installed skill directories; it exists so a maintainer or reviewer can recover why
a rule exists without reconstructing issue history.

Covers three skills:

- `skills/wabun-math-style/SKILL.md`
- `skills/math-notation-consistency/SKILL.md`
- `skills/math-claim-integrity/SKILL.md`

Original implementation: PR [#118](https://github.com/t-uda/skills/pull/118).
Latest semantic revision: [#149](https://github.com/t-uda/skills/issues/149).
Future semantic rewrites need their own issue. This document
preserves *design intent*; it must not silently weaken any target behaviour or
drop any "Protected behaviour" clause when edited.

## 1. `wabun-math-style`: implication, cases, and discourse roles

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

## 2. `wabun-math-style`: unnatural Japanese literal translations and AI metaphors

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
relevant field and used with that exact technical meaning, or when the paper
explicitly defines it as a local technical term — e.g. `模型` in model theory,
`統計量` for a genuine statistic in probability/statistics, `検出` where
detection is an established technical operation in that field, `層別` in an
established technical expression (e.g. a recognised statistical procedure). Do
not infer an exception from English usage alone.

### Special handling of `統計量`

`統計量` should not be banned categorically — it is valid for a genuine
statistic. Flag it when used as a generic label for an arbitrary scalar
quantity, invariant, score, or summary with no statistical meaning.

### Protected behaviour

Future maintainers must not reinterpret JP-13 as a generic ban on
interdisciplinary concepts. Its purpose is to reject unnatural Japanese
literal translations and decorative AI metaphors while preserving established
Japanese technical terminology.

## 3. `wabun-math-style`: canonical terminology and concept-preserving translation

### Originating failure mode

A translation can be linguistically fluent and still alter the mathematics. A
model may translate an unsuitable English label literally, flatten distinct
operations into one Japanese term, ignore a repository glossary, or invent a
technical-sounding Japanese noun where the source names only an ordinary
organisational role.

### Identify the concept before translating its label

Definitions, formulas, and use determine the concept; an English label is not
decisive evidence. If a source calls a simplex filtration threshold a "birth
value" even though it is not homology-class birth, the review must report that
source-side inconsistency rather than endorse `誕生値`. Natural English is not
enough to justify a literal Japanese translation.

### Terminology SoT is authoritative but not infallible

When a document or repository supplies a glossary, it controls canonical
Japanese wording and permitted aliases in its scope. The reviewer must not
introduce a local alternative. A glossary does not override a conflicting
definition, however, whether the definition is in the Japanese artifact or a
supplied source: report the conflict and resolve the terminology at its source
rather than mechanically replacing the prose.

### Preserve distinctions and established usage

Distinct concepts and operations must retain distinct names in Japanese. This
is a semantic requirement, not a stylistic preference. Conversely, do not ban
established Japanese mathematics terms such as `層`, `核`, or `台`, and retain
English or katakana where that is the field's established usage. Local terms
are valid when explicitly defined and consistent with the supplied SoT.

### Ownership boundary

`wabun-math-style` owns a SoT conflict and translation-level concept
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

## 6. Relationship among the three skills

Ownership boundaries to preserve:

- `wabun-math-style` owns Japanese linguistic form, connective roles,
  unnatural Japanese translation patterns, terminology SoT conflicts, and
  translation-level concept identity.
- `math-notation-consistency` owns document-level symbol identity, aliases,
  definition locality, and notation reuse.
- `math-claim-integrity` owns claim structure, proof/evidence boundaries,
  result hierarchy, and contribution hierarchy.

A wording pattern may reveal a deeper claim defect, but a finding should state
which layer is actually broken instead of duplicating the same rule across all
three skills.
