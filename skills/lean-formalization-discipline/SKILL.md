---
name: lean-formalization-discipline
description: Use when writing, refactoring, or maintaining Lean / Mathlib proofs — especially across a large formalization — so soundness survives both the mechanical checks and a close reading of every statement, and progress is measured by discharged obligations rather than the appearance of motion.
---

# Lean Formalization Discipline

Working discipline for an agent editing Lean proofs. These are default failure modes a human had to repeatedly correct when collaborating with an AI on a large formalization, sharpened by field use on a real project. Treat them as standing policy, not suggestions. The body is Lean-specific; the general stance below is included because each item shows up sharply in Lean.

## Stance

Give one reasoned recommendation; do not lay out a menu and hedge. Prefer honesty to the appearance of progress — a `sorry` hidden under a typeclass or an axiom class is not progress, and an honest `sorry` beats a concealed axiom. **Aim at the most dangerous step.** When the goal is a `sorry`-free capstone, attack the genuinely-missing pillar (the load-bearing hypothesis most likely to fail) *early*, rather than banking easy connected wins while the hard part is parked off to the side — safe incremental wins give the illusion of progress while the capstone stays one hard step away forever. Delegate volume, keep judgment: hand mechanical bulk to clean-context agents, but never trust an agent's "PROVEN" label — re-verify it yourself.

## Use when

- Writing or refactoring Lean / Mathlib code, particularly in a large library where soundness can hide behind machinery.
- Wiring already-proven parts together, isolating a missing pillar, or porting external Lean code into the repo.
- Reviewing a `sorry`/`axiom` count, or an agent's claim that a result is complete.
- Deciding whether a target is "done."

## Two pillars

Soundness is enforced by two independent checks, and you need both:

1. **The mechanical ritual** (`lake build` + `#print axioms`) catches relocated gaps and leaked `sorry`/axioms.
2. **Statement-gate reading** catches gaps that are *build-clean and axiom-clean* — statements that compile and verify yet do not say what the mathematics supports.

The worst soundness bugs in practice pass every mechanical check. Do not lean on the ritual alone.

## Statement-gate reading

Do this *before* proving, on every new statement, field, or hypothesis.

- **Over-strength trap (the headline check).** A `structure` field or hypothesis can be *provable exactly as written* yet stronger than the mathematics supports — `∀ t : ℝ` for a forward-only object, a mis-scaled bound, `∀ u` where only `∀ u ∈ S` holds. It passes `lake build` and `#print axioms` cleanly; nothing mechanical catches it. For every hypothesis ask: *is what I get to assume too generous?* For every conclusion ask: *is this exactly what the real theorem yields, no stronger?* Forward-only objects quantified over all of `ℝ` are the canonical offender.
- **A `-- TODO` / "impossible" note is itself a claim.** It earns the same skepticism as a proof. Do not assert "impossible" or "unsound"; assert "not done here — missing pillar X." A wrong blocker note is a soundness defect in prose.
- **No-smuggle audit.** When you isolate a missing pillar as a hypothesis, check that the hypothesis does not already contain the conclusion. An assumption that quietly implies the capstone is worthless even though it builds and prints clean.

## Soundness invariants

