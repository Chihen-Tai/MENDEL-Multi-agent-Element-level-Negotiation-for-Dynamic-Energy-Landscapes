"""Phase 8.5 dataset quality and normalization tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from mendel.dataset_quality import (
    build_dataset_quality_report,
    canonicalize_mechanism_type,
    check_labeled_reaction_quality,
    normalize_labeled_dataset,
    normalize_labeled_reaction,
    save_dataset_quality_report,
    suggest_dataset_improvements,
)
from mendel.labels import LabeledGroupRole, LabeledReaction, load_labeled_reactions
from mendel.types import FunctionalGroupType, ReactionContext, Role

_ROOT = Path(__file__).parent.parent
_MINIMAL = _ROOT / "data" / "reactions.minimal.json"
_SCRIPT = _ROOT / "scripts" / "normalize_dataset.py"


def _label(
    group_id: str = "mol0_halide_0",
    confidence: str = "manual",
    notes: str | None = "curated label",
) -> LabeledGroupRole:
    return LabeledGroupRole(
        group_id=group_id,
        molecule_index=0,
        group_type=FunctionalGroupType.halide,
        atom_indices=[0, 1],
        role=Role.leaving_group,
        confidence=confidence,
        notes=notes,
    )


def _reaction(
    mechanism_type: str = "SN2",
    split: str = "train",
    roles: list[LabeledGroupRole] | None = None,
    metadata: dict[str, object] | None = None,
) -> LabeledReaction:
    return LabeledReaction(
        reaction_id="rxn1",
        reaction_smiles="CBr.[OH-]>>CO.[Br-]",
        context=ReactionContext.ionic,
        mechanism_type=mechanism_type,
        split=split,
        group_roles=roles if roles is not None else [_label()],
        reaction_center_atoms=[0, 1],
        metadata=dict(metadata or {}),
    )


def test_canonicalize_mechanism_type_known_aliases() -> None:
    assert canonicalize_mechanism_type("SN2") == "sn2"
    assert canonicalize_mechanism_type("Diels-Alder") == "diels_alder"
    assert (
        canonicalize_mechanism_type("Benzylic radical bromination")
        == "benzylic_radical_bromination"
    )


def test_canonicalize_unknown_mechanism_deterministically() -> None:
    assert canonicalize_mechanism_type("My New-Mechanism") == "my_new_mechanism"


def test_normalize_labeled_reaction_does_not_mutate_input() -> None:
    rxn = _reaction(mechanism_type="Diels-Alder")

    normalized = normalize_labeled_reaction(rxn)

    assert rxn.mechanism_type == "Diels-Alder"
    assert normalized.mechanism_type == "diels_alder"
    assert normalized.metadata["original_mechanism_type"] == "Diels-Alder"
    assert normalized.metadata["normalized_by"] == "MENDELV Phase 8.5"


def test_normalize_labeled_dataset_preserves_length_and_ordering() -> None:
    reactions = [
        _reaction(mechanism_type="SN2"),
        _reaction(mechanism_type="Aldol"),
    ]
    reactions[0].reaction_id = "first"
    reactions[1].reaction_id = "second"

    normalized = normalize_labeled_dataset(reactions)

    assert [r.reaction_id for r in normalized] == ["first", "second"]
    assert [r.mechanism_type for r in normalized] == ["sn2", "aldol"]


def test_check_quality_flags_empty_group_roles() -> None:
    issues = check_labeled_reaction_quality(_reaction(roles=[]))

    assert any(issue.code == "no_group_roles" for issue in issues)


def test_check_quality_flags_draft_confidence() -> None:
    issues = check_labeled_reaction_quality(_reaction(roles=[_label(confidence="draft")]))

    assert any(issue.code == "draft_label" for issue in issues)


def test_check_quality_flags_duplicate_group_id() -> None:
    issues = check_labeled_reaction_quality(
        _reaction(roles=[_label("dup"), _label("dup")])
    )

    assert any(issue.code == "duplicate_group_id" for issue in issues)


def test_build_dataset_quality_report_counts_and_serializes() -> None:
    report = build_dataset_quality_report([
        _reaction(mechanism_type="SN2"),
        _reaction(mechanism_type="Aldol", split="val"),
    ])
    payload = report.to_dict()

    assert report.n_reactions == 2
    assert report.n_group_labels == 2
    assert report.role_distribution["leaving_group"] == 2
    assert report.mechanism_distribution["sn2"] == 1
    assert report.split_distribution["val"] == 1
    assert isinstance(payload["issues"], list)


def test_suggest_dataset_improvements_for_low_counts() -> None:
    report = build_dataset_quality_report([_reaction()])

    suggestions = suggest_dataset_improvements(report)

    assert suggestions
    assert any("labels" in suggestion.lower() for suggestion in suggestions)


def test_save_dataset_quality_report_writes_json(tmp_path: Path) -> None:
    report = build_dataset_quality_report([_reaction()])
    path = tmp_path / "quality.json"

    save_dataset_quality_report(report, path)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["n_reactions"] == 1


def test_cli_smoke_normalizes_minimal_without_overwrite(tmp_path: Path) -> None:
    output = tmp_path / "normalized.json"
    report = tmp_path / "report.json"

    result = subprocess.run(
        [
            sys.executable,
            str(_SCRIPT),
            "--input",
            str(_MINIMAL),
            "--output",
            str(output),
            "--report",
            str(report),
        ],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    assert output.exists()
    assert report.exists()
    assert load_labeled_reactions(_MINIMAL)[0].mechanism_type == "SN2"
