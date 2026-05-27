# MENDEL

**Molecular Entity Negotiation for Dynamic Energy Landscapes** — a fully local, functional-group-level reaction role prediction framework for organic chemistry.

Each functional group in a molecule is treated as an **agent** that observes its local chemical environment, predicts its own reaction role, then negotiates with neighbouring groups to produce a coherent, conflict-free assignment.

---

## Quick Demo

```python
import mendel
from mendel.negotiator import run_full_rule_pipeline

result = run_full_rule_pipeline(
    "CBr.[OH-]>>CO.[Br-]",
    context="ionic",
)

print(mendel.__version__)       # 0.1.0
print(result.mechanism_hint)    # sn2_or_e2_like
```

`import mendel` does not import PyTorch. Phase 7 MLP APIs must be imported directly from `mendel.mlp`.

---

## Pipeline

```
reaction SMILES + context
         │
         ▼
  functional group detection       (identifier.py — RDKit SMARTS, 3-pass)
         │
         ▼
  per-group descriptor building    (descriptor.py — 55-dim feature vector)
         │
         ▼
  per-group role prediction        (predictor.py — rule-based baseline)
         │
         ▼
  negotiation / conflict resolution (negotiator.py — mechanism hints, reaction center)
         │
         ▼
  [optional] MLP role predictor    (mlp.py — learned, Phase 7)
         │
         ▼
  [future] MLIP energy / forces    (Phase 8 — MACE/Transition1x)
```

### Roles

Five mutually exclusive roles per functional group per reaction step:

| Role | Description |
|------|-------------|
| `reactive_nucleophile` | donates electrons |
| `reactive_electrophile` | accepts electrons |
| `reactive_radical` | radical center |
| `leaving_group` | departs with electron pair |
| `spectator` | uninvolved in this step |

---

## Install

```bash
git clone <repo-url>
cd mendel
conda create -n mendel python=3.12
conda activate mendel
pip install -e ".[dev]"          # Phases 0–6 + tests
pip install -e ".[ml]"           # Phase 7 only — installs torch
```

Requires Python ≥ 3.10 and RDKit.

---

## Current Status

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Project scaffold and data contracts | ✓ |
| 1 | Reaction SMILES parser | ✓ |
| 2 | Functional group identifier (RDKit + SMARTS) | ✓ |
| 3 | Group descriptor builder (55-dim) | ✓ |
| 4 | Labeled data schema | ✓ |
| 5 | Rule-based role predictor | ✓ |
| 6 | Negotiation layer | ✓ |
| 6.5 | Dataset curation / draft label generation | ✓ |
| 7 | MLP role predictor training | ✓ (needs more curated data) |
| 8 | Benchmark evaluator | ✓ |
| 8.5 | Dataset normalization + MLP readiness diagnostics | ✓ |

---

## Validation

### Phase 0–6 (no PyTorch required)

```bash
PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider \
  tests/test_phase0_scaffold.py tests/test_parser.py \
  tests/test_identifier.py tests/test_descriptor.py \
  tests/test_labels.py tests/test_predictor.py tests/test_negotiator.py
```

### Phase 6.5 — curation

```bash
pytest tests/test_curation.py -q
```

### Phase 7 — MLP (requires `pip install -e ".[ml]"`)

```bash
pytest tests/test_mlp.py -q
```

---

## Dataset Curation (Phase 6.5)

Before Phase 7 training can produce meaningful results, a curated labeled dataset must be built. Phase 6.5 generates draft labels from the rule-based pipeline for manual review.

```bash
# Generate draft labels from 5 core benchmark reactions
python scripts/draft_labels.py \
  --core \
  --output data/reactions.draft.core.json \
  --report reports/draft_core_report.json

# Generate draft labels from all 15 extended reactions
python scripts/draft_labels.py \
  --core --extended \
  --output data/reactions.draft.json \
  --report reports/draft_report.json
```

Draft records carry `confidence="draft"` and `needs_manual_review=true`. A chemist must inspect and correct roles, change the split to `train`/`val`/`test`, and set `needs_manual_review=false` before adding records to `data/reactions.json`.

See [docs/curation.md](docs/curation.md) for the full curation workflow.

---

## MLP Training (Phase 7)

Trains a small PyTorch MLP (55 → hidden → 5) on descriptor vectors. Does **not** require MACE, MLIP, or any energy model.

