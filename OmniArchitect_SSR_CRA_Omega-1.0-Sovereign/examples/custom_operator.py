"""
Example: custom monotone operator for SSR–CRA (v4.1).
Replace demo_gamma with your own generation + admissibility rules.
Must preserve monotonicity: X ⊆ Y ⇒ Γ(X) ⊆ Γ(Y). Writing every rule in Horn form
("if these atoms are present, add that atom") guarantees it.

v4.1 fix: the v4.0 rule `if "atom:energy" in g or not g` could never fire from ∅,
because source:Gamma_C had already been added, so energy/light/matter were never generated.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))
from cra_core import LatticeDomain, CRAEngine

def custom_universe():
    return frozenset([
        "atom:energy", "atom:light", "atom:matter",
        "flow:energy→light", "flow:light→matter",
        "constraint:recoverability", "source:Gamma_C",
    ])

def custom_gamma(X):
    g = set(X)
    g.add("source:Gamma_C")                      # axiom
    if "source:Gamma_C" in g:                    # Source generates energy
        g.add("atom:energy")
    if "atom:energy" in g:
        g.add("flow:energy→light")
    if "flow:energy→light" in g:
        g.add("atom:light")
    if "atom:light" in g:
        g.add("flow:light→matter")
    if "flow:light→matter" in g:
        g.add("atom:matter")
    if "atom:matter" in g:
        g.add("constraint:recoverability")
    return frozenset(g)

if __name__ == "__main__":
    engine = CRAEngine(LatticeDomain(custom_universe()), custom_gamma)
    print("Monotonicity (exhaustive, |U| = 7):", "PASS" if engine.verify_monotonicity() else "FAIL")
    fp, iters = engine.least_fixed_point()
    print(f"Fixed point in {iters} steps ({len(fp)} atoms):", sorted(fp))
