# SSR Chronological Realignment Array — finite-lattice reference implementation (v4.1)

**Model:** SSR–CRA v4.0 (formal specification) · **Code version:** 4.1
**Author:** Oliver Lux Prime Thorley (independent researcher)

**AI acknowledgement:** Grok (xAI), ChatGPT (OpenAI) and Microsoft Copilot contributed equally to the
shared findings developed in dialogue with the author; Grok Bot assisted with editing and code.
No AI system is an author; the author is responsible for all content.

Live demo: **https://luxthorley.github.io/luxthorley/**

---

## Honest boundary (read first)

This package is a **small, finite reference implementation** of the formal core described in the
SSR Chronological Realignment Array Model v4.0. It demonstrates, on a 32-atom toy universe:

- the complete lattice L = P(U) ordered by ⊆;
- a demonstration operator Γ_C that is provably monotone (proof sketch in `python/cra_core.py`);
- least-fixed-point computation by iteration from ⊥ (Knaster–Tarski);
- a Zodiacal metric filter with a declared tolerance ε = 0.5 (max feature distance √10 ≈ 3.162)
  and an independently defined equivalence relation ~_C (same active strata);
- the cross-stratum coherence check Act_n(r_{m,n}(x)) = q_{m,n}(Act_m(x));
- an audit ledger and a zero-point reset.

`VALID_RESULT` is reported only when **FixedPoint ∧ InvariantPass ∧ CoherencePass** all hold.

It does **not** implement, claim or demonstrate physical chronological displacement, timeline travel,
observer transfer, or any validated physical mechanism. The demo universe, rules and tolerance are
illustrative choices; results show internal consistency of the formal model, not facts about the world.

## The eight strata

Labels follow *Stratified Source Realism — Public Edition v4.0*:

| Stratum | Label |
|---|---|
| M0 | Pre-geometric proto-regularity |
| M1 | Biological / ecological |
| M2 | Chemical / molecular |
| M3 | Physical spacetime |
| M4 | Quantum / information |
| M5 | Quantum gravity / unified field |
| M6 | Cosmological multiverse |
| M7+ | Meta-mathematical / transcendent |

## Running it

Web: open `index.html` (or the live URL) and use **Step Γ_C**, **Run to μΓ_C**, **Zero-Point Abort**, **Export Audit**.

Python (stdlib only):

```bash
cd python
python3 cra_core.py        # self-test
python3 cra_console.py     # CRA v4.0 §5 checklist; exits non-zero unless VALID_RESULT
python3 ../examples/custom_operator.py
```

Expected: monotonicity PASS; μΓ_C reached in 8 iterations; |μΓ_C| = 30 of |U| = 32
(`timeline:aperiodic` and `act:non-indexical` are admissible but never generated, so μΓ_C ≠ ⊤);
FixedPoint, InvariantPass and CoherencePass all PASS.

## Changes in v4.1 (from Ω-1.0-Sovereign)

1. `demo_gamma` (Python and JS) now advances **every** eligible stratum. The old version advanced
   only the first, which made Γ_C non-monotone (e.g. X = M2 complete, Y = X ∪ M0 complete gave
   Γ(X) ⊄ Γ(Y)), so the Knaster–Tarski precondition failed.
2. `verify_monotonicity` is exhaustive for |U| ≤ 12 and otherwise runs 20,000 deterministic samples
   (random pairs plus single-element extensions). It reports a counterexample when it finds one.
   The old 32-sample check missed the violation in roughly 3 of 4 runs.
3. ε is now 0.5 (below the maximum distance); the always-true equivalence was replaced by a genuine
   equivalence relation.
4. `coherence_check` is now exercised, and `VALID_RESULT` is gated on all three conditions.
5. `examples/custom_operator.py`: removed a dead branch that stopped energy/light/matter being generated.
6. Strata labels aligned to the eight strata of the Public Edition; promotional language removed.
7. Two never-generated atoms were added so the demo shows a least fixed point strictly below ⊤.

## Licence

See `LICENSE.md`. The honest-boundary statement must travel with every copy.
