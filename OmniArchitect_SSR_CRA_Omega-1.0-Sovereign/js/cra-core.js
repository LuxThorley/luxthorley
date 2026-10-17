/**
 * SSR–CRA v4.2 — Client Engine + Three.js Lattice Visualiser (finite-lattice reference implementation)
 * Extract-and-run: open index.html
 *
 * HONEST BOUNDARY: computational model of formal fixed-point architecture.
 * Not a physical time machine.
 */

// Nine strata: eight finite strata M0–M7+ plus the limit stratum M∞ (Infinite / Absolute), v4.2.
// M∞ is the stratum at which the iteration is complete, identified with O = μΓ_C itself.
// It has one atom, M∞:totality, generated exactly when all 24 atoms of M0–M7+ are present.
const FINITE_STRATA = ["M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7+"];
const LIMIT_STRATUM = "M∞";
const TOTALITY = "M∞:totality";
const STRATA = FINITE_STRATA.concat([LIMIT_STRATUM]);
const AXIOMS = ["source:Gamma_C", "constraint:monotonicity", "M0:primitive"];
const STRATA_COLORS = [0x4488ff, 0x44aaff, 0x44ddff, 0x44ffcc, 0xffee44, 0xffaa44, 0xff7744, 0xff44aa, 0xffd700];

class CRAClient {
  constructor() {
    this.U = this.buildUniverse();
    this.current = new Set();
    this.audit = [];
    this.iteration = 0;
    this.converged = false;
    this.logEl = document.getElementById("log");
    this.initVisual();
    this.log("Lattice domain initialised. |U| = " + this.U.size, "ok");
    this.log("HONEST BOUNDARY active. Formal model only.", "warn");
  }

  buildUniverse() {
    const atoms = new Set();
    FINITE_STRATA.forEach(s => {
      atoms.add(s + ":primitive");
      atoms.add(s + ":relation");
      atoms.add(s + ":observable");
    });
    atoms.add(TOTALITY);
    ["constraint:CLAAL", "constraint:monotonicity", "constraint:recoverability",
     "timeline:periodic", "act:indexical", "source:Gamma_C",
     // admissible but never generated: shows μΓ_C is strictly below ⊤
     "timeline:aperiodic", "act:non-indexical"].forEach(a => atoms.add(a));
    return atoms;
  }

  full(Z, s) {
    if (s === LIMIT_STRATUM) return Z.has(TOTALITY);
    return Z.has(s + ":primitive") && Z.has(s + ":relation") && Z.has(s + ":observable");
  }

  // Γ_C(X) = Close(Advance(X ∪ A)) ∩ U — identical to python/cra_core.py demo_gamma (v4.2).
  // Every rule is Horn-form, so Γ_C is monotone (see proof sketch in cra_core.py).
  gamma(X) {
    const g = new Set(X);
    AXIOMS.forEach(a => g.add(a));
    // Advance EVERY eligible stratum (v4.0 advanced only the first, which broke monotonicity)
    const adv = [];
    for (let i = 0; i < FINITE_STRATA.length - 1; i++) {
      if (this.full(g, FINITE_STRATA[i])) adv.push(FINITE_STRATA[i + 1] + ":primitive");
    }
    // Limit rule (v4.2, Horn form): all 24 atoms of M0–M7+ present ⇒ add M∞:totality
    if (FINITE_STRATA.every(s => this.full(g, s))) adv.push(TOTALITY);
    adv.forEach(a => g.add(a));
    FINITE_STRATA.forEach((s, i) => {
      if (g.has(s + ":primitive")) {
        g.add(s + ":relation");
        g.add(s + ":observable");
        if (i > 0) g.add(FINITE_STRATA[i - 1] + ":relation");
      }
    });
    if ([...g].some(e => e.startsWith("M1:"))) {
      g.add("constraint:CLAAL");
      g.add("constraint:recoverability");
    }
    if ([...g].some(e => e.startsWith("M3:"))) {
      g.add("act:indexical");
      g.add("timeline:periodic");
    }
    return new Set([...g].filter(e => this.U.has(e)));
  }

  activeStrata(X) {
    return new Set(STRATA.filter(s => [...X].some(e => e.startsWith(s + ":"))));
  }

