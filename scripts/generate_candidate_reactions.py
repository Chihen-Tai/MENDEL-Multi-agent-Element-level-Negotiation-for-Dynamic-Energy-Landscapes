"""Generate local template-based draft reaction inputs for MENDELV.

The generated records are candidates for Phase 6.5 draft labeling only.
They are not ground truth and must be manually reviewed before any use as
curated training data.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from mendel.parser import ReactionParseError, parse_reaction_smiles

Scalar = str | int | float | bool
CandidateRecord = dict[str, Any]

DEFAULT_OUTPUT = Path("data/draft_inputs.auto_candidates.json")
SOURCE = "MENDELV template starter set"
LICENSE_NOTE = (
    "Generated from generic textbook-style reaction patterns; no external "
    "reaction dataset or copyrighted table used."
)
GENERATION_METHOD = "deterministic_template_v1"


def _metadata(labeling_note: str, **extra: Scalar) -> dict[str, Scalar]:
    metadata: dict[str, Scalar] = {
        "source": SOURCE,
        "source_type": "local_template",
        "license_note": LICENSE_NOTE,
        "generation_method": GENERATION_METHOD,
        "needs_manual_review": True,
        "labeling_note": labeling_note,
        "exclude_from_ground_truth_until_review": True,
    }
    metadata.update(extra)
    return metadata


def _record(
    reaction_id: str,
    reaction_smiles: str,
    context: str,
    mechanism_type: str,
    labeling_note: str,
    **metadata: Scalar,
) -> CandidateRecord:
    return {
        "reaction_id": reaction_id,
        "reaction_smiles": reaction_smiles,
        "context": context,
        "mechanism_type": mechanism_type,
        "split": "draft",
        "metadata": _metadata(labeling_note, **metadata),
    }


def _template_records() -> dict[str, list[CandidateRecord]]:
    unsupported_external = (
        "External reagent may not be represented by current functional-group schema."
    )
    product_review = {
        "product_simplified": True,
        "exclude_from_ground_truth_until_review": True,
    }
    return {
        "sn2": [
            _record(
                "auto_sn2_methyl_bromide_iodide",
                "CBr.[I-]>>CI.[Br-]",
                "ionic",
                "sn2",
                "Detected alkyl halide should be reviewed as leaving_group.",
            ),
            _record(
                "auto_sn2_methyl_chloride_iodide",
                "CCl.[I-]>>CI.[Cl-]",
                "ionic",
                "sn2",
                "Detected alkyl halide should be reviewed as leaving_group.",
            ),
            _record(
                "auto_sn2_ethyl_bromide_methoxide",
                "CCBr.[O-]C>>CCOC.[Br-]",
                "ionic",
                "sn2",
                "Halide is expected leaving_group; methoxide may be unsupported.",
                unsupported_reagent_note=unsupported_external,
            ),
            _record(
                "auto_sn2_ethyl_chloride_thiolate",
                "CCCl.[S-]C>>CCSC.[Cl-]",
                "ionic",
                "sn2",
                "Halide is expected leaving_group; thiolate may be unsupported.",
                unsupported_reagent_note=unsupported_external,
            ),
            _record(
                "auto_sn2_methyl_bromide_cyanide",
                "CBr.[C-]#N>>CC#N.[Br-]",
                "ionic",
                "sn2",
                "Halide is expected leaving_group; cyanide may be unsupported.",
                unsupported_reagent_note=unsupported_external,
            ),
            _record(
                "auto_sn2_benzyl_chloride_methoxide",
                "ClCc1ccccc1.[O-]C>>COCc1ccccc1.[Cl-]",
                "ionic",
                "sn2",
                "Benzyl halide should be reviewed as leaving_group.",
                unsupported_reagent_note=unsupported_external,
            ),
            _record(
                "auto_sn2_benzyl_bromide_iodide",
                "BrCc1ccccc1.[I-]>>ICc1ccccc1.[Br-]",
                "ionic",
                "sn2",
                "Benzyl halide should be reviewed as leaving_group.",
            ),
            _record(
                "auto_sn2_ethyl_iodide_azide",
                "CCI.[N-]=[N+]=[N-]>>CCN=[N+]=[N-].[I-]",
                "ionic",
                "sn2",
                "Halide is expected leaving_group; azide may be unsupported.",
                unsupported_reagent_note=unsupported_external,
                product_simplified=True,
            ),
            _record(
                "auto_sn2_isopropyl_bromide_iodide",
                "CC(C)Br.[I-]>>CC(C)I.[Br-]",
                "ionic",
                "sn2",
                "Secondary alkyl halide substitution candidate; review for competing E2.",
                **product_review,
            ),
        ],
        "e2": [
            _record(
                "auto_e2_isopropyl_bromide_hydroxide",
                "CC(Br)C.[OH-]>>C=CC.[Br-].[OH2]",
                "ionic",
                "e2",
                "Halide leaving_group is expected; beta C-H/base are not explicit agents.",
                unsupported_reagent_note=unsupported_external,
            ),
            _record(
                "auto_e2_isopropyl_chloride_hydroxide",
                "CC(Cl)C.[OH-]>>C=CC.[Cl-].[OH2]",
                "ionic",
                "e2",
                "Halide leaving_group is expected; beta C-H/base are not explicit agents.",
                unsupported_reagent_note=unsupported_external,
            ),
            _record(
                "auto_e2_tertbutyl_bromide_hydroxide",
                "CC(C)(C)Br.[OH-]>>CC(=C)C.[Br-].[OH2]",
                "ionic",
                "e2",
                "Tertiary halide should be reviewed as leaving_group.",
                unsupported_reagent_note=unsupported_external,
            ),
            _record(
                "auto_e2_2_bromobutane_hydroxide",
                "CCC(Br)C.[OH-]>>CC=CC.[Br-].[OH2]",
                "ionic",
                "e2",
                "Halide leaving_group expected; alkene regiochemistry simplified.",
                unsupported_reagent_note=unsupported_external,
                **product_review,
            ),
            _record(
                "auto_e2_cyclohexyl_bromide_hydroxide",
                "C1CCC(Br)CC1.[OH-]>>C1=CCCCC1.[Br-].[OH2]",
                "ionic",
                "e2",
                "Cyclic alkyl bromide leaving_group; base not represented.",
                unsupported_reagent_note=unsupported_external,
            ),
            _record(
                "auto_e2_2_bromobutane_methoxide",
                "CCC(Br)C.[O-]C>>CC=CC.[Br-].CO",
                "ionic",
                "e2",
                "Halide leaving_group expected; methoxide base may be unsupported.",
                unsupported_reagent_note=unsupported_external,
                **product_review,
            ),
            _record(
                "auto_e2_tertbutyl_chloride_hydroxide",
                "CC(C)(C)Cl.[OH-]>>CC(=C)C.[Cl-].[OH2]",
                "ionic",
                "e2",
                "Tertiary chloride should be reviewed as leaving_group.",
                unsupported_reagent_note=unsupported_external,
            ),
        ],
        "aldol": [
            _record(
                "auto_aldol_acetaldehyde_self",
                "CC=O.CC=O>>CC(O)CC=O",
                "ionic",
                "aldol",
                "Aldol donor/acceptor labels must be manually reviewed.",
                **product_review,
            ),
            _record(
                "auto_aldol_acetone_self",
                "CC(=O)C.CC(=O)C>>CC(=O)CC(O)(C)C",
                "ionic",
                "aldol",
                "Aldol donor/acceptor labels must be manually reviewed.",
                **product_review,
            ),
            _record(
                "auto_aldol_propanal_self",
                "CCC=O.CCC=O>>CCC(O)C(C)C=O",
                "ionic",
                "aldol",
                "Aldol donor/acceptor labels must be manually reviewed.",
                **product_review,
            ),
        ],
        "cross_aldol": [
            _record(
                "auto_cross_aldol_acetaldehyde_benzaldehyde",
                "CC=O.O=Cc1ccccc1>>CC(O)Cc1ccccc1",
                "ionic",
                "cross_aldol",
                "Cross-aldol donor/acceptor labels must be manually reviewed.",
                **product_review,
            ),
            _record(
                "auto_cross_aldol_acetone_benzaldehyde",
                "CC(=O)C.O=Cc1ccccc1>>CC(=O)CC(O)c1ccccc1",
                "ionic",
                "cross_aldol",
                "Cross-aldol donor/acceptor labels must be manually reviewed.",
                **product_review,
            ),
            _record(
                "auto_cross_aldol_propanal_benzaldehyde",
                "CCC=O.O=Cc1ccccc1>>CCC(O)Cc1ccccc1",
                "ionic",
                "cross_aldol",
                "Cross-aldol donor/acceptor labels must be manually reviewed.",
                **product_review,
            ),
        ],
        "carbonyl_addition": [
            _record(
                "auto_carbonyl_addition_acetaldehyde_hydride",
                "CC=O.[BH4-]>>CC[O-]",
                "ionic",
                "carbonyl_addition",
                "Carbonyl should be reviewed as reactive_electrophile; hydride-like reagent unsupported.",
                unsupported_reagent_note=unsupported_external,
            ),
            _record(
                "auto_carbonyl_addition_acetone_hydride",
                "CC(=O)C.[BH4-]>>CC(C)[O-]",
                "ionic",
                "carbonyl_addition",
                "Carbonyl should be reviewed as reactive_electrophile; hydride-like reagent unsupported.",
                unsupported_reagent_note=unsupported_external,
            ),
            _record(
                "auto_carbonyl_addition_acetaldehyde_cyanide",
                "CC=O.[C-]#N>>CC(O)C#N",
                "ionic",
                "carbonyl_addition",
                "Carbonyl electrophile expected; cyanide reagent may be unsupported.",
                unsupported_reagent_note=unsupported_external,
                **product_review,
            ),
            _record(
                "auto_carbonyl_addition_acetone_cyanide",
                "CC(=O)C.[C-]#N>>CC(O)(C)C#N",
                "ionic",
                "carbonyl_addition",
                "Carbonyl electrophile expected; cyanide reagent may be unsupported.",
                unsupported_reagent_note=unsupported_external,
                **product_review,
            ),
            _record(
                "auto_carbonyl_addition_benzaldehyde_cyanide",
                "O=Cc1ccccc1.[C-]#N>>OC(C#N)c1ccccc1",
                "ionic",
                "carbonyl_addition",
                "Carbonyl electrophile expected; cyanide reagent may be unsupported.",
                unsupported_reagent_note=unsupported_external,
                **product_review,
            ),
            _record(
                "auto_carbonyl_addition_formaldehyde_hydride",
                "C=O.[BH4-]>>C[O-]",
                "ionic",
                "carbonyl_addition",
                "Carbonyl should be reviewed as reactive_electrophile; hydride-like reagent unsupported.",
                unsupported_reagent_note=unsupported_external,
            ),
            _record(
                "auto_carbonyl_addition_benzaldehyde_hydride",
                "O=Cc1ccccc1.[BH4-]>>[O-]Cc1ccccc1",
                "ionic",
                "carbonyl_addition",
                "Carbonyl should be reviewed as reactive_electrophile; hydride-like reagent unsupported.",
                unsupported_reagent_note=unsupported_external,
            ),
        ],
        "diels_alder": [
            _record(
                "auto_diels_alder_butadiene_ethylene",
                "C=CC=C.C=C>>C1CCC=CC1",
                "pericyclic",
                "diels_alder",
                "Diene/dienophile alkene roles must be reviewed by group_id.",
                **product_review,
            ),
            _record(
                "auto_diels_alder_butadiene_acrylonitrile",
                "C=CC=C.C=CC#N>>N#CC1CCC=CC1",
                "pericyclic",
                "diels_alder",
                "Dienophile alkene expected reactive; nitrile usually spectator.",
                **product_review,
            ),
            _record(
                "auto_diels_alder_butadiene_methyl_acrylate",
                "C=CC=C.C=CC(=O)OC>>COC(=O)C1CCC=CC1",
                "pericyclic",
                "diels_alder",
                "Dienophile alkene expected reactive; ester substituent usually spectator.",
                **product_review,
            ),
            _record(
                "auto_diels_alder_butadiene_methyl_vinyl_ketone",
                "C=CC=C.C=CC(C)=O>>CC(=O)C1CCC=CC1",
                "pericyclic",
                "diels_alder",
                "Dienophile alkene expected reactive; carbonyl substituent usually spectator.",
                **product_review,
            ),
            _record(
                "auto_diels_alder_isoprene_ethylene",
                "C=C(C)C=C.C=C>>CC1CCC=CC1",
                "pericyclic",
                "diels_alder",
                "Diene/dienophile alkene roles must be reviewed by group_id.",
                **product_review,
            ),
        ],
        "benzylic_radical_bromination": [
            _record(
                "auto_benzylic_bromination_toluene",
                "Cc1ccccc1.BrBr>>BrCc1ccccc1.Br",
                "radical",
                "benzylic_radical_bromination",
                "Benzylic site should be reviewed as reactive_radical; Br2 unsupported.",
                unsupported_reagent_note="Br2 is not represented by the current schema.",
                **product_review,
            ),
            _record(
                "auto_benzylic_bromination_ethylbenzene",
                "CCc1ccccc1.BrBr>>CC(Br)c1ccccc1.Br",
                "radical",
                "benzylic_radical_bromination",
                "Benzylic site should be reviewed as reactive_radical; Br2 unsupported.",
                unsupported_reagent_note="Br2 is not represented by the current schema.",
                **product_review,
            ),
            _record(
                "auto_benzylic_bromination_cumene",
                "CC(C)c1ccccc1.BrBr>>CC(Br)(C)c1ccccc1.Br",
                "radical",
                "benzylic_radical_bromination",
                "Benzylic site should be reviewed as reactive_radical; Br2 unsupported.",
                unsupported_reagent_note="Br2 is not represented by the current schema.",
                **product_review,
            ),
        ],
        "radical_bromination": [
            _record(
                "auto_radical_bromination_ethane",
                "CC.BrBr>>CCBr.Br",
                "radical",
                "radical_bromination",
                "Alkane C-H abstraction may not be represented by current functional groups.",
                unsupported_reagent_note="Br2 is not represented by the current schema.",
                **product_review,
            ),
            _record(
                "auto_radical_bromination_propane",
                "CCC.BrBr>>CC(C)Br.Br",
                "radical",
                "radical_bromination",
                "Alkane C-H abstraction may not be represented by current functional groups.",
                unsupported_reagent_note="Br2 is not represented by the current schema.",
                **product_review,
            ),
        ],
        "control": [
            _record(
                "auto_control_benzene_no_reaction",
                "c1ccccc1>>c1ccccc1",
                "unknown",
                "control",
                "Negative control; detected groups should usually be spectator.",
            ),
            _record(
                "auto_control_toluene_no_reaction",
                "Cc1ccccc1>>Cc1ccccc1",
                "unknown",
                "control",
                "Negative control; detected groups should usually be spectator.",
            ),
            _record(
                "auto_control_anisole_no_reaction",
                "COc1ccccc1>>COc1ccccc1",
                "unknown",
                "control",
                "Negative control; detected groups should usually be spectator.",
            ),
            _record(
                "auto_control_phenol_no_reaction",
                "Oc1ccccc1>>Oc1ccccc1",
                "unknown",
                "control",
                "Negative control; detected groups should usually be spectator.",
            ),
            _record(
                "auto_control_ethanol_no_reaction",
                "CCO>>CCO",
                "unknown",
                "control",
                "Negative control; detected groups should usually be spectator.",
            ),
            _record(
                "auto_control_nitrobenzene_no_reaction",
                "O=[N+]([O-])c1ccccc1>>O=[N+]([O-])c1ccccc1",
                "unknown",
                "control",
                "Negative control; nitro and aromatic groups should usually be spectator.",
            ),
            _record(
                "auto_control_cyclohexane_no_reaction",
                "C1CCCCC1>>C1CCCCC1",
                "unknown",
                "control",
                "Negative control; may produce no detected functional groups.",
            ),
        ],
        "nitroalkane_deprotonation": [
            _record(
                "auto_nitro_methane_deprotonation",
                "C[N+](=O)[O-].[OH-]>>[CH2-][N+](=O)[O-].O",
                "ionic",
                "nitroalkane_deprotonation",
                "Nitro/alpha-carbon role requires manual review.",
                unsupported_reagent_note=unsupported_external,
            ),
            _record(
                "auto_nitro_ethane_deprotonation",
                "CC[N+](=O)[O-].[OH-]>>C[CH-][N+](=O)[O-].O",
                "ionic",
                "nitroalkane_deprotonation",
                "Nitro/alpha-carbon role requires manual review.",
                unsupported_reagent_note=unsupported_external,
            ),
        ],
        "ester_control": [
            _record(
                "auto_ester_control_methyl_acetate_no_reaction",
                "CC(=O)OC>>CC(=O)OC",
                "unknown",
                "ester_control",
                "Ester control; current labels should be spectator unless reviewed otherwise.",
            ),
            _record(
                "auto_ester_control_ethyl_acetate_no_reaction",
                "CC(=O)OCC>>CC(=O)OCC",
                "unknown",
                "ester_control",
                "Ester control; current labels should be spectator unless reviewed otherwise.",
            ),
            _record(
                "auto_ester_control_methyl_benzoate_no_reaction",
                "COC(=O)c1ccccc1>>COC(=O)c1ccccc1",
                "unknown",
                "ester_control",
                "Ester and aromatic control; current labels should be spectator unless reviewed otherwise.",
            ),
        ],
        "nitrile_control": [
            _record(
                "auto_nitrile_control_acetonitrile_no_reaction",
                "CC#N>>CC#N",
                "unknown",
                "nitrile_control",
                "Nitrile control; current labels should be spectator unless reviewed otherwise.",
            ),
            _record(
                "auto_nitrile_control_benzonitrile_no_reaction",
                "N#Cc1ccccc1>>N#Cc1ccccc1",
                "unknown",
                "nitrile_control",
                "Nitrile control; current labels should be spectator unless reviewed otherwise.",
            ),
            _record(
                "auto_nitrile_control_propionitrile_no_reaction",
                "CCC#N>>CCC#N",
                "unknown",
                "nitrile_control",
                "Nitrile control; current labels should be spectator unless reviewed otherwise.",
            ),
        ],
    }


def generate_candidates(max_per_class: int = 10) -> list[CandidateRecord]:
    """Return deterministic draft candidate records, capped per mechanism class."""
    if max_per_class <= 0:
        raise ValueError("max_per_class must be positive")

    candidates: list[CandidateRecord] = []
    seen_ids: set[str] = set()
    seen_smiles: set[str] = set()

    for records in _template_records().values():
        for record in records[:max_per_class]:
            reaction_id = str(record["reaction_id"])
            reaction_smiles = str(record["reaction_smiles"])
            if reaction_id in seen_ids or reaction_smiles in seen_smiles:
                continue
            candidates.append(record)
            seen_ids.add(reaction_id)
            seen_smiles.add(reaction_smiles)

    validate_candidate_records(candidates)
    return candidates


def validate_candidate_records(candidates: list[CandidateRecord]) -> None:
    """Validate candidate schema and reaction SMILES parseability."""
    required = {"reaction_id", "reaction_smiles", "context", "mechanism_type", "split", "metadata"}
    seen_ids: set[str] = set()
    seen_smiles: set[str] = set()

    for i, candidate in enumerate(candidates):
        missing = required - set(candidate)
        if missing:
            raise ValueError(f"Candidate {i} missing required fields: {sorted(missing)}")

        reaction_id = candidate["reaction_id"]
        reaction_smiles = candidate["reaction_smiles"]
        metadata = candidate["metadata"]

        if reaction_id in seen_ids:
            raise ValueError(f"Duplicate reaction_id: {reaction_id}")
        if reaction_smiles in seen_smiles:
            raise ValueError(f"Duplicate reaction_smiles: {reaction_smiles}")
        seen_ids.add(reaction_id)
        seen_smiles.add(reaction_smiles)

        if candidate["split"] not in {"draft", "review"}:
            raise ValueError(f"{reaction_id}: split must be draft or review")
        if not isinstance(metadata, dict):
            raise ValueError(f"{reaction_id}: metadata must be an object")
        for key in (
            "source",
            "source_type",
            "license_note",
            "generation_method",
            "needs_manual_review",
            "labeling_note",
        ):
            if key not in metadata:
                raise ValueError(f"{reaction_id}: missing metadata.{key}")
        if metadata["needs_manual_review"] is not True:
            raise ValueError(f"{reaction_id}: metadata.needs_manual_review must be true")

        try:
            parse_reaction_smiles(str(reaction_smiles), str(candidate["context"]))
        except ReactionParseError as exc:
            raise ValueError(f"{reaction_id}: invalid reaction_smiles: {exc}") from exc


def save_candidates(candidates: list[CandidateRecord], path: str | Path) -> None:
    """Save candidate draft inputs as a top-level JSON list."""
    validate_candidate_records(candidates)
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(candidates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def summarize_candidates(candidates: list[CandidateRecord]) -> dict[str, int]:
    """Return candidate count by mechanism label."""
    return dict(sorted(Counter(str(c["mechanism_type"]) for c in candidates).items()))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate MENDELV draft reaction candidates.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output JSON path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--max-per-class",
        type=int,
        default=10,
        help="Maximum candidates per mechanism class (default: 10)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        candidates = generate_candidates(max_per_class=args.max_per_class)
        save_candidates(candidates, args.output)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    summary = summarize_candidates(candidates)
    print(f"Saved {len(candidates)} draft candidate reaction input(s) to {args.output}")
    print(f"Mechanism distribution: {summary}")
    print("Source: local template starter set; no external dataset used.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
