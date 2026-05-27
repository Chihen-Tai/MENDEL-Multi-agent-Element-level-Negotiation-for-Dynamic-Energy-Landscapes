# Phase 8.5: Dataset Quality and MLP Readiness

`mendel/dataset_quality.py` normalizes mechanism labels and reports dataset quality
issues before MLP training or benchmark evaluation.

## Purpose

Phase 8 showed that the current MLP is data-limited:

| Predictor | Overall role accuracy |
|-----------|----------------------:|
| `rule_based_local` | 0.667 |
| `rule_based_negotiated` | 0.792 |
| `mlp_local` | 0.417 |
| `mlp_negotiated` | 0.417 |

The negotiated rule-based pipeline remains the best-performing default. Phase 8.5
improves the data layer so future MLP training is easier to interpret.

## Normalize and Check Data

```bash
python scripts/normalize_dataset.py \
  --input data/reactions.json \
  --output data/reactions.normalized.json \
  --report reports/dataset_quality_report.json
```

To replace the input dataset, the CLI must be explicit:

```bash
python scripts/normalize_dataset.py \
  --input data/reactions.json \
  --output data/reactions.normalized.json \
  --report reports/dataset_quality_report.json \
  --overwrite
```

`--overwrite` first creates `data/reactions.json.backup_before_phase8_5`.

## Auto Candidate Generation

MENDELV can generate a local template-based starter set of draft candidate
reactions, then run Phase 6.5 draft labeling and filtering:

```bash
python scripts/generate_candidate_reactions.py \
  --output data/draft_inputs.auto_candidates.json

python scripts/auto_draft_and_filter.py \
  --input data/draft_inputs.auto_candidates.json
```

The outputs are draft labels only. Manual review is required before merging any
candidate into `data/reactions.json` or using it for training.

## What Gets Checked

- mechanism label consistency
- split validity
- empty reactions and empty reaction-center labels
- draft labels and manual-review flags
- duplicate `group_id` entries
- missing notes
- low-count roles and mechanisms
- context-level sanity checks for ionic, radical, and pericyclic reactions

## Data Targets

- Minimum smoke training: 20-50 group labels
- Early meaningful MLP training: 100-300 group labels
- Better benchmark: 50-100 reactions

These are practical thresholds, not guarantees. The current dataset is still small
enough that MLP metrics should be treated as early evidence only.

## Known Limitations

- The current functional-group schema cannot represent free hydroxide, cyanide, Br2,
  and related species as reactive agents in some cases.
- Atom mapping and reaction-center labels may be incomplete.
- The flat role taxonomy loses donor/acceptor subroles.
- Data remains manually curated and should be reviewed before MLP training.
- This phase does not add MLIP, MACE, Transition1x, energy, force, transition-state,
  or barrier prediction.

## Status

The MLP remains experimental until benchmark results show it improves over the
rule-based negotiated pipeline. Functional group = agent remains the core abstraction.