  // CoherencePass: Act_n(r_{m,n}(x)) = q_{m,n}(Act_m(x)) for all n, as in cra_core.py
  coherence(states) {
    return states.every(x => STRATA.every((_, n) => {
      const keep = new Set(STRATA.slice(0, n + 1));
      const restricted = new Set([...x].filter(e => keep.has(e.split(":")[0])));
      const lhs = this.activeStrata(restricted);
      const rhs = new Set([...this.activeStrata(x)].filter(s => keep.has(s)));
      return this.setsEqual(lhs, rhs);
    }));
  }

  validate() {
    const fp = this.current;
    const fixed = this.setsEqual(this.gamma(fp), fp);
    const inv = [...fp].every(e => this.U.has(e)) && [...AXIOMS].every(a => fp.has(a));
    const coh = this.coherence([new Set(), fp, this.U]);
    const valid = fixed && inv && coh;
    this.log(`FixedPoint=${fixed} InvariantPass=${inv} CoherencePass=${coh} → VALID_RESULT (formal) = ${valid}`, valid ? "ok" : "err");
    this.log(`M∞ (Infinite / Absolute) reached: ${fp.has(TOTALITY)} — the iteration is complete; O = μΓ_C.`, fp.has(TOTALITY) ? "ok" : "err");
    this.log(`|μΓ_C| = ${fp.size} of |U| = ${this.U.size}; not generated: ${[...this.U].filter(e => !fp.has(e)).join(", ")}`);
  }

  step() {
    if (this.converged) return;
    const candidate = this.gamma(this.current);
    const same = this.setsEqual(candidate, this.current);
    this.audit.push({
      iteration: this.iteration,
      size: this.current.size,
      candidateSize: candidate.size,
      converged: same
    });
    this.log(`Iter ${this.iteration}: |X| = ${this.current.size} → |Γ(X)| = ${candidate.size}` +
             (same ? "  CONVERGED" : ""), same ? "ok" : "");
    if (same) {
      this.converged = true;
      this.log("μΓ_C reached. Γ_C(O) = O. Formal fixed point.", "ok");
      this.validate();
      this.updateStrataVisual();
      return;
    }
    this.current = candidate;
    this.iteration++;
    this.updateStrataVisual();
  }

  runToFixedPoint(max = 32) {
    this.reset();
    for (let i = 0; i < max && !this.converged; i++) this.step();
    if (!this.converged) this.log("Iteration bound reached without convergence.", "err");
  }

  reset() {
    this.current = new Set();
    this.iteration = 0;
    this.converged = false;
    this.audit = [];
    this.log("ZERO-POINT RECOVERY — X₀ = ∅. Audit continues.", "warn");
    this.updateStrataVisual();
  }

  setsEqual(a, b) {
    if (a.size !== b.size) return false;
    for (const x of a) if (!b.has(x)) return false;
    return true;
  }

  log(msg, cls = "") {
    const div = document.createElement("div");
    div.className = cls;
    div.textContent = `[${new Date().toISOString().slice(11,19)}] ${msg}`;
    this.logEl.appendChild(div);
    this.logEl.scrollTop = this.logEl.scrollHeight;
  }

