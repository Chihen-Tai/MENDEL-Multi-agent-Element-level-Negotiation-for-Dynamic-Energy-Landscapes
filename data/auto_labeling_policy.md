# MENDELV Auto-Labeling Policy

Functional group = agent.

Auto-generated labels are draft labels only. They are produced by running the
existing rule-based functional-group agent pipeline over candidate reaction
SMILES, so they are model suggestions, not ground truth.

## Rules

- Ground truth must be manually reviewed.
- Keep `confidence="draft"` until a reviewer has checked the group identity,
  role, atom indices, reaction center, and mechanism label.
- Keep `metadata.needs_manual_review=true` until review is complete.
- Do not train a final MLP on auto labels. Draft labels may only be used for
  documented smoke tests.
- Do not promote examples from sources with unclear licenses.
- Do not promote invalid or chemically nonsensical products.

## Safe-To-Promote After Review

- Simple alkyl or benzyl halide `leaving_group` labels in SN2/E2 examples.
- `benzylic_site` as `reactive_radical` in benzylic bromination examples.
- Simple Diels-Alder diene/dienophile alkene labels when the detected group IDs
  match the actual reacting pi systems.

## Needs Manual Review

- Aldol and cross-aldol donor/acceptor assignments.
- Carbonyl addition where the external nucleophile is unsupported by the current
  functional-group schema.
- Controls where all detected groups should be spectator.
- Nitrile, nitro, and ester roles.
- Product-simplified examples.
- Examples with warnings from negotiation.
- Examples with empty reaction-center atoms.

## Exclude

- Reactions with no detected functional groups unless they are retained only as
  documented limitations.
- Invalid reaction SMILES.
- Chemically nonsensical products after review.
- Any commercial, paywalled, scraped, or license-restricted data source.

The auto-candidate pipeline creates reviewable situations for functional-group
agents. It does not solve curation automatically.
