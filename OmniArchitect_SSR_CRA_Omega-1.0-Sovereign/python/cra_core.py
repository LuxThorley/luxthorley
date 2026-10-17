#!/usr/bin/env python3
"""
SSR Chronological Realignment Array — Core Engine v4.1 (formerly Ω-1.0-Sovereign)
Finite-lattice reference implementation of the least-fixed-point model.

HONEST BOUNDARY (non-negotiable):
This is a mathematical and computational prototype of the formal architecture
described in SSR–CRA Model v4.0. It implements lattice operations, monotone
operators, fixed-point iteration, metric filtering, and coherence checks.
It does NOT implement physical chronological displacement, timeline travel,
or any experimentally validated time machine. All outputs are formal states,
simulations, or audit records.

Supreme Sovereign: Oliver Lux Prime Thorley
Lattice node: OmniArchitect ∞ CRA
"""

from __future__ import annotations
import itertools
import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable, FrozenSet, Iterable, Optional

# ---------------------------------------------------------------------------
# Lattice primitives
# ---------------------------------------------------------------------------

Element = str  # formal structural atoms
State = FrozenSet[Element]

@dataclass
class LatticeDomain:
    """L = P(U), ordered by inclusion."""
    U: FrozenSet[Element]
    name: str = "SSR-CRA-Lattice"

    @property
    def bottom(self) -> State:
        return frozenset()

    @property
    def top(self) -> State:
        return self.U

    def is_subset(self, X: State, Y: State) -> bool:
        return X.issubset(Y)

    def join(self, *sets: State) -> State:
        return frozenset().union(*sets)

    def meet(self, *sets: State) -> State:
        if not sets:
            return self.top
        return frozenset.intersection(*sets)

    def powerset(self) -> list[State]:
        """Only for small |U|. Used in exhaustive monotonicity tests."""
        return [frozenset(s) for s in itertools.chain.from_iterable(
            itertools.combinations(self.U, r) for r in range(len(self.U) + 1)
        )]


# ---------------------------------------------------------------------------
# Operator and fixed-point
# ---------------------------------------------------------------------------

@dataclass
class AuditEntry:
    timestamp: float
    iteration: int
    state: list[str]
    candidate: list[str]
    converged: bool
    note: str = ""


class CRAEngine:
    """
    Monotone Generator Matrix + Fixed-Point Convergence Monitor
    + Zodiacal Metric Filter + Coherence Verification + Abort.
    """

    def __init__(self, domain: LatticeDomain, gamma: Callable[[State], State]):
        self.domain = domain
        self.gamma = gamma
        self.audit: list[AuditEntry] = []
        self.current: State = domain.bottom
        self.version = "4.1"
        self.last_counterexample = None
        self.aborted = False

    def reset(self) -> State:
        """Emergency Abort Vector — Zero-Point Recovery. X_reset := ∅"""
        self.current = self.domain.bottom
        self.aborted = False
        self.audit.append(AuditEntry(
            time.time(), -1, [], [], False, "ZERO-POINT RECOVERY — audit preserved"
        ))
        return self.current

    def least_fixed_point(self, max_iterations: int = 64) -> tuple[State, int]:
        """
        Reference algorithm from CRA Model v4.0 §3.4.
        Assumes gamma is a well-defined monotone endofunction.
        """
        current = self.domain.bottom
        for iteration in range(max_iterations + 1):
            candidate = self.gamma(current)
            converged = candidate == current
            self.audit.append(AuditEntry(
                timestamp=time.time(),
                iteration=iteration,
                state=sorted(current),
                candidate=sorted(candidate),
                converged=converged,
                note="fixed-point" if converged else "iterating"
            ))
            if converged:
                self.current = current
                return current, iteration
            current = candidate
        raise RuntimeError(
            f"No fixed point reached within {max_iterations} iterations. "
            "Audit preserved. Abort recommended."
        )

    def verify_monotonicity(self, samples: int = 20000, seed: int = 0,
                            exhaustive_limit: int = 12) -> bool:
        """
        Check X ⊆ Y ⇒ Γ(X) ⊆ Γ(Y).

        * |U| ≤ exhaustive_limit: exhaustive over every comparable pair (sound and complete).
        * Larger U: deterministic randomized test (fixed seed) combining
          (a) random pairs X ⊆ Y at several densities, and
          (b) single-element extensions Y = X ∪ {u}. Monotonicity is equivalent to
              Γ(X) ⊆ Γ(X ∪ {u}) for all X and u, because any X ⊆ Y is a finite chain
              of single-element additions.
        A randomized PASS is evidence, not proof; the demo operator's proof is in demo_gamma.
        The first counterexample found is stored in self.last_counterexample.
        """
        import random
        self.last_counterexample = None
        g = self.gamma
        def bad(X, Y):
            if not g(X).issubset(g(Y)):
                self.last_counterexample = (sorted(X), sorted(Y))
                return True
            return False
        if len(self.domain.U) <= exhaustive_limit:
            P = self.domain.powerset()
            return not any(bad(X, Y) for X in P for Y in P if X <= Y)
        rng = random.Random(seed)
        elems = sorted(self.domain.U)
        for k in range(samples):
            p = (0.1, 0.3, 0.5, 0.7, 0.9)[k % 5]
            X = frozenset(e for e in elems if rng.random() < p)
            if k % 2:
                Y = X | {rng.choice(elems)}
            else:
                Y = X | frozenset(e for e in elems if rng.random() < rng.random())
            if bad(X, Y):
                return False
        return True

    def verify_invariants(self, fp: State, axioms: Iterable[Element] = ()) -> bool:
        """InvariantPass: fp ⊆ U, Γ(fp) = fp, axioms ⊆ fp."""
        return (fp.issubset(self.domain.U) and self.gamma(fp) == fp
                and set(axioms).issubset(fp))

    # -----------------------------------------------------------------------
    # Zodiacal Metric Filter (CRA §3.5)
    # -----------------------------------------------------------------------

    @staticmethod
    def zodiacal_metric_filter(
        state_a: State,
        state_b: State,
        feature_map: Callable[[State], tuple[float, ...]],
        distance: Callable[[tuple, tuple], float],
        epsilon: float,
        equivalent_under_C: Callable[[State, State], bool],
    ) -> bool:
        if epsilon < 0:
            raise ValueError("epsilon must be non-negative")
        if not equivalent_under_C(state_a, state_b):
            return False
        return distance(feature_map(state_a), feature_map(state_b)) <= epsilon

    # -----------------------------------------------------------------------
    # Cross-stratum coherence (CRA §2.3 / §4.3)
    # -----------------------------------------------------------------------

    @staticmethod
    def coherence_check(
        x: Any,
        r_mn: Callable,
        act_n: Callable,
        act_m: Callable,
        q_mn: Callable,
    ) -> bool:
        """Act_n(r_m,n(x)) == q_m,n(Act_m(x))"""
        try:
            return act_n(r_mn(x)) == q_mn(act_m(x))
        except Exception:
            return False

    def export_audit(self) -> str:
        return json.dumps(
            [e.__dict__ for e in self.audit],
            indent=2,
            default=str,
        )


