"""Phase 8 benchmark evaluator tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from mendel.benchmark import (
    BenchmarkReport,
    GroupBenchmarkRecord,
    ReactionBenchmarkRecord,
    build_confusion_matrix,
    compare_benchmark_reports,
    compute_accuracy_by_group_type,
    compute_accuracy_by_role,
    compute_reaction_center_metrics,
    evaluate_negotiated_mlp_predictor,
    evaluate_negotiated_rule_based,
    evaluate_rule_based_predictor,
    load_benchmark_report,
    save_benchmark_report,
)
from mendel.labels import load_labeled_reactions
from mendel.types import FunctionalGroupType, Role

_ROOT = Path(__file__).parent.parent
_MINIMAL = _ROOT / "data" / "reactions.minimal.json"
_SCRIPT = _ROOT / "scripts" / "benchmark.py"
_MLP_MINIMAL = _ROOT / "models" / "role_mlp_minimal.pt"


def _group_record(
    true_role: Role,
    predicted_role: Role,
    group_type: FunctionalGroupType = FunctionalGroupType.halide,
    reaction_id: str = "rxn",
    predictor_name: str = "test_predictor",
) -> GroupBenchmarkRecord:
    return GroupBenchmarkRecord(
        reaction_id=reaction_id,
        group_id=f"{reaction_id}_{group_type.value}_{true_role.value}",
        group_type=group_type,
        true_role=true_role,
        predicted_role=predicted_role,
        predicted_confidence=0.75,
        predictor_name=predictor_name,
        correct=true_role == predicted_role,
        split="train",
        mechanism_type="SN2",
        metadata={},
    )


def _reaction_record(
    predictor_name: str,
    role_accuracy: float,
) -> ReactionBenchmarkRecord:
    return ReactionBenchmarkRecord(
        reaction_id=f"{predictor_name}_rxn",
        reaction_smiles="CBr>>CBr",
        split="train",
        mechanism_type="SN2",
        predictor_name=predictor_name,
        n_labeled_groups=1,
        n_correct_roles=1 if role_accuracy == 1.0 else 0,
        role_accuracy=role_accuracy,
        mechanism_hint="sn2_or_e2_like",
        reaction_center_precision=None,
        reaction_center_recall=None,
        reaction_center_f1=None,
        warnings=[],
        metadata={},
    )


def _report(name: str, records: list[GroupBenchmarkRecord]) -> BenchmarkReport:
    return BenchmarkReport(
        predictor_name=name,
        n_reactions=1,
        n_group_labels=len(records),
        overall_role_accuracy=sum(1 for r in records if r.correct) / len(records),
        role_accuracy_by_role=compute_accuracy_by_role(records),
        role_accuracy_by_group_type=compute_accuracy_by_group_type(records),
        role_accuracy_by_mechanism={"SN2": sum(1 for r in records if r.correct) / len(records)},
        split_accuracy={"train": sum(1 for r in records if r.correct) / len(records)},
        confusion_matrix=build_confusion_matrix(records),
        reaction_center_precision=None,
        reaction_center_recall=None,
        reaction_center_f1=None,
        group_records=records,
        reaction_records=[_reaction_record(name, sum(1 for r in records if r.correct) / len(records))],
        metadata={},
    )


def test_confusion_matrix_includes_all_role_rows_and_columns() -> None:
    records = [
        _group_record(Role.leaving_group, Role.leaving_group),
        _group_record(Role.reactive_nucleophile, Role.spectator),
    ]

    matrix = build_confusion_matrix(records)

    role_values = {role.value for role in Role}
    assert set(matrix) == role_values
    for row in matrix.values():
        assert set(row) == role_values
    assert matrix["leaving_group"]["leaving_group"] == 1
    assert matrix["reactive_nucleophile"]["spectator"] == 1


def test_accuracy_by_role_uses_true_role_denominator() -> None:
    records = [
        _group_record(Role.leaving_group, Role.leaving_group),
        _group_record(Role.leaving_group, Role.spectator),
        _group_record(Role.spectator, Role.spectator),
    ]

    accuracy = compute_accuracy_by_role(records)

    assert accuracy["leaving_group"] == 0.5
    assert accuracy["spectator"] == 1.0


def test_accuracy_by_group_type_aggregates_group_types() -> None:
    records = [
        _group_record(Role.leaving_group, Role.leaving_group, FunctionalGroupType.halide),
        _group_record(Role.spectator, Role.leaving_group, FunctionalGroupType.halide),
        _group_record(Role.reactive_electrophile, Role.reactive_electrophile, FunctionalGroupType.carbonyl),
    ]

    accuracy = compute_accuracy_by_group_type(records)

    assert accuracy["halide"] == 0.5
    assert accuracy["carbonyl"] == 1.0


def test_reaction_center_metrics_overlap_case() -> None:
    metrics = compute_reaction_center_metrics([1, 2], [2, 3])

    assert metrics["precision"] == 0.5
    assert metrics["recall"] == 0.5
    assert metrics["f1"] == 0.5


def test_reaction_center_metrics_empty_cases_do_not_crash() -> None:
    both_empty = compute_reaction_center_metrics([], [])
    no_predictions = compute_reaction_center_metrics([], [1])
    no_truth = compute_reaction_center_metrics([1], [])

    assert both_empty == {"precision": None, "recall": None, "f1": None}
    assert no_predictions["precision"] == 0.0
    assert no_predictions["recall"] == 0.0
    assert no_predictions["f1"] == 0.0
    assert no_truth["precision"] == 0.0
    assert no_truth["recall"] is None
    assert no_truth["f1"] is None


def test_rule_based_benchmark_returns_report() -> None:
    reactions = load_labeled_reactions(_MINIMAL)

    report = evaluate_rule_based_predictor(reactions)

    assert isinstance(report, BenchmarkReport)
    assert report.predictor_name == "rule_based_local"
    assert report.n_group_labels > 0
    assert 0.0 <= report.overall_role_accuracy <= 1.0


def test_negotiated_benchmark_returns_mechanism_hints_when_possible() -> None:
    reactions = load_labeled_reactions(_MINIMAL)

    report = evaluate_negotiated_rule_based(reactions)

    assert isinstance(report, BenchmarkReport)
    assert report.predictor_name == "rule_based_negotiated"
    assert report.n_group_labels > 0
    assert any(record.mechanism_hint for record in report.reaction_records)


def test_mlp_negotiated_benchmark_accepts_fake_predictor_without_torch() -> None:
    class FakePrediction:
        def __init__(self, group_id: str, group_type: FunctionalGroupType) -> None:
            self.group_id = group_id
            self.group_type = group_type
            self.predicted_role = Role.spectator
            self.confidence = 0.50

    class FakePredictor:
        def predict_descriptors(self, descriptors):
            return [FakePrediction(d.group_id, d.group_type) for d in descriptors]

    reactions = load_labeled_reactions(_MINIMAL)

    report = evaluate_negotiated_mlp_predictor(reactions, FakePredictor())

    assert report.predictor_name == "mlp_negotiated"
    assert report.n_group_labels > 0
    assert any(record.mechanism_hint for record in report.reaction_records)


def test_save_and_load_benchmark_report(tmp_path: Path) -> None:
    report = _report("one", [_group_record(Role.leaving_group, Role.leaving_group)])
    path = tmp_path / "report.json"

    save_benchmark_report(report, path)
    loaded = load_benchmark_report(path)

    assert loaded["predictor_name"] == "one"
    assert loaded["n_group_labels"] == 1


def test_compare_benchmark_reports_returns_tables_and_best_predictor() -> None:
    report_a = _report("a", [_group_record(Role.leaving_group, Role.leaving_group)])
    report_b = _report("b", [_group_record(Role.leaving_group, Role.spectator)])

    comparison = compare_benchmark_reports([report_a, report_b])

    assert comparison["predictor_names"] == ["a", "b"]
    assert comparison["overall_role_accuracy"] == {"a": 1.0, "b": 0.0}
    assert comparison["best_predictor_by_overall_accuracy"] == "a"


def test_cli_smoke_creates_rule_and_negotiated_reports(tmp_path: Path) -> None:
    comparison = tmp_path / "comparison.json"

    result = subprocess.run(
        [
            sys.executable,
            str(_SCRIPT),
            "--data",
            str(_MINIMAL),
            "--rule-based",
            "--negotiated",
            "--output-dir",
            str(tmp_path),
            "--comparison-output",
            str(comparison),
        ],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    assert (tmp_path / "rule_based_local.json").exists()
    assert (tmp_path / "rule_based_negotiated.json").exists()
    assert comparison.exists()
    payload = json.loads(comparison.read_text(encoding="utf-8"))
    assert payload["predictor_names"] == ["rule_based_local", "rule_based_negotiated"]


def test_optional_mlp_checkpoint_benchmark() -> None:
    pytest.importorskip("torch")
    if not _MLP_MINIMAL.exists():
        pytest.skip("models/role_mlp_minimal.pt is not available")

    from mendel.benchmark import evaluate_mlp_checkpoint

    reactions = load_labeled_reactions(_MINIMAL)
    report = evaluate_mlp_checkpoint(reactions, _MLP_MINIMAL, device="cpu")

    assert report.predictor_name == "mlp_local"
    assert report.n_group_labels > 0
