# MENDEL Benchmark Specification

Evaluation pipeline for partition quality, temporal accuracy, and energy continuity. Companion to `README.md` and `DESIGN.md`.

## 1. Reference Reaction Set

Four tiers of increasing complexity. Tier N completion required before Tier N+1.

### Tier 1 — Foundational (SN reactions)

| Reaction | System | Why |
|---|---|---|
| SN2: CH₃Br + OH⁻ → CH₃OH + Br⁻ | 8 atoms + solvent | Textbook concerted mechanism, single transition state |
| SN2: CH₃Cl + CN⁻ → CH₃CN + Cl⁻ | 9 atoms + solvent | Confirms generality across halides |
| SN1: tBuBr → tBu⁺ + Br⁻ → tBuOH | 15 atoms + solvent | Two-stage mechanism, carbocation intermediate — stress test for dynamic re-partitioning |

**Purpose:** validate basic promotion/demotion mechanism on known textbook chemistry.

### Tier 2 — Pericyclic

| Reaction | System | Why |
|---|---|---|
| Diels-Alder: butadiene + ethylene | 16 atoms | Concerted, multi-center promotion test |
| Claisen rearrangement: allyl vinyl ether | 15 atoms | [3,3]-sigmatropic, tests Coordinator's multi-atom transaction |

**Purpose:** test simultaneous promotion of multiple atoms across coordinator.

### Tier 3 — Catalysis (literature-grounded)

| System | Reaction | Why |
|---|---|---|
| Lysozyme | glycoside hydrolysis | Well-characterized active site, literature consensus |
| HIV-1 protease | peptide bond hydrolysis | Two catalytic aspartates, water activation |

**Purpose:** test on realistic enzyme systems with literature ground truth.

### Tier 4 — Stretch

| System | Why |
|---|---|
| [Fe-S] cluster electron transfer | Direct comparison with Genie-CAT scope |
| Heterogeneous catalysis on Cu(111) | Tests element agents in non-organic regime |

## 2. Metrics

### 2.1 Partition Quality

For each timestep `t` and each method `M`:

$$\text{TP}_t = |\{a : a \in \text{promoted}_M(t) \cap \text{reactive}_{\text{ref}}(t)\}|$$
$$\text{FP}_t = |\{a : a \in \text{promoted}_M(t) \setminus \text{reactive}_{\text{ref}}(t)\}|$$
$$\text{FN}_t = |\{a : a \in \text{reactive}_{\text{ref}}(t) \setminus \text{promoted}_M(t)\}|$$

Reported:
- **Precision** = TP / (TP + FP)
- **Recall** = TP / (TP + FN)
- **F1** = 2 · P · R / (P + R)

Aggregated over the reactive window of the trajectory (defined per reaction).

### 2.2 Temporal Accuracy

**Latency** for each true-positive promotion event:

$$\Delta t = t_{\text{promoted}} - t_{\text{react\_onset}}$$

where `t_react_onset` = first timestep where reference QM shows significant electronic structure change (Δq > 0.1 e or ΔBO > 0.2) on that atom.

- Δt < 0 → predictive (good)
- Δt ≈ 0 → tracking (acceptable)
- Δt > 0 → reactive (late)

Report **median Δt** and **distribution histogram** across all events.

### 2.3 Energy Continuity

For each partition transition:

$$\Delta E_{\text{jump}} = \max_{t \in [t_0, t_0 + T_{\text{ramp}}]} |E(t+1) - E(t) - \langle \Delta E \rangle|$$

where `<ΔE>` is the trajectory-wide median energy change per step (subtracts thermal drift).

Compare against PAP/HAMBC-PAP baseline.

**Pass criterion:** `ΔE_jump` ≤ 1.2× baseline.

## 3. Ground Truth Construction

### Method A — High-level QM reference (Tier 1, 2)

For systems ≤ 50 atoms:

1. Run reference DFT-MD with B3LYP / def2-TZVP (or ωB97X-D / def2-TZVPP for transition metals)
2. Sample 100 ps trajectory at 1 fs timesteps
3. At each frame, compute per-atom:
   - Partial charges (Hirshfeld or NPA)
   - Bond orders (Wiberg or Mayer)
4. Annotate atom `a` as **reactive at time `t`** if:
   - |Δq_a(t, t-100fs)| > 0.1 e, OR
   - max bond order change > 0.2

Output: `reactive_atoms_ref[t]` time series.

### Method B — Literature consensus (Tier 3)

1. Identify 3+ peer-reviewed mechanism papers per reaction
2. Extract residue-level active site definitions
3. Map to atom IDs in starting structure
4. Cross-validate: residues must appear in ≥2 sources

### Method C — Expert annotation (ambiguous Tier 3+ cases)

1. Two independent computational chemists annotate
2. Compute Cohen's κ inter-rater agreement
3. Accept only when κ > 0.7
4. Disagreements resolved by third reviewer

## 4. Baselines

