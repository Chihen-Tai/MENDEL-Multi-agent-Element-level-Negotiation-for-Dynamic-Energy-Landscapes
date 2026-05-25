# MENDEL

**Molecular Element-group NeDotiation for Energy Landscapes**

A functional-group-level role prediction system for organic reactions. Given a molecule and reaction context, MENDEL identifies functional groups, predicts each group's role (electrophile / nucleophile / radical / leaving / spectator), and pairs this with a foundation MLIP for energy/force computation.

---

## Concept

Each functional group is treated as an **agent** that predicts its own role in a reaction. Agents then negotiate to produce a coherent assignment.

```
Molecule
   │
   ▼
Functional group decomposition (RDKit + SMARTS)
   │
   ▼
Each group → role prediction (small NN)
   │
   ▼
Negotiation layer (rule-based)
   │
   ▼
Foundation MLIP (MACE-OFF / MACE-MP-0) → E, F
   │
   ▼
Output: roles + reaction center + energy + visualization
```

---

## Project Scope

| | |
|---|---|
| Group definition | SMARTS pattern matching (~20 predefined groups) |
| Chemical scope | Small organic molecule reactions |
| Agent capability | Role prediction only |
| MLIP | Foundation model (no training) |
| Timeline | ~6 weeks |
| Cost | $0 (no API, fully local) |

---

## Repository Structure

```
mendel/
├── README.md           ← this file
├── DESIGN.md           ← full architecture spec
├── BENCHMARK.md        ← benchmark reactions and expected outputs
├── TEMPLATE.md         ← template for adding new functional groups
└── groups/             ← per-group specifications
    ├── alkene.md
    ├── alkyne.md
    ├── aromatic.md
    ├── alcohol.md
    ├── ether.md
    ├── carbonyl.md
    ├── carboxylic_acid.md
    ├── ester.md
    ├── amine.md
    ├── amide.md
    ├── halide.md
    ├── nitrile.md
    └── alpha_carbon.md   (contextual: sp³ C-H α to EWG)
```

---

## Quick Start (planned)

```python
from mendel import MENDEL

m = MENDEL()
result = m.predict(
    reactants=["CH3Br", "[OH-]"],
    products=["CH3OH", "[Br-]"],
    context="ionic"
)

print(result.roles)
# {'halide': 'leaving_group',
#  'hydroxide': 'nucleophile',
#  'methyl': 'electrophile'}

print(result.energy)        # MLIP energy
print(result.reaction_center)  # atoms involved
result.visualize()           # colored 3D structure
```

---

## Status

Project specification phase. Implementation TBD.

---

## Design Principles

- **Project, not research**: prioritize working demo over ML novelty
- **Interpretable**: every prediction must be chemically explainable
- **Modular**: each module can be swapped out
- **Honest framing**: agent = group-level role predictor, no overclaiming
- **Zero cost**: no API, fully local
