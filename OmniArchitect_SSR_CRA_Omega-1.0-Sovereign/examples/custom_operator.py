"""
Example: custom monotone operator for SSR–CRA.
Replace demo_gamma with your own generation + admissibility rules.
Must preserve monotonicity: X ⊆ Y ⇒ Γ(X) ⊆ Γ(Y).
"""

from cra_core import LatticeDomain, CRAEngine

def custom_universe():
    return frozenset([
        "atom:energy", "atom:light", "atom:matter",
        "flow:energy→light", "flow:light→matter",
        "constraint:recoverability", "source:Gamma_C"
    ])

def custom_gamma(X):
    g = set(X)
    if "source:Gamma_C" not in g:
        g.add("source:Gamma_C")
    if "atom:energy" in g or not g:
        g.add("atom:energy")
        g.add("flow:energy→light")
    if "flow:energy→light" in g:
        g.add("atom:light")
        g.add("flow:light→matter")
    if "flow:light→matter" in g:
        g.add("atom:matter")
        g.add("constraint:recoverability")
    return frozenset(g)

if __name__ == "__main__":
    domain = LatticeDomain(custom_universe())
    engine = CRAEngine(domain, custom_gamma)
    print("Monotonicity:", engine.verify_monotonicity())
    fp, iters = engine.least_fixed_point()
    print(f"Fixed point in {iters} steps:", sorted(fp))
