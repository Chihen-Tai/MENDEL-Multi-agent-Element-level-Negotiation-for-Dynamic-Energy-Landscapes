# MENDEL Design Document

Detailed architecture and mechanism specification. Companion to `README.md`.

## 1. Layer Interfaces

### L1 — Physics Substrate

Adapter pattern over OpenMM (default), LAMMPS, or ASE.

**Outputs per timestep:**
- `positions[N, 3]` — atom coordinates (Å)
- `velocities[N, 3]` — velocities (Å/ps)
- `forces[N, 3]` — current forces (kcal/mol/Å)
- `partial_charges[N]` — from MLIP head or polarizable FF
- `bond_orders[edges]` — Wiberg or Mayer, computed on-demand for active atoms only

**Inputs:**
- `partition_weight[N]` ∈ [0, 1] — per-atom buffer interpolation weight
- `element_symbol[N]` — frozen at init

### L2 — Atom Instance Registry

Shared state. Schema (per atom):

```python
@dataclass
class AtomRecord:
    atom_id: int
    element: str
    sub_agent: Literal["ACTIVE", "BUFFER", "SPECTATOR"]
    buffer_weight: float  # 0 in SPECTATOR, 1 in ACTIVE, interpolating in BUFFER
    promotion_history: list[Event]
    local_env_cache: LocalEnv | None  # populated only for ACTIVE
```

**Invariants:**
- All atom records are mutated only via Coordinator-approved transitions
- `sub_agent == "SPECTATOR"` ⟺ `buffer_weight == 0`
- `sub_agent == "ACTIVE"` ⟺ `buffer_weight == 1`

### L3 — Sub-agents

`ActiveSubAgent` (per element):
- Owns: `atom_ids: list[int]` in ACTIVE state
- Per-atom detailed cache: partial charge, neighbor list, bond orders, reasoning buffer
- Updates: every `K_active` timesteps (default K=10)

`SpectatorSubAgent` (per element):
- Owns: `atom_ids: list[int]` in SPECTATOR state
- Aggregate stats only: mean charge, RMSF, COM
- Per-atom cheap descriptor refreshed every timestep (Gate 1 input)
- No reasoning state

### L4 — Element Agent

Per-element singleton. Public interface:

```python
class ElementAgent:
    element: str
    persona: ElementPersona  # frozen, loaded from prompts/{element}.md
    active_sub: ActiveSubAgent
    spectator_sub: SpectatorSubAgent

    def on_anomaly(atom_id: int, gate1_signal: DescriptorReading) -> Decision: ...
    def on_settling(atom_id: int, settling_signal: SettlingReading) -> Decision: ...
    def negotiate(other: ElementAgent, context: NegotiationCtx) -> Agreement: ...
```

`Decision` ∈ `{PROMOTE, DEFER, IGNORE, VETO}`.

### L5 — Mechanism Coordinator

- Global event bus (publish/subscribe across element agents)
- Approves/blocks transitions per registry invariants
- Builds mechanism trace: ordered DAG of promotion events with cross-references
- Resolves multi-element negotiations (e.g., nucleophile-electrophile pairing)

## 2. Two-Gate State Machine

States and transitions:

```
SPECTATOR ──Gate1+Gate2──> BUFFER_PROMOTING ──ramp complete──> ACTIVE
                                  │
                                  └──Gate2 VETO──> SPECTATOR (revert)

ACTIVE ──settling detected──> BUFFER_DEMOTING ──ramp complete──> SPECTATOR
                                       │
                                       └──new anomaly──> ACTIVE (cancel demotion)
```

### Gate 1 — Deterministic descriptor gate

Per-element threshold tables (see §3). Evaluated every timestep for all SPECTATOR atoms of that element.

**Cost:** O(N_spectator) per timestep, no LLM call.

**Output:** boolean + descriptor reading object.

### Gate 2 — LLM reasoning gate

Triggered only when Gate 1 fires. Element agent's LLM call:

1. Receives: persona, atom local environment, descriptor reading, recent event log
2. Generates: K=3 candidate classifications (mechanism type, expected behavior, confidence)
3. **Commits if all K agree.** Disagreement → DEFER.
4. May also issue VETO if reasoning identifies false positive.

**Cost:** O(K) LLM forward passes per promotion event. K=3 default.

**Constraint:** Gate 2 can only **reject** a Gate 1 trigger. It cannot promote unilaterally. This bounds hallucination damage to over-conservatism.

## 3. Descriptor Tables

Each element agent owns a descriptor table. Thresholds tuned per system; values below are starting defaults.

### Carbon (C)

| Descriptor | Trigger condition |
|---|---|
| Partial charge magnitude | \|q\| > 0.3 e |
| Partial charge change rate | dq/dt > 0.05 e/ps |
| Nearest-neighbor distance | d < 3.0 Å with non-bonded δ- atom |
| Wiberg bond order to neighbor | 0.3 < BO < 0.7 (mid-cleavage) |
| Hybridization change indicator | sp³ → sp² geometry shift > 15° |

### Oxygen (O)

| Descriptor | Trigger condition |
|---|---|
| Lone pair orientation toward δ+ | cos θ > 0.7, distance < 3.5 Å |
| Wiberg bond order change | \|dBO\| > 0.1 per ps |
| Coordination number change | dCN ≠ 0 |
| Protonation state shift | partial H assignment changes |

### Nitrogen (N)

