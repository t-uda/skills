# Shared Japanese mathematical language

Apply to narrative and structured mathematical prose according to each sentence's role. The severity stated in each rule controls the finding. For one defect matching several rules, list the applicable tags once, use the highest severity, and break ties by ascending rule number.

**JP-1 (invariant) — Assert established claims.**
Do not hedge a proved conclusion with `〜と思われる`, `〜と考えられる`, `〜のように見える`, `〜らしい`, `〜と予想される` or `〜はずである`. This includes narrative summaries of proved results. Definitions must define clearly; conclusions must assert what was proved. Severity: BLOCKING. Proof goals and outlook are not proved conclusions; explicitly identified conjectures or interpretations in remarks may retain their appropriate uncertainty.

**JP-2 (convention) — Present tense for mathematical facts.**
Use `〜する`, `〜である`, `〜が成り立つ` or `〜が存在する`. Severity: BLOCKING in theorem/proposition statements, MINOR elsewhere. Preserve historical attribution (`Euler は〜を示した`) and references to a proof step already completed (`先に〜を示した`).

**JP-4 (heuristic) — Restatement and inference.**
`すなわち` restates the immediately preceding sentence; it must not introduce a new deduction. `ゆえに`, `よって` and `したがって` assert a necessary consequence of what immediately precedes. Test whether the conclusion follows from that text, including the assumptions and results it invokes. Severity: BLOCKING for a logical gap, MINOR for a register mismatch. `つまり` is informal restatement, suitable in notes but not theorem proofs.

**JP-11 (heuristic) — Long noun chains.**
A chain of four or more stacked `の` is MINOR; restructure it into shorter nominal phrases or a predicate form.

**JP-14 (convention) — No fullwidth semicolon.**
Do not use `；` in Japanese prose. Use `、` or `。`, or split the sentence. Severity: MINOR.

**JP-18 (convention) — Arabic numerals for quantities.**
Use Arabic numerals, including quantity-bearing compounds, operations, powers and ordinal references: `2つ`, `2段階`, `2頂点`, `1を引く`, `2倍`, `1/2`, `第1節`. Preserve fixed lexical items such as `一意`, `一般` and `唯一`, and follow the document's spacing convention. Numeral style alone is MINOR even in a theorem or abstract; a wrong quantity requires a substantive correction.

**JP-25 (heuristic) — Recoverable demonstratives.**
Use `この` when its referent is unambiguous in the active context and the reference or contrast serves a purpose. Flag competing live referents or repetition that adds no useful reference. A construction can remain clear across intervening sentences about its properties. Use a name or precise reference only to resolve real ambiguity; impose no adjacency, distance or occurrence limit. Severity: MINOR, BLOCKING only when ambiguity affects a load-bearing statement's interpretation.

Keep `この写像` when one map is constructed and subsequent sentences discuss its properties; flag `この構成` when two live constructions compete.
