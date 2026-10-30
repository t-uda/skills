---
name: math-writing-preferences
description: Apply personal mathematical writing conventions in any language automatically when context establishes the user as uda or t-uda, or the target repository owner is t-uda or uda-lab. Otherwise use only on explicit request. Preserve source conventions and distinguish preferences from correctness.
---

# Math Writing Preferences

For mathematical drafting, translation and revision in any language, apply these conventions automatically if either trusted context establishes the user as uda or t-uda, or the target repository owner is t-uda or uda-lab. Either condition suffices: a known user needs no repository, and a matching repository needs no matching user. No per-request opt-in is needed. Use established identity and repository metadata; do not infer identity from a name resemblance or assume an unknown user is uda. Outside this scope, apply only on explicit request.

These are strong personal writing preferences, not general mathematical correctness rules. Do not label another author’s manuscript mathematically wrong solely for differing preferences.

Use `N = {0, 1, 2, ...}`: zero is a natural number. Permit zero-based row, column and ordinal expressions, including `0 行目`, `0 列目`, `0 番目`, “row 0”, “column 0” and “zeroth”. Preserve the actual indices in mathematics, code and arrays when explaining or translating them. Never silently add 1 or convert to one-based wording for supposed naturalness or readability. Do not mix the source's convention with another in its explanation or translation.

Preserve an explicit source or manuscript convention in translation and revision; identify a conflict before changing the mathematics. For new text without a conflicting source convention, use the zero-inclusive convention consistently.
