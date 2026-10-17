#!/usr/bin/env python3
"""
SSR–CRA Console v4.2 — operational runtime checklist (CRA Model v4.0 §5) as a script.
Finite-lattice reference implementation. Run: python3 cra_console.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from cra_core import (
    LatticeDomain, CRAEngine, demo_universe, demo_gamma, demo_feature_map, euclidean,
    strata_equivalent, demo_coherence, AXIOMS, STRATA, STRATA_LABELS,
    DEMO_EPSILON, MAX_DISTANCE, TOTALITY,
)

CYAN, GOLD, GREEN, RED, RESET, BOLD = "\033[96m", "\033[93m", "\033[92m", "\033[91m", "\033[0m", "\033[1m"

def ok(b):
    return f"{GREEN}PASS{RESET}" if b else f"{RED}FAIL{RESET}"

def banner():
    print(f"{CYAN}{BOLD}  SSR CHRONOLOGICAL REALIGNMENT ARRAY — CONSOLE v4.2")
    print(f"  Finite-lattice reference implementation of CRA Model v4.0{RESET}")
    print(f"{GOLD}HONEST BOUNDARY:{RESET} formal/computational model only.")
    print("  No validated physical mechanism for timeline displacement exists.\n")

def stage_i(engine):
    print(f"{CYAN}STAGE I — BOUNDARY ISOLATION{RESET}")
    print("  I-01 Domain declared: |U| =", len(engine.domain.U))
    print("  I-02 Lattice L = P(U) under ⊆")
    print("  I-03 Zero-point X₀ = ∅")
    print("  I-04 Operator Γ_C registered (demo_gamma)")
    print(f"       Strata ({len(STRATA)}):", "; ".join(f"{s} {STRATA_LABELS[s]}" for s in STRATA))
    mono = engine.verify_monotonicity()
    print(f"  I-05 Monotonicity (20,000 deterministic samples): {ok(mono)}")
    if not mono:
        print("       counterexample:", engine.last_counterexample)
    print("  I-09 Audit ledger active.  I-10 Safe-state reset available.")
    print(f"  Stage I acceptance: {'READY' if mono else 'NOT READY'}")
    return mono

def stage_iii(engine):
    print(f"\n{CYAN}STAGE III — TRANSITION (fixed-point computation){RESET}")
    try:
        fp, iters = engine.least_fixed_point(max_iterations=32)
    except RuntimeError as e:
        print(f"  {RED}{e}{RESET}")
        return None, False, False, False
    fixed = engine.gamma(fp) == fp
    inv = engine.verify_invariants(fp, AXIOMS)
    tests = [engine.domain.bottom, fp, engine.domain.top] + [frozenset(e.state) for e in engine.audit]
    coh = demo_coherence(engine, tests)
    print(f"  Converged in {iters} iterations; |μΓ_C| = {len(fp)} of |U| = {len(engine.domain.U)}")
    print("  Not generated:", sorted(engine.domain.U - fp))
    print(f"  M∞ limit stratum reached ({TOTALITY} ∈ μΓ_C): {ok(TOTALITY in fp)}")
    print(f"  III-04 FixedPoint Γ_C(O) = O : {ok(fixed)}")
    print(f"  III-05 InvariantPass         : {ok(inv)}")
    print(f"  III-06 CoherencePass ({len(tests)} states × {len(STRATA)} levels): {ok(coh)}")
    return fp, fixed, inv, coh

def stage_ii(engine, fp):
    print(f"\n{CYAN}STAGE II — ZODIACAL METRIC FILTER (ε = {DEMO_EPSILON}, max distance {MAX_DISTANCE:.3f}){RESET}")
    pairs = [("μΓ_C vs Γ_C(μΓ_C)", fp, engine.gamma(fp)),
             ("μΓ_C vs μΓ_C minus M7+:observable", fp, fp - {"M7+:observable"}),
             ("μΓ_C vs μΓ_C minus all M7+ atoms", fp, frozenset(e for e in fp if not e.startswith("M7+:"))),
             ("∅ vs μΓ_C", frozenset(), fp)]
    for name, a, b in pairs:
        d = euclidean(demo_feature_map(a), demo_feature_map(b))
        acc = engine.zodiacal_metric_filter(a, b, demo_feature_map, euclidean, DEMO_EPSILON, strata_equivalent)
        print(f"  {name:40s} d = {d:.4f}  ~_C = {strata_equivalent(a, b)}  → {'ACCEPT' if acc else 'REJECT'}")

def main():
    banner()
    engine = CRAEngine(LatticeDomain(demo_universe(), name="SSR-CRA-Demo"), demo_gamma)
    if not stage_i(engine):
        print(f"{RED}Stage I failed. Aborting.{RESET}")
        engine.reset()
        return 1
    fp, fixed, inv, coh = stage_iii(engine)
    if fp is None:
        engine.reset()
        return 1
    stage_ii(engine, fp)
    valid = fixed and inv and coh
    colour = GREEN if valid else RED
    print(f"\n{colour}VALID_RESULT (formal) = FixedPoint ∧ InvariantPass ∧ CoherencePass = {valid}{RESET}")
    print(f"{GOLD}Audit ledger ({len(engine.audit)} entries) preserved.{RESET}")
    return 0 if valid else 1

if __name__ == "__main__":
    sys.exit(main())