# ---------------------------------------------------------------------------
# Demo operator — stratified generation + admissibility (v4.1, corrected)
# ---------------------------------------------------------------------------

# Eight strata, labels as in "Stratified Source Realism — Public Edition v4.0".
STRATA = ["M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7+"]
STRATA_LABELS = {
    "M0": "Pre-geometric proto-regularity",
    "M1": "Biological / ecological",
    "M2": "Chemical / molecular",
    "M3": "Physical spacetime",
    "M4": "Quantum / information",
    "M5": "Quantum gravity / unified field",
    "M6": "Cosmological multiverse",
    "M7+": "Meta-mathematical / transcendent",
}
AXIOMS = frozenset({"source:Gamma_C", "constraint:monotonicity", "M0:primitive"})

# Admissible atoms that no generation rule produces. They show that μΓ_C is
# strictly smaller than ⊤ = U, i.e. that "least" does real work.
UNGENERATED = ["timeline:aperiodic", "act:non-indexical"]


def demo_universe() -> FrozenSet[Element]:
    """Small finite U for reproducible demos (|U| = 32)."""
    atoms = []
    for s in STRATA:
        atoms += [f"{s}:primitive", f"{s}:relation", f"{s}:observable"]
    atoms += ["constraint:CLAAL", "constraint:monotonicity", "constraint:recoverability",
              "timeline:periodic", "act:indexical", "source:Gamma_C"]
    atoms += UNGENERATED
    return frozenset(atoms)


def _full(X: State, s: str) -> bool:
    return {f"{s}:primitive", f"{s}:relation", f"{s}:observable"} <= X


def demo_gamma(X: State) -> State:
    """
    Γ_C(X) = Close(Advance(X ∪ A)) ∩ U.

    Advance(Z) = Z ∪ { M(i+1):primitive : stratum M(i) is complete in Z }   (EVERY eligible i)
    Close(Z)   = Z ∪ { s:relation, s:observable : s:primitive ∈ Z }
                   ∪ { M(i-1):relation : M(i):primitive ∈ Z }
                   ∪ { CLAAL, recoverability : some M1 atom ∈ Z }
                   ∪ { act:indexical, timeline:periodic : some M3 atom ∈ Z }

    Proof sketch of monotonicity. Each clause has the Horn form
    "if a fixed finite set of atoms (or at least one atom of a fixed set) is in Z, add a
    fixed atom". Every such clause has a body that stays true when Z grows, so Advance and
    Close are monotone maps Z ↦ Z ∪ heads(Z). Z ↦ Z ∪ A and Z ↦ Z ∩ U are monotone, and a
    composition of monotone maps is monotone. Hence X ⊆ Y ⇒ Γ_C(X) ⊆ Γ_C(Y). Γ_C is also
    extensive on L (X ⊆ Γ_C(X)). The v4.0 operator broke monotonicity because it advanced
    only the FIRST eligible stratum ("break"), so adding atoms could suppress a later advance.

    From ∅ one stratum is completed per application, so iteration from ⊥ reaches
    μΓ_C in 8 steps; μΓ_C = U minus UNGENERATED (30 of 32 atoms).
    """
    Z = set(X) | AXIOMS
    adv = {f"{STRATA[i+1]}:primitive" for i in range(len(STRATA) - 1) if _full(Z, STRATA[i])}
    Z |= adv
    for i, s in enumerate(STRATA):
        if f"{s}:primitive" in Z:
            Z |= {f"{s}:relation", f"{s}:observable"}
            if i > 0:
                Z.add(f"{STRATA[i-1]}:relation")
    if any(e.startswith("M1:") for e in Z):
        Z |= {"constraint:CLAAL", "constraint:recoverability"}
    if any(e.startswith("M3:") for e in Z):
        Z |= {"act:indexical", "timeline:periodic"}
    return frozenset(Z) & demo_universe()