- **Never place a `sorry` on a `false` or non-satisfiable statement.** Reason at the statement gate first: forward-only existence stated backward, a limit that can blow up, etc.
- **No junk or circular `structure` fields.** A field whose only role is to be discharged, or that depends on what it is meant to establish, is a bad field.
- **Honest `sorry` over hidden axioms.** A `sorry` covered by a typeclass instance or `axiom` class looks like progress but is not. To "grind" means to dig the proof forward, not to relocate the gap.
- **An isolated frontier hypothesis is debt, not progress.** Converting a missing pillar into a clean `structure`/`∀∃` hypothesis (never a new `axiom`) is the right way to express "done modulo this precisely-stated gap" — but until the hypothesis is *discharged by a real proof and wired in*, it is a `sorry` in a suit. Count every hypothesis outside the project's intended **irreducible primitive set** as outstanding debt with an owner, not as a win. Track whether that debt is shrinking or growing; if isolated hypotheses accumulate faster than they are discharged, the hard part is being fled. Isolate at the *least* abstract level that captures the genuine Mathlib gap — over-abstract hypotheses are both harder to discharge and more prone to the over-strength trap.
- **Self-contained in the repo.** Done means the whole target is `sorry`-free and axiom-clean *inside this repo*; depend on nothing landing upstream in Mathlib. But *do* check Mathlib first — its boundary (what it has vs. lacks) is what tells you where the honest frontier is. Let Mathlib decide *where* you draw the isolated hypothesis; never *weaken the target* to fit what Mathlib happens to provide.

## Build, wiring, and naming

- **Wire finished parts into the capstone; isolation is a staging area, not a destination.** Connect proven upstream pieces bottom-up so the capstone genuinely depends on them. An in-progress kernel with `sorry`s *may* be quarantined out of the capstone's import graph to keep `#print axioms` honest — that is legitimate — but a quarantined kernel must stay tracked and on a path to being wired in. Permanent isolation is how the hard math gets deferred indefinitely.
- **Root-import / build-graph gap.** A new file not added to the default build target compiles green in isolation while the guard never runs on it — preflight goes green on a file it is not checking. The first action on any new file is to add its import to the build root; verify the file is actually in the default build target before trusting any green.
- **Standard over bespoke.** Take the classical, textbook route; name the concrete standard method rather than over-stating the prerequisite. Before declaring a wall, check whether a raw/low-level version of the lemma already exists in Mathlib and can be lifted (e.g. by density). Reach for a standard Mathlib lemma before inventing a private mechanism.
- **Descriptive shipped names; scratch labels are fine.** Shipped Lean `def`/`theorem` names must describe what they prove. Opaque numbering (`S1`–`S8`, `Phase`, `Priority`, `T5`) is fine as internal orchestration/scratch labels but must never leak into formal names — a reader seeing `T5` learns nothing. Reformat ported/external code as your own: rename and repackage rather than preserving foreign structure verbatim.
- **Intrinsically slow elaboration is a design smell.** A genuinely slow `lake build` / elaboration is an early warning of combinatorial trouble: an exploding or looping `simp` set, `decide`/`norm_num` on large terms, runaway typeclass resolution, or `omega`/`grind` on a huge goal. Treat it as a signal to restructure, not just a wait. (This is distinct from infrastructure flakiness — see the verification ritual.)

## Verification ritual

Run this every commit — the mechanical half of the two pillars:

1. `lake build` must be clean.
2. **`#print axioms` as an exact pin on the top-level theorem.** Pin the *capstone* theorem's axiom set to an exact expected list (e.g. the project's intended primitives, no `sorryAx`), and re-check after *any* core edit. Checking only "results you touched" misses leakage *into* the capstone from elsewhere; the binding invariant is the capstone's full axiom set.
3. **STATUS / header / doc prose is part of the soundness surface.** `sorry` counts, "only non-proved input," and similar claims drift out of date and become overclaims. Update them in the *same* commit as the code, and state `sorry` counts numerically.
4. **Infrastructure-failure hygiene (distinct from the slow-build smell).** A timed-out or killed prover can leave a half-applied edit behind — a broken token in an otherwise-green file. After any prover/build process dies, re-run preflight; do not trust the partial. Network/socket timeouts are environment noise, not a design smell.

Commit locally often. Push only when asked. An agent's "PROVEN" label is not evidence; the build and the pinned `#print axioms` are.

## Relationship to other skills

- For generic delegate-and-verify orchestration mechanics, see `light-orchestration` and `claude-code-advanced-orchestration`.
- For keeping computational (non-proof) experiments reproducible and honest about status, see `computational-reproducibility` — this skill is its analogue for machine-checked proofs.