**Smoke test** (minimal dataset, no curated labels needed):

```bash
python scripts/train_mlp.py \
  --data data/reactions.minimal.json \
  --output models/role_mlp_minimal.pt \
  --report reports/mlp_minimal_report.json \
  --epochs 3 --hidden-dim 16 --batch-size 4 \
  --allow-draft-labels
```

**Full training** (requires curated `data/reactions.json`):

```bash
python scripts/train_mlp.py \
  --data data/reactions.json \
  --output models/role_mlp.pt \
  --report reports/mlp_training_report.json \
  --epochs 100
```

See [docs/mlp.md](docs/mlp.md) for the full API reference.

## Benchmarking

Compare the rule-based local predictor against the negotiated rule-based pipeline:

```bash
python scripts/benchmark.py --data data/reactions.json --rule-based --negotiated
```

Optionally evaluate an existing MLP checkpoint:

```bash
python scripts/benchmark.py --data data/reactions.json --mlp-checkpoint models/role_mlp.pt --device cpu
```

The MLP checkpoint command evaluates both `mlp_local` and `mlp_negotiated`.
These commands evaluate existing predictors only. They do not train the MLP and do not
use MLIP, MACE, Transition1x, energies, forces, transition states, or barriers.

See [docs/benchmark.md](docs/benchmark.md) for the Phase 8 metric definitions and
limitations.

Current benchmark status:

- `rule_based_negotiated` is the best-performing current pipeline.
- The MLP is implemented and checkpoint-evaluable, but underperforms because the
  dataset is still small.
- Do not use the MLP as the default predictor until benchmark results improve.

Normalize and inspect the labeled dataset:

```bash
python scripts/normalize_dataset.py \
  --input data/reactions.json \
  --output data/reactions.normalized.json \
  --report reports/dataset_quality_report.json
```

See [docs/dataset_quality.md](docs/dataset_quality.md) for Phase 8.5 guidance.

---

## Repository Structure

```
mendel/
├── mendel/
│   ├── __init__.py         ← public entry point (no PyTorch)
│   ├── types.py            ← core enums and dataclasses
│   ├── constants.py        ← derived constant sets
│   ├── parser.py           ← reaction SMILES parser
│   ├── identifier.py       ← functional group identifier
│   ├── descriptor.py       ← 55-dim descriptor builder
│   ├── labels.py           ← labeled data schema
│   ├── predictor.py        ← rule-based role predictor
│   ├── negotiator.py       ← negotiation layer
│   ├── curation.py         ← draft label generation (Phase 6.5)
│   ├── mlp.py              ← MLP role predictor (Phase 7)
│   ├── benchmark.py        ← benchmark evaluator (Phase 8)
│   └── dataset_quality.py  ← normalization and diagnostics (Phase 8.5)
├── scripts/
│   ├── draft_labels.py     ← CLI: generate draft labels
│   ├── train_mlp.py        ← CLI: train MLP
│   ├── benchmark.py        ← CLI: evaluate predictors
│   └── normalize_dataset.py ← CLI: normalize/check labels
├── data/
│   ├── reactions.json               ← curated labeled reactions
│   ├── reactions.minimal.json       ← 2-reaction subset for fast tests
│   ├── reactions.example.json       ← schema reference
│   └── draft_inputs.example.json   ← draft input format reference
├── tests/
│   ├── test_phase0_scaffold.py
│   ├── test_parser.py
│   ├── test_identifier.py
│   ├── test_descriptor.py
│   ├── test_labels.py
│   ├── test_predictor.py
│   ├── test_negotiator.py
│   ├── test_curation.py
│   └── test_mlp.py
├── docs/
│   ├── index.md
│   ├── descriptor.md
│   ├── labels.md
│   ├── predictor.md
│   ├── negotiator.md
│   ├── curation.md
│   └── mlp.md
├── groups/                 ← per-group SMARTS specifications
├── DESIGN.md               ← full architecture spec
├── BENCHMARK.md            ← benchmark reactions
└── TEMPLATE.md             ← template for adding a new functional group
```

---

## Design Principles

- **Functional group = agent** — the natural unit of organic chemistry decision-making
- **Interpretable** — every prediction is chemically explainable
- **Modular** — each phase is independently testable and swappable
- **Fully local** — no API calls, no external services
