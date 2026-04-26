---
name: randomness
description: Use when a task explicitly requires random selection, probabilistic sampling, stochastic tie-breaking, or diverse creative generation. Prefer the bundled PRNG script when tool execution is available. Use prompt-only String Seed fallback only for low-stakes or creative-diversity cases. Do not use for security-sensitive, scientific, benchmark, lottery, or correctness-critical randomness.
---

# Randomness

Use this skill when the user asks for random selection, probabilistic sampling, stochastic tie-breaking, or diverse creative generation.

## Priority order

1. **Script-backed randomness** (primary): Use the bundled PRNG script when tool execution is available.
2. **String Seed fallback** (secondary): Use only when tools are unavailable or the goal is creative diversification rather than PRNG-backed sampling.
3. **Refuse or redirect**: For security-sensitive, fairness-sensitive, scientific, benchmark, simulation, lottery, or reproducibility-critical tasks, redirect to explicit external tooling.

## Script-backed randomness (primary path)

When tool execution is available, use the bundled script:

```sh
python3 skills/randomness/scripts/random_choice.py --uniform A B C
python3 skills/randomness/scripts/random_choice.py --weighted A:0.2 B:0.8
```

The script uses Python's `random` module (PRNG). It is not cryptographically secure and not suitable for fair lotteries or security-sensitive tasks.

### Uniform choice

```sh
python3 skills/randomness/scripts/random_choice.py --uniform option1 option2 option3
```

Outputs the selected item to stdout.

### Weighted choice

```sh
python3 skills/randomness/scripts/random_choice.py --weighted item1:0.3 item2:0.7
```

Format: `item:weight`. Weights must be non-negative, finite, and sum to greater than zero.

### JSON output

```sh
python3 skills/randomness/scripts/random_choice.py --uniform A B C --json
```

Outputs:

```json
{"mode": "uniform", "items": ["A", "B", "C"], "selected": "A", "method": "python random module"}
```

Weighted JSON output includes the per-item weights:

```json
{"mode": "weighted", "items": [{"item": "A", "weight": 0.2}, {"item": "B", "weight": 0.8}], "selected": "B", "method": "python random module"}
```

## String Seed fallback (secondary path)

Use String Seed prompting only for low-stakes tasks, and only in either of these cases:

- Tool execution is unavailable, and a random or probabilistic choice is still needed.
- Tool execution is available, but the goal is creative diversification rather than PRNG-backed sampling.

### Fallback procedure

When using String Seed as a fallback:

1. Generate a random-looking string of 24–40 mixed characters.
2. Use the **entire seed string** as a control signal for the downstream task.
3. Do not choose by intuition or by the most natural/default answer.
4. Map the seed to the requested choice space or diversity dimensions.

**The seed is a control signal, not decorative text.**

### Prompt template for probabilistic choice

```text
First, generate a random-looking string of 24–40 mixed characters.
Then, use the entire string as a seed for the following task.
Do not choose by intuition or by the most natural/default answer.

For uniform choice among n options, use a concrete full-string mapping such as:
- value = sum(ord(c) for c in seed)
- selected_index = value % n

For weighted choice, use a rolling-hash full-string mapping such as:
- M = 2**61 - 1
- h = 0
- for c in seed: h = (131 * h + ord(c)) % M
- u = h / M    # u is a value in [0, 1)
- select the item whose cumulative weight first exceeds u
```

### Prompt template for creative diversification

```text
First, generate a random-looking string of 24–40 mixed characters.

Then:
1. Decompose the output into explicit variation dimensions
   (for example: style, perspective, ordering, examples, emphasis).
2. For each dimension, list the candidate values you would otherwise default to.
3. Slice the seed into one segment per dimension.
4. For each dimension, derive an integer from its segment
   (for example: value = sum(ord(c) for c in segment)) and pick
   candidates[value % len(candidates)].
5. Do not use default completions unless they are selected through this
   seed-driven mapping.
```

## Limitations

- Python's `random` module is a PRNG, not cryptographically secure.
- String Seed fallback is emulated randomness, not a substitute for real PRNGs.
- Do not use for:
  - Security-sensitive tasks
  - Fair lotteries
  - Scientific simulations or experiments
  - Benchmark sampling
  - Reproducibility-critical tasks
  - Fairness-sensitive or auditability-critical decisions

When reproducibility matters, use an explicit external seed and a real PRNG-backed implementation outside this skill's scope.

## When to use

Use this skill when:

- The user explicitly asks for random selection or sampling
- A task requires stochastic tie-breaking
- Creative generation needs diversity or variation
- The task is low-stakes and does not require cryptographic or scientific-grade randomness

Do not use this skill when:

- The task requires cryptographic randomness
- Fairness or auditability is critical
- The task is a scientific simulation, lottery, or benchmark
- Reproducibility with explicit seeds is required