| Descriptor | Trigger condition |
|---|---|
| Lone pair availability | uncoordinated, partial charge < -0.4 |
| Pyramidal-to-planar flattening | improper angle change > 20° |
| Coordination number change | dCN ≠ 0 |

### Hydrogen (H)

| Descriptor | Trigger condition |
|---|---|
| Grotthuss proton indicator | indicator > threshold (Voth-style) |
| Bond order to two heavy atoms | BO_donor + BO_acceptor change > 0.3 |
| Distance to acceptor | d_H–A < 1.5 Å while d_H–D > 1.2 Å |

### Halogens (Br, Cl, F, I)

| Descriptor | Trigger condition |
|---|---|
| C–X bond order | BO < 0.7 (leaving group activation) |
| Partial charge | q approaching -1.0 (departing as anion) |
| Geometric departure | d_C–X > 2.5 Å (Br typical) |

### Iron (Fe) — metalloprotein systems

| Descriptor | Trigger condition |
|---|---|
| Coordination number change | dCN ≠ 0 |
| Spin state indicator | from ML head, transition detected |
| Ligand exchange in progress | partial coordination to two ligands |
| Redox-relevant ESP shift | electrostatic potential change > threshold |

## 4. Buffer Zone Mathematics

Smooth interpolation function during BUFFER state:

$$w(t) = \frac{1}{2}\left(1 - \cos\left(\pi \cdot \frac{t}{T_{\text{ramp}}}\right)\right)$$

where `t` is timesteps since transition entry, `T_ramp = 100` timesteps (~ 100 fs at 1 fs/step) by default.

**Energy interpolation:**

$$E_{\text{buffer}}(\text{atom}) = w \cdot E_{\text{active}}(\text{atom}) + (1 - w) \cdot E_{\text{spectator}}(\text{atom})$$

**Force interpolation:**

$$\vec{F}_{\text{buffer}} = w \cdot \vec{F}_{\text{active}} + (1 - w) \cdot \vec{F}_{\text{spectator}}$$

Follows HAMBC-PAP convention to preserve energy conservation in the smoothed region.

## 5. Hysteresis

To prevent boundary chatter (atoms oscillating across partition):

- **Promote threshold** `T_high`: descriptor must exceed
- **Demote threshold** `T_low`: descriptor must remain below for `N_settle = 50` timesteps
- **Ratio:** `T_high / T_low ≥ 1.5` recommended
- Demotion timer resets if any descriptor crosses `T_high` during the settling window

## 6. Self-Consistency Protocol

Each Gate 2 LLM call:
1. Sample `K=3` hypotheses with `temperature=0.7`
2. Each hypothesis returns: `{classification, expected_behavior, confidence}`
3. Commit decision iff all K share the same classification AND all confidences > 0.5
4. Otherwise: DEFER (no transition this timestep, Gate 1 must re-fire)

Cost trade-off: 3× LLM calls per promotion event, but eliminates ~80% of single-shot hallucinations in pilot tests (target validation, TBD).

## 7. Event Log Schema

JSONL format. One record per transition or LLM call.

```json
{
  "timestep": 12450,
  "event_type": "PROMOTION",
  "atom_id": 47,
  "element": "C",
  "from_state": "SPECTATOR",
  "to_state": "BUFFER_PROMOTING",
  "gate1_descriptors": {
    "partial_charge": 0.42,
    "dq_dt": 0.08,
    "nn_distance": 2.7
  },
  "gate2_hypotheses": [
    {"classification": "electrophilic_C_in_SN2", "confidence": 0.81},
    {"classification": "electrophilic_C_in_SN2", "confidence": 0.78},
    {"classification": "electrophilic_C_in_SN2", "confidence": 0.85}
  ],
  "decision": "PROMOTE",
  "negotiation_partners": [{"atom_id": 92, "element": "O"}]
}
```

This log doubles as the mechanism trace and the debugging artifact.

## 8. Edge Cases

**Bond cleavage / formation** — both participating atoms must be ACTIVE simultaneously. Coordinator enforces by blocking transitions until partner is also ACTIVE.

**Proton hopping (Grotthuss)** — H agent uses indicator function locating excess proton; the indicator's "carrier" atom is always ACTIVE.

**Multi-center concerted reactions** (e.g., pericyclic) — Coordinator brokers simultaneous promotion across all participating atoms in a single transaction.

**Spectator promoted by mistake** — fallback: if active sub-agent observes no chemistry within `T_review = 500` timesteps, force demotion and log as false positive.

## 9. Cost Model

Per timestep (N = total atoms, K = LLM samples):

| Layer | Cost | Frequency |
|---|---|---|
| L1 Physics | O(N) | every step |
| L2 Registry updates | O(1) per transition | rare |
| L3 Spectator descriptors | O(N_spectator) | every step |
| L3 Active reasoning state | O(N_active) | every K_active=10 steps |
| L4 LLM Gate 2 | O(K) forward passes | only on Gate 1 trigger |
| L5 Coordination | O(promotion events) | rare |

Expected LLM call count for a typical reactive trajectory (10⁵ timesteps, ~20 promotion events): **~60 LLM calls**, vs. naive per-atom-per-step which would be ~10⁹.

## 10. Open Design Questions

- Should sub-personas exist for different oxidation states within one element (e.g., Fe²⁺ vs Fe³⁺)?
- Negotiation protocol semantics — synchronous voting vs. async eventual consistency?
- Should Gate 2 have access to global trajectory history, or only local context window?
- How to handle competing Gate 1 triggers from different element agents on the same neighborhood?
