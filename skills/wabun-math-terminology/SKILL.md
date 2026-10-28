---
name: wabun-math-terminology
description: Research, select, translate and audit Japanese mathematical terminology, and create or update glossaries, across structured blocks and narrative prose. Require inspected evidence for meaning and established Japanese usage, or reuse a matching verified record; retain English when no standard Japanese translation is found.
---

# Wabun Math Terminology

Apply to every terminology operation, including terms introduced while drafting and existing terms under review. Read [usage cases](references/usage.md) for the specific recurring vocabulary and its exceptions. These examples are inspection triggers, not a verified translation dictionary.

## Evidence workflow

1. Identify each concept from its definition, formulas, field and use. Classify different senses before selecting terms. A source label or identifier is not sufficient evidence.
2. Research both mathematical meaning and established Japanese usage, or reuse an inspected record matching the same concept, use and scope. Inspect external mathematical sources and record exact locations: edition, page/section and URL/DOI as applicable. An English source can establish meaning without establishing a Japanese translation. Internal glossaries, earlier repository prose, AI suggestions and repeated AI wording in issues are not independent usage evidence.
3. Separate attested external usage, project editorial choices and unresolved evidence. If completed research finds no established Japanese translation, record **no standard Japanese translation** and retain English. This is an operational result for the documented search scope; it does not require proof of global nonexistence. Do not invent provisional Japanese, unsupported katakana, or a term disguised as explanation. Ordinary explanation may clarify the concept without becoming a canonical translation. If research is inaccessible or incomplete, record that limitation rather than claiming a completed negative search; leave the terminology decision unresolved.
4. Record the adopted form, scope and evidence using [the compact record fields](references/record.md). Reassess when the concept, scope, evidence or proposed term changes. Keep working evidence separate from reader-facing prose. Do not copy a project's dictionary into a universal answer list.
5. Check the text against the record. Honor scoped alternatives without treating a legitimate alternative as mathematically wrong solely because the project prefers another. Definitions outrank glossaries; preserve a local definition's meaning, but never use local definition as permission to invent an unestablished Japanese translation.

For migration, `math-semantic-preservation` MS-7 owns occurrence classification and synchronization of statements, proof explanations, notes, link text, glossary and audit records. Share this terminology record; do not repeat searches or findings. Use MS-4 when a wording change could alter the probability or measure context. Retain recoverable conventional shorthand.

## Rules

**JP-12 (invariant) — Inspect technical generic explicitly.**
Always inspect `generic` and proposed Japanese equivalents during terminology review. Retain technical `generic` in English (`generic な`); never substitute `一般位置の`, `一般的な` or `一般の`. Recover its actual exceptional-set or nondegeneracy meaning from the source. Severity: BLOCKING in theorem statements, the scope of a cited result or an introduction whose main point is the generic/degenerate distinction; MINOR in other narrative framing. Nontechnical “general/typical” may still use `一般の` or `一般的な`.

**JP-13 (convention, strong) — Use vocabulary for the actual mathematical role.**
Reject unsuitable Japanese calques and decorative metaphors; identify the object, relation, event or operation. Apply every relevant case and exception in [usage cases](references/usage.md), supported by the evidence workflow. Established field-specific Japanese terms with their exact technical meaning remain valid; English naturalness and local definition alone do not establish Japanese usage. Severity: BLOCKING in theorem statements, proofs, abstracts and contribution summaries; MINOR elsewhere. A calque naming the correct concept is JP-13; a different concept or invented technical name is JP-17 instead.

**JP-14 (convention) — Consistent names and English retention.**
A defined Japanese term must not acquire an undeclared English alias, such as `平衡条件` later called `balanced`/`unbalanced`. Unpack bare English adjectives such as `genuine` or `strict` into precise Japanese when they are ordinary qualifications; research technical uses under the workflow. Keep English when no established Japanese translation exists, including `generic`; established katakana requires usage evidence. Preserve English quotations, titles and bibliography entries. Severity: BLOCKING for an undeclared English alias in a theorem statement or results summary, MINOR otherwise. Report one terminology finding; notation-wide alias defects belong to `math-notation-consistency` NC-3 only when distinct.

**JP-15 (convention) — No vague closed-form label.**
Do not use vague `閉形式` where an explicit formula or equation reference can express the intended content: state the formula, cite the equation or use `明示式`. Exempt closed differential forms (`dω = 0`), documents whose formally defined subject is closed-form solvability, and cited titles; preserve labels. Severity: BLOCKING in theorem/proposition/lemma statements and titles, abstracts and results summaries; MINOR elsewhere.

**JP-16 (convention) — Honor a supplied terminology source of truth.**
Use its canonical terms and permitted aliases within their stated scope, subject to the evidence workflow. Flag conflicting local translations or names. Severity: BLOCKING in theorem/proposition/lemma statements, abstracts and results/contribution summaries; MINOR elsewhere. Compatibility-only Lean identifiers, LaTeX macros, labels and citation keys are exempt. If the glossary contradicts a definition, formula or supplied source, report one JP-17 conflict instead of replacing mechanically or also reporting JP-16.

**JP-17 (invariant) — Preserve concept identity.**
Flag translations that collapse distinct concepts or operations, names inconsistent with their definitions, and invented technical Japanese for an ordinary organisational role. A source label or glossary that contradicts a definition is also a conflict, even without an external-language source. Severity: BLOCKING. Report the source/glossary location and definition evidence, and the required naming repair; do not invent a Japanese rendering to hide the conflict. Established terms must match their attested meaning. English retention is valid; local definition cannot justify an unestablished translation.

**JP-26 (convention) — Name the role, not generic coordinates.**
Use `座標` for an actual coordinate system/chart or coordinates in a basis identified by active context. Do not substitute it for `成分`, `係数`, `変数`, `基底変換` or `表示の変更`. Interpret coordinate-wise by referent (`成分ごとに`, `各変数について`). A multi-index has `成分`, even when represented as a tuple. Do not repeat an already clear basis or referent; preserve cited titles. Severity: MINOR, BLOCKING when a load-bearing statement or definition becomes genuinely ambiguous. When the role is unrecoverable independent of Japanese wording, use `math-notation-consistency` NC-11; a translation/source-naming defect is JP-17. Report one finding.

## Output and repair

For selection or glossary work, provide the decision and its evidence record, including unresolved research. For drafting or translation, use verified decisions in the finished text and report unresolved conflicts. For review, give the rule, class, severity, occurrence, concept evidence and concrete repair; list multiple applicable tags in one finding with the highest severity, breaking ties by ascending rule number. Distinguish an unchecked term from an established defect.

Apply fixes only when requested. Repair a source or glossary conflict only when that artifact is supplied and in scope; otherwise leave the affected Japanese text unchanged and report the external repair needed. Preserve mathematical content and compatibility identifiers. Keep the record synchronized with applied terminology and give a compact change log. `math-claim-integrity` owns distinct claim-support or scope defects; `math-notation-consistency` owns distinct notation bookkeeping. Do not duplicate one defect across skills.
