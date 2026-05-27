"""Tests for automatic draft candidate generation and filtering."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
sys.path.insert(0, str(_SCRIPTS_DIR))

from auto_draft_and_filter import run_auto_draft_pipeline
from generate_candidate_reactions import (
    generate_candidates,
    save_candidates,
    validate_candidate_records,
)


def test_generate_candidates_non_empty() -> None:
    candidates = generate_candidates(max_per_class=3)
    assert candidates


def test_generated_candidates_required_fields() -> None:
    candidates = generate_candidates(max_per_class=2)
    validate_candidate_records(candidates)
    for candidate in candidates:
        assert candidate["reaction_id"]
        assert ">>" in candidate["reaction_smiles"]
        assert candidate["context"]
        assert candidate["mechanism_type"]
        assert candidate["split"] in {"draft", "review"}
        assert isinstance(candidate["metadata"], dict)


def test_generated_candidates_include_required_mechanisms() -> None:
    candidates = generate_candidates(max_per_class=3)
    mechanisms = {candidate["mechanism_type"] for candidate in candidates}
    assert "sn2" in mechanisms
    assert "e2" in mechanisms
    assert "diels_alder" in mechanisms
    assert {"aldol", "cross_aldol"} & mechanisms
    assert "carbonyl_addition" in mechanisms
    assert "control" in mechanisms


def test_generated_candidate_ids_and_smiles_are_unique() -> None:
    candidates = generate_candidates(max_per_class=10)
    reaction_ids = [candidate["reaction_id"] for candidate in candidates]
    reaction_smiles = [candidate["reaction_smiles"] for candidate in candidates]
    assert len(reaction_ids) == len(set(reaction_ids))
    assert len(reaction_smiles) == len(set(reaction_smiles))


def test_generated_candidates_all_need_manual_review() -> None:
    candidates = generate_candidates(max_per_class=3)
    assert all(candidate["metadata"]["needs_manual_review"] is True for candidate in candidates)


def test_generated_candidates_split_is_draft_or_review() -> None:
    candidates = generate_candidates(max_per_class=3)
    assert {candidate["split"] for candidate in candidates} <= {"draft", "review"}


def test_generate_candidate_reactions_cli_creates_output(tmp_path: Path) -> None:
    output = tmp_path / "draft_inputs.auto_candidates.json"
    result = subprocess.run(
        [
            sys.executable,
            str(_SCRIPTS_DIR / "generate_candidate_reactions.py"),
            "--output",
            str(output),
            "--max-per-class",
            "2",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert isinstance(payload, list)
    assert payload


def test_auto_draft_and_filter_smoke(tmp_path: Path) -> None:
    candidates = generate_candidates(max_per_class=1)[:6]
    input_path = tmp_path / "draft_inputs.auto_candidates.json"
    draft_output = tmp_path / "reactions.draft.auto_candidates.json"
    review_output = tmp_path / "reactions.auto_review_queue.json"
    report_output = tmp_path / "auto_candidates_report.json"
    save_candidates(candidates, input_path)

    report = run_auto_draft_pipeline(
        input_path=input_path,
        draft_output=draft_output,
        review_output=review_output,
        report_output=report_output,
    )

    assert draft_output.exists()
    assert review_output.exists()
    assert report_output.exists()
    assert report["n_inputs"] == len(candidates)
    assert "review_queue" in report


def test_auto_draft_filter_applies_conservative_review_rules(tmp_path: Path) -> None:
    candidates = [
        candidate
        for candidate in generate_candidates(max_per_class=10)
        if candidate["reaction_id"]
        in {
            "auto_carbonyl_addition_acetaldehyde_cyanide",
            "auto_diels_alder_butadiene_acrylonitrile",
            "auto_ester_control_methyl_acetate_no_reaction",
        }
    ]
    input_path = tmp_path / "draft_inputs.json"
    draft_output = tmp_path / "draft.json"
    review_output = tmp_path / "review.json"
    report_output = tmp_path / "report.json"
    save_candidates(candidates, input_path)

    report = run_auto_draft_pipeline(
        input_path=input_path,
        draft_output=draft_output,
        review_output=review_output,
        report_output=report_output,
    )
    review = json.loads(review_output.read_text(encoding="utf-8"))["reactions"]

    by_id = {reaction["reaction_id"]: reaction for reaction in review}
    carbonyl_alpha_roles = [
        group["role"]
        for group in by_id["auto_carbonyl_addition_acetaldehyde_cyanide"]["group_roles"]
        if group["group_type"] == "alpha_carbon"
    ]
    diels_nitrile_roles = [
        group["role"]
        for group in by_id["auto_diels_alder_butadiene_acrylonitrile"]["group_roles"]
        if group["group_type"] == "nitrile"
    ]
    ester_control_roles = [
        group["role"]
        for group in by_id["auto_ester_control_methyl_acetate_no_reaction"]["group_roles"]
        if group["group_type"] in {"ester", "alpha_carbon"}
    ]

    assert carbonyl_alpha_roles == ["spectator"]
    assert diels_nitrile_roles == ["spectator"]
    assert set(ester_control_roles) == {"spectator"}
    assert report["review_queue"]["conservative_adjustments"]


def test_auto_scripts_do_not_reference_mlp_training() -> None:
    for script_name in ("generate_candidate_reactions.py", "auto_draft_and_filter.py"):
        text = (_SCRIPTS_DIR / script_name).read_text(encoding="utf-8")
        assert "train_mlp" not in text
        assert "mendel.mlp" not in text
