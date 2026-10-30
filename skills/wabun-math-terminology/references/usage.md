# Recurring Japanese vocabulary cases

Use the concept and external usage evidence to assess each occurrence. The following repairs illustrate the intended role; they do not establish translations for an unchecked concept. Never apply them as global string substitutions.

## Metaphors and calques (JP-13)

| Inspect | Repair by role |
| --- | --- |
| `証人` | `明示例`, `具体例`, `〜を満たす例` |
| `模型` in a generic/physics sense | `例`, `構成` |
| `機構`, `装置`, `回路`, `エンジン`, `からくり`, `仕組み` | `構成`, `議論の構造`, or the actual map, estimate, induction, decomposition or correspondence |
| `異常`, `病理` | `退化した場合`, `反例`, according to the concept |
| `感知する`, `検出する`, `検出力` | `区別する`, `識別する`, identifying the objects |
| `層別する`, `層別される` as vague layering | `分類`, or `階層` only when the hierarchy is formally defined |
| `帳簿`, `台帳` | `計数`, `対応` |
| `余裕` in an estimate | State the relevant difference, bound or strict inequality |
| `風景`, `地図`, `物語`, `旅`, `精神` | Delete the metaphor, state the claim or make the analogy precise: `〜と同じ精神に立つ` → `〜の対応物である` |

Example: replace `不変量 I の検出力は完全に層別される` with the actual assertion, such as `不変量 I が区別する対象対の全体は、定理 6.5 の条件により特徴づけられる`, only if that theorem supports it.

Preserve established field-specific uses with matching meaning: `模型` in model theory, `検出` as an established technical operation, `層別` in a recognised statistical procedure, and technical uses of `核`, `流`, `スペクトル`, `作用素`, `エネルギー法` and `安定性`. `統計量` is valid for a genuine statistic in probability/statistics; flag it as a generic label for an arbitrary scalar, invariant, score or summary without statistical meaning. Neither an English term's naturalness nor a new local definition establishes a Japanese exception.

## Mathematical shorthand (JP-13)

| Inspect | Repair and retained exception |
| --- | --- |
| `幾何的に減衰する` for exponential decay | `指数的に減衰する`; preserve genuinely geometric meanings of `幾何的` |
| `概確実` | `ほとんど確実に`, `確率 1 で`, preserving the same probability space, event and dependencies |
| `下側裾` when the event is obscured | State the actual threshold event; keep recoverable established shorthand |
| `網` | `ε-ネット` with recoverable set, metric and approximation scale; explain only what the audience needs |
| `失敗確率` without a recoverable event | Identify the actual event; retain the shorthand once established |

Use the source's event, never an invented replacement. When probability context is uncertain, use `math-semantic-preservation` MS-4. `順位` and `規約` remain drafting preferences, not vocabulary findings.

## Concept and role checks

- JP-12: for a claim about matrices outside the discriminant's zero set, replace the misleading `一般的な行列` with `generic な行列`; do not use `一般位置の` as a translation of generic.
- JP-15: keep `ω は閉形式である（dω = 0）` in the differential-form sense.
- JP-17: if a source identifies a simplex's filtration-entry threshold with homology-class birth, report that concept conflict before choosing Japanese. A separately defined simplex “birth time” does not itself conflate these concepts; verify its scope and Japanese usage rather than endorsing `単体の誕生値` from the label alone.
- JP-17: do not collapse simplicial collapse and filtration-preserving reduction into one `簡約`. Verify distinct names for their actual concepts; a source or old glossary's proposed pair is not independent translation evidence.
- JP-16: if a verified, scoped glossary adopts `フィルトレーション値` for a simplex threshold, flag the conflicting `生成値`; first resolve any definition conflict under JP-17.
- JP-17: “theorem layer” meaning only a grouping of statements does not justify `定理層`. Describe the actual grouping, for example `定理を確立済みの結果と条件付きの結果に区分する`, when that is the intended distinction.
- Preserve established `層` in sheaf theory, `核` of a linear map and `台` of a function or measure. Preserve compatible local definitions' mathematical meaning, but do not infer established Japanese usage from them.
- JP-26: `多重指数 $\alpha$ の座標` → `多重指数 $\alpha$ の成分`; tuple encoding gives no exception. For positive rescaling of basis functions, `特徴座標の変換` → `各基底関数の正の定数倍によるスケーリング`. Keep basis coordinates (`基底 $e_1,\ldots,e_n$ に関する座標`), local coordinates (`局所座標`), and the distinction between `連結成分` and `ベクトルの成分`.