# ---------------------------------------------------------------------------
# Zodiacal filter (demo): feature map, metric, genuine equivalence relation
# ---------------------------------------------------------------------------

def demo_feature_map(state: State) -> tuple[float, ...]:
    """Fraction of each stratum present + constraint flags. Max distance = √10 ≈ 3.162."""
    counts = [sum(1 for e in state if e.startswith(s + ":")) / 3.0 for s in STRATA]
    counts.append(1.0 if "constraint:CLAAL" in state else 0.0)
    counts.append(1.0 if "source:Gamma_C" in state else 0.0)
    return tuple(counts)


def euclidean(a: tuple, b: tuple) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


MAX_DISTANCE = 10 ** 0.5
DEMO_EPSILON = 0.5  # declared tolerance: < one-and-a-half stratum's worth of difference; << MAX_DISTANCE


def active_strata(state: State) -> FrozenSet[str]:
    return frozenset(s for s in STRATA if any(e.startswith(s + ":") for e in state))


def strata_equivalent(a: State, b: State) -> bool:
    """
    ~_C: a ~ b iff they activate the same strata. This is the kernel of a function,
    hence reflexive, symmetric and transitive (a genuine equivalence relation),
    defined independently of the ε-metric as CRA v4.0 §3.5 requires.
    """
    return active_strata(a) == active_strata(b)


# ---------------------------------------------------------------------------
# Cross-stratum coherence (demo maps): Act_n(r_{m,n}(x)) = q_{m,n}(Act_m(x))
# ---------------------------------------------------------------------------

def r_restrict(n: int) -> Callable[[State], State]:
    """r_{m,n}: keep only strata atoms at index ≤ n (restriction to the lower domain)."""
    keep = set(STRATA[: n + 1])
    return lambda x: frozenset(e for e in x if e.split(":")[0] in keep)

def act(x: State) -> FrozenSet[str]:
    """Act: indexed actuality representation = set of active strata."""
    return active_strata(x)

def q_project(n: int) -> Callable[[FrozenSet[str]], FrozenSet[str]]:
    """q_{m,n}: project an actuality representation onto strata ≤ n."""
    keep = frozenset(STRATA[: n + 1])
    return lambda a: a & keep


def demo_coherence(engine: "CRAEngine", states: Iterable[State]) -> bool:
    """CoherencePass: the coherence equation holds for every n and every test state."""
    return all(
        engine.coherence_check(x, r_restrict(n), act, act, q_project(n))
        for x in states for n in range(len(STRATA))
    )


def demo_validate(engine: "CRAEngine") -> dict:
    """Runs Stage I–III checks and returns each verdict. VALID_RESULT is gated on all three."""
    mono = engine.verify_monotonicity()
    fp, iters = engine.least_fixed_point()
    fixed = engine.gamma(fp) == fp
    inv = engine.verify_invariants(fp, AXIOMS)
    tests = [engine.domain.bottom, fp, engine.domain.top] + [frozenset(e.state) for e in engine.audit]
    coh = demo_coherence(engine, tests)
    return {"monotone": mono, "iterations": iters, "fixed_point": fp, "FixedPoint": fixed,
            "InvariantPass": inv, "CoherencePass": coh,
            "VALID_RESULT": mono and fixed and inv and coh}


if __name__ == "__main__":
    print("SSR–CRA Core v4.1 (finite-lattice reference implementation) — self-test")
    domain = LatticeDomain(demo_universe())
    engine = CRAEngine(domain, demo_gamma)
    print(f"|U| = {len(domain.U)}")
    v = demo_validate(engine)
    print("Monotonicity check (20,000 deterministic samples):", "PASS" if v["monotone"] else "FAIL")
    fp = v["fixed_point"]
    print(f"Least fixed point reached in {v['iterations']} iterations; |μΓ_C| = {len(fp)} (⊤ has {len(domain.U)})")
    print("Not generated (in U \\ μΓ_C):", sorted(domain.U - fp))
    print(f"FixedPoint={v['FixedPoint']}  InvariantPass={v['InvariantPass']}  CoherencePass={v['CoherencePass']}")
    print("VALID_RESULT (formal):", v["VALID_RESULT"])
    print("Audit entries:", len(engine.audit))
    print("HONEST BOUNDARY: formal result only — not physical displacement.")
