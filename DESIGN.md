# MENDEL Architecture Design

**Molecular Element-group NeDotiation for Energy Landscapes**

---

## 1. Core Idea

Each functional group in a molecule is an agent. Agents:
1. Observe their local environment
2. Predict their own role in the reaction
3. Negotiate with other agents to resolve conflicts
4. Hand off the final assignment to a foundation MLIP for energy computation

This replaces the original element-based design (C-agent, O-agent, ...), which conflated atomic identity with chemical behavior.

---

## 2. Roles

The five roles a group can take:

| Role | Description | Typical groups |
|---|---|---|
| `reactive_electrophile` | accepts electrons | carbonyl C, alkyl halide C, sp³ C with LG |
| `reactive_nucleophile` | donates electrons | alcohol O, amine N, alkene π, enolate C |
| `reactive_radical` | radical center | C-H near radical initiator, halide in radical chain |
| `leaving_group` | departs with electron pair | halide, tosylate, water (from -OH) |
| `spectator` | does not participate | aromatic ring (in most cases), alkyl chain |

Roles are mutually exclusive per group in a single reaction step.

---

## 3. System Architecture

```
┌──────────────────────────────────────────┐
│  INPUT                                   │
│  - reactant SMILES / 3D structure        │
│  - (optional) product SMILES             │
│  - reaction context (radical / ionic)    │
└──────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│  Module 1: Functional Group Identifier   │
│  RDKit + SMARTS pattern matching         │
│  Output: list of groups + atom indices   │
└──────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│  Module 2: Group Descriptor Builder      │
│  - Internal features                     │
│  - Environment features                  │
│  - Context features                      │
└──────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│  Module 3: Group Agents (Role Predictor) │
│  Small NN per group → role probabilities │
└──────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│  Module 4: Negotiation Layer             │
│  Rule-based conflict resolution          │
└──────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│  Module 5: MLIP Wrapper                  │
│  Foundation MLIP → E, F                  │
└──────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│  OUTPUT                                  │
│  - roles per group                       │
│  - reaction center                       │
│  - energy, forces                        │
│  - visualization                         │
└──────────────────────────────────────────┘
```

---

## 4. Module Specifications

### Module 1: Functional Group Identifier

Use RDKit SMARTS matching to find all functional groups.

**Conflict resolution**: longer/more specific patterns win; already-matched atoms skipped.

**Coverage**: ~20 predefined groups (see `groups/` folder).

**Contextual groups**: some groups (e.g., `alpha_carbon`) are not standalone functional groups — they only exist relative to another group. These are identified in a second pass after primary groups are found. Example: α-C is a sp³ C-H adjacent to a carbonyl, ester, nitrile, nitro, or sulfone.

**Identification order**:
1. Match high-priority specific groups first (carboxylic acid, ester, amide, ...)
2. Match remaining standard groups (carbonyl, alcohol, ether, alkene, ...)
3. Identify contextual groups based on neighbors (alpha_carbon, ...)
4. Remaining atoms → spectator (alkyl chain, etc.)

### Module 2: Group Descriptor Builder

For each identified group, build a feature vector.

| Category | Features |
|---|---|
| Internal | group type one-hot, atom count, total charge, π-bond presence, hybridization |
| Environment | neighbor group types (multi-hot), distance to nearest reactant, EWG/EDG neighbors |
| Context | reaction type (ionic / radical / pericyclic), solvent polarity, temperature regime |

Output: ~64-dim vector per group.

### Module 3: Group Agents

Small MLP per group type (or one shared MLP conditioned on group type).

```
Input  : descriptor (~64 dim)
Hidden : 64 → 32
Output : 5 role probabilities (softmax)
```

Each group's spec file (in `groups/`) declares which roles are allowed for that group and under what conditions.

### Module 4: Negotiation Layer

Rule-based for project scope. Examples:

- **Ionic**: pick top-1 electrophile + top-1 nucleophile by confidence; rest = spectator
- **Radical**: pick top-2 radical candidates; rest = spectator
- **Pericyclic**: assign roles based on group geometry (e.g., diene + dienophile for Diels-Alder)

Conflicts (one group predicted high for multiple reactive roles) resolved by:
1. Reaction context (e.g., radical context forces radical assignment)
2. Highest probability among allowed roles for that group type
3. Compatibility with partner groups

### Module 5: MLIP Wrapper

Use foundation MLIP for energy and forces:

| System | MLIP |
|---|---|
| Pure organic | MACE-OFF |
| Contains metal | MACE-MP-0 |
| Periodic | MACE-MP-0 |

Roles do not affect MLIP computation directly. They are passed through as metadata, used for visualization and downstream analysis (e.g., for tagging active region in active-learning workflows).

---

## 5. Training Strategy

**Data**: 50–100 manually labeled benchmark reactions covering SN2, E2, addition, cycloaddition, radical reactions.

**Labels**: per-group role assignment, validated against organic chemistry textbook mechanisms.

**Loss**: cross-entropy on role classification.

**Augmentation**: same reaction with different reactant arrangements (conformers, distances) to teach environment-awareness.

**Scale-up path** (post-project): extract from USPTO via atom-mapping → propagate roles to groups.

---

## 6. Evaluation

| Metric | Definition |
|---|---|
| Role accuracy | per-group classification accuracy |
| Reactive recall | recall on reactive (non-spectator) groups |
| Spectator precision | precision on spectator predictions |
| Reaction center IoU | overlap between predicted and true reaction-center atoms |

Target: >80% role accuracy on the 5 benchmark reactions.

---

## 7. Tech Stack

| Component | Library |
|---|---|
| Cheminformatics | RDKit |
| 3D structure | ASE, OpenBabel |
| MLIP | MACE (mace-torch) |
| ML framework | PyTorch |
| Visualization | py3Dmol, matplotlib |
| Pre-optimization | xTB (optional) |

All open source. No API calls. Fully local.

---

## 8. Timeline (6 weeks)

| Week | Task | Deliverable |
|---|---|---|
| 1 | SMARTS group identifier | Module 1 working |
| 2 | Descriptor builder + label 50 reactions | Training data |
| 3 | Group agent NN + training | Trained model |
| 4 | Negotiation + MLIP wrapper | End-to-end pipeline |
| 5 | Run 5 benchmark reactions | Results table |
| 6 | Analysis + visualization + report | Final deliverable |

---

## 9. Out of Scope (for this project)

- Transition state search
- Reaction barrier prediction
- Multi-step mechanism discovery
- Inorganic / organometallic systems
- LLM-based reasoning
- Training a new MLIP

These can be follow-ups once the core role-prediction system works.

---

## 10. Design Choices Justification

**Why functional group, not per-atom?**
Groups are the natural unit of chemical decision-making. Per-atom is too granular and loses chemical meaning.

**Why not element-level?**
Same element behaves very differently across functional groups (sp³ C in alkane vs sp² C in carbonyl). Element is not a behavior unit.

**Why rule-based negotiation?**
For project scope, rules are interpretable and debuggable. Learned negotiation is a future extension.

**Why foundation MLIP instead of training one?**
MACE-OFF / MACE-MP-0 are state-of-the-art and free. Training a new MLIP is not where the novelty lies in this project.

**Why no API?**
Group role classification is a small NN task. Doesn't need LLM reasoning. Local execution keeps cost zero and inference fast (ms-level).