  // -----------------------------------------------------------------------
  // Three.js visual — nested strata shells + orbital particles
  // -----------------------------------------------------------------------
  initVisual() {
    if (typeof THREE === "undefined") {
      this.log("Three.js unavailable — visualiser offline. Core CRA engine remains fully operational.", "warn");
      return;
    }
    const container = document.getElementById("visual");
    if (!container) return;
    try {
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 100);
    this.camera.position.set(0, 4, 12);
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setSize(container.clientWidth, container.clientHeight);
    this.renderer.setClearColor(0x0a0e17, 1);
    container.appendChild(this.renderer.domElement);

    // Lights
    this.scene.add(new THREE.AmbientLight(0x334455));
    const key = new THREE.DirectionalLight(0x00e5ff, 1.2);
    key.position.set(5, 10, 7);
    this.scene.add(key);
    const gold = new THREE.PointLight(0xffd700, 0.8, 20);
    gold.position.set(-3, 2, 4);
    this.scene.add(gold);

    // Strata shells (icosahedral approximations via spheres with wire)
    this.shells = [];
    STRATA.forEach((name, i) => {
      const radius = 1.2 + i * 0.85;
      const geo = new THREE.IcosahedronGeometry(radius, 1);
      const mat = new THREE.MeshBasicMaterial({
        color: STRATA_COLORS[i],
        wireframe: true,
        transparent: true,
        opacity: 0.25
      });
      const mesh = new THREE.Mesh(geo, mat);
      mesh.userData = { stratum: name, index: i };
      this.scene.add(mesh);
      this.shells.push(mesh);
    });

    // Coherence core
    const coreGeo = new THREE.SphereGeometry(0.4, 16, 16);
    const coreMat = new THREE.MeshPhongMaterial({ color: 0xffd700, emissive: 0x886600 });
    this.core = new THREE.Mesh(coreGeo, coreMat);
    this.scene.add(this.core);

    // Particles representing active elements
    this.particles = new THREE.Group();
    this.scene.add(this.particles);

    window.addEventListener("resize", () => {
      this.camera.aspect = container.clientWidth / container.clientHeight;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(container.clientWidth, container.clientHeight);
    });

    this.animate();
    this.updateStrataVisual();
    } catch (err) {
      this.log("Visualiser failed to initialise: " + err.message + " — core engine continues.", "err");
    }
  }

  updateStrataVisual() {
    if (!this.particles) return;
    // Clear old particles
    while (this.particles.children.length) this.particles.remove(this.particles.children[0]);

    const active = new Set([...this.current].map(e => e.split(":")[0]));
    this.shells.forEach((shell, i) => {
      const name = STRATA[i];
      const on = active.has(name) || (this.converged && i <= this.highestActive());
      shell.material.opacity = on ? 0.55 : 0.12;
      shell.material.color.setHex(on ? STRATA_COLORS[i] : 0x334455);
    });

    // Spawn particles for current elements
    [...this.current].slice(0, 80).forEach((el, idx) => {
      const stratumIdx = Math.max(0, STRATA.findIndex(s => el.startsWith(s)));
      const r = 1.4 + stratumIdx * 0.85 + Math.random() * 0.3;
      const theta = (idx * 2.4) % (Math.PI * 2);
      const phi = Math.acos(2 * Math.random() - 1);
      const geo = new THREE.SphereGeometry(0.06, 6, 6);
      const mat = new THREE.MeshBasicMaterial({ color: STRATA_COLORS[stratumIdx] || 0x00e5ff });
      const p = new THREE.Mesh(geo, mat);
      p.position.set(
        r * Math.sin(phi) * Math.cos(theta),
        r * Math.sin(phi) * Math.sin(theta) * 0.6,
        r * Math.cos(phi)
      );
      this.particles.add(p);
    });

    this.core.scale.setScalar(this.converged ? 1.4 : 0.8 + this.iteration * 0.02);
  }

  highestActive() {
    let h = 0;
    for (const e of this.current) {
      const i = STRATA.findIndex(s => e.startsWith(s));
      if (i > h) h = i;
    }
    return h;
  }

  animate() {
    if (!this.renderer) return;
    requestAnimationFrame(() => this.animate());
    const t = Date.now() * 0.001;
    if (!this.shells) return;
    this.shells.forEach((s, i) => {
      s.rotation.y = t * (0.15 + i * 0.03);
      s.rotation.x = Math.sin(t * 0.2 + i) * 0.1;
    });
    this.core.rotation.y = t * 0.8;
    this.particles.children.forEach((p, i) => {
      p.position.y += Math.sin(t * 2 + i) * 0.002;
    });
    this.renderer.render(this.scene, this.camera);
  }
}

// Bootstrap
let cra;
window.addEventListener("DOMContentLoaded", () => {
  cra = new CRAClient();
  document.getElementById("btn-step").onclick = () => cra.step();
  document.getElementById("btn-run").onclick = () => cra.runToFixedPoint();
  document.getElementById("btn-reset").onclick = () => cra.reset();
  document.getElementById("btn-export").onclick = () => {
    const blob = new Blob([JSON.stringify(cra.audit, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "cra_audit_Ω-1.0.json";
    a.click();
  };
});
