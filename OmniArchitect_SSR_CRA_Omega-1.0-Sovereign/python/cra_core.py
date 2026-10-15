#!/usr/bin/env python3
"""
SSR Chronological Realignment Array — Core Engine Ω-1.0-Sovereign
Least-Fixed-Point computational model.

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
        self.version = "Ω-1.0-Sovereign"
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

    def verify_monotonicity(self, sample_size: int = 32) -> bool:
        """Spot-check X ⊆ Y ⇒ Γ(X) ⊆ Γ(Y). Exhaustive only for tiny U."""
        if len(self.domain.U) <= 6:
            for X, Y in itertools.combinations(self.domain.powerset(), 2):
                if X.issubset(Y) and not self.gamma(X).issubset(self.gamma(Y)):
                    return False
            return True
        # Random sample for larger domains
        import random
        elems = list(self.domain.U)
        for _ in range(sample_size):
            x_elems = random.sample(elems, k=random.randint(0, len(elems)))
            y_elems = list(set(x_elems) | set(random.sample(elems, k=random.randint(0, len(elems)))))
            X, Y = frozenset(x_elems), frozenset(y_elems)
            if not self.gamma(X).issubset(self.gamma(Y)):
                return False
        return True

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
# Demo operator — closed under stratified generation + admissibility
# ---------------------------------------------------------------------------

STRATA = ["M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7+"]

def demo_universe() -> FrozenSet[Element]:
    """Small finite U for reproducible demos."""
    atoms = []
    for s in STRATA:
        atoms.append(f"{s}:primitive")
        atoms.append(f"{s}:relation")
        atoms.append(f"{s}:observable")
    atoms.extend([
        "constraint:CLAAL",
        "constraint:monotonicity",
        "constraint:recoverability",
        "timeline:periodic",
        "act:indexical",
        "source:Gamma_C",
    ])
    return frozenset(atoms)


def demo_gamma(X: State) -> State:
    """
    Monotone extensive operator that advances one stratum frontier per application.
    From bottom it builds M0, then M1, etc., across successive iterations.
    """
    generated = set(X)
    generated.add("source:Gamma_C")
    generated.add("constraint:monotonicity")

    # Ensure M0 if source is present (always)
    generated.add("M0:primitive")

    # Advance exactly one new primitive if the previous is already fully present
    for i in range(len(STRATA) - 1):
        curr = STRATA[i]
        nxt = STRATA[i + 1]
        if (f"{curr}:primitive" in generated and
            f"{curr}:relation" in generated and
            f"{curr}:observable" in generated and
            f"{nxt}:primitive" not in generated):
            generated.add(f"{nxt}:primitive")
            break  # only one advance per application

    # Close relations/observables for any primitive that is present
    for s in STRATA:
        if f"{s}:primitive" in generated:
            generated.add(f"{s}:relation")
            generated.add(f"{s}:observable")

    # Downward restriction
    for i in range(1, len(STRATA)):
        if f"{STRATA[i]}:primitive" in generated:
            generated.add(f"{STRATA[i-1]}:relation")

    if any(e.startswith("M1:") for e in generated):
        generated.add("constraint:CLAAL")
        generated.add("constraint:recoverability")
    if any(e.startswith("M3:") for e in generated):
        generated.add("act:indexical")
        generated.add("timeline:periodic")

    return frozenset(generated)


# ---------------------------------------------------------------------------
# Feature map for Zodiacal filter (demo)
# ---------------------------------------------------------------------------

def demo_feature_map(state: State) -> tuple[float, ...]:
    """Count of elements per stratum + constraint flags. Normalised."""
    counts = []
    for s in STRATA:
        counts.append(sum(1 for e in state if e.startswith(s + ":")) / 3.0)
    counts.append(1.0 if "constraint:CLAAL" in state else 0.0)
    counts.append(1.0 if "source:Gamma_C" in state else 0.0)
    return tuple(counts)


def euclidean(a: tuple, b: tuple) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def always_equivalent(a: State, b: State) -> bool:
    """Demo equivalence under C — refine for real models."""
    return True


if __name__ == "__main__":
    print("SSR–CRA Core Ω-1.0-Sovereign — self-test")
    domain = LatticeDomain(demo_universe())
    engine = CRAEngine(domain, demo_gamma)
    print(f"|U| = {len(domain.U)}")
    print("Monotonicity spot-check:", engine.verify_monotonicity())
    try:
        fp, iters = engine.least_fixed_point()
        print(f"Least fixed point reached in {iters} iterations.")
        print(f"|μΓ_C| = {len(fp)}")
        print("Sample elements:", sorted(list(fp))[:8], "...")
    except RuntimeError as e:
        print(e)
    print("Audit entries:", len(engine.audit))
    print("HONEST BOUNDARY: formal result only — not physical displacement.")