### B1 — Distance-cutoff PAP (primary opponent)

Reference implementation:
- QM zone: substrate + atoms within 4.0 Å
- Buffer: 0.5 Å shell
- Smoothing: standard PAP

### B2 — DAS / FSA / HAMBC-PAP

Alternative AP schemes. Selected by reaction type. Used for robustness — MENDEL should not be best on only one AP variant by coincidence.

### B3 — Static QM/MM with expert active site (upper bound)

- Human-curated QM region from literature
- Fixed throughout trajectory
- Represents "perfect" partition for known mechanism
- MENDEL approaches but cannot exceed this on F1 (by construction)

### B4 — Full MM (lower bound)

- No QM treatment
- Trivially fails on reactivity prediction
- Sanity check that the problem is non-trivial

### B5 — Ablation: Gate 1 only (no LLM)

- Descriptor-based promotion without LLM reasoning
- Critical: this reveals **LLM marginal contribution**
- If MENDEL ≈ Gate 1 only, the LLM layer is not earning its keep

### B6 — Genie-CAT (Tier 3 only)

- Apply Genie-CAT to active site detection
- Compare predicted active region overlap with MENDEL's ACTIVE atoms

## 5. Killer Experiment — Solvent Exchange

The clearest demonstration that reasoning-based promotion beats distance-based.

### Setup

- Enzyme system with active site that exchanges catalytic water
- Examples: serine protease, lysozyme
- Reference trajectory: bulk water enters active site, participates in reaction, leaves
- Reference QM marks `t_participation_onset` as first significant charge transfer to/from that water

### Measurement

For each method M and each swap event:

$$\text{lead\_time}_M = t_{\text{participation\_onset}} - t_{\text{promote}}^{M}$$

- Positive lead = predictive promotion (M moved the water early)
- Zero / negative lead = reactive (waited for it to enter geometric zone)

### Hypothesis

$$\text{median}(\text{lead\_time}_{\text{MENDEL}}) > \text{median}(\text{lead\_time}_{\text{PAP}}) + 50 \text{ fs}$$

### Statistical test

- N = 20 independent swap events
- Paired comparison (same trajectory, same event, different method)
- Wilcoxon signed-rank test, α = 0.05

### Decision criterion

MENDEL wins this experiment iff:
- Lead time advantage ≥ 50 fs (median, paired)
- p < 0.05 across N=20 events
- No more than 2 events where MENDEL is late by > 50 fs

## 6. Reporting Template

For each benchmark reaction, the report contains:

1. **System description**
   - Atoms, force field, solvent, conditions
   - Reference trajectory: source, length, validation

2. **Method × metric matrix**
   - Rows: methods (MENDEL, B1–B6)
   - Columns: Precision, Recall, F1, median Δt, ΔE_jump
   - Bold-faced winner per column
   - Significance markers vs primary baseline B1

3. **Energy continuity plot**
   - PES vs time across partition transitions
   - Overlay MENDEL vs PAP
   - Zoom on transition windows

4. **Confusion matrix at peak reactivity**
   - Per atom, ACTIVE classification accuracy at the moment of maximum chemistry

5. **Mechanism trace comparison**
   - Textbook arrow-pushing diagram
   - MENDEL's event log rendered as a comparable diagram
   - Differences annotated

6. **LLM cost accounting**
   - Total Gate 2 calls, total tokens, wall-clock attributable to LLM
   - Compared against per-atom-per-step naive baseline

## 7. Execution Order

Recommended progression once code is functional:

1. **Calibration phase** — run on Tier 1 SN2, manually inspect every promotion event, tune descriptor thresholds
2. **Validation phase** — Tier 1 full evaluation, all baselines, report
3. **Generalization phase** — Tier 2, no further tuning, report
4. **Stress phase** — Tier 3, expect breakage, document failures
5. **Showcase phase** — killer experiment on best Tier 3 system

Do not jump tiers. If Tier N fails, fix and re-run; do not move on.

## 8. What "Success" Looks Like

For a paper-worthy result, MENDEL should achieve, on at least Tier 1 and one Tier 3 system:

- F1 ≥ B1 (distance-cutoff PAP) — non-inferiority floor
- F1 > B5 (Gate 1 only) — LLM contribution is real
- F1 < B3 (expert static) — sanity (not beating an oracle)
- Median Δt < median Δt of B1 by ≥ 25 fs
- ΔE_jump ≤ 1.2× B1
- Mechanism trace human-readable and chemically sensible

If any of these fail, the design has not yet succeeded — iterate, don't write the paper.

## 9. Anti-Goals

To avoid Goodhart's law on benchmarks:

- Do **not** tune descriptor thresholds on test reactions; only on a held-out calibration set
- Do **not** report only the best Tier 1 result; report all attempts
- Do **not** exclude promotion events from latency stats; include all
- Do **not** present a single trajectory as evidence; N ≥ 5 replicates with different initial conditions
