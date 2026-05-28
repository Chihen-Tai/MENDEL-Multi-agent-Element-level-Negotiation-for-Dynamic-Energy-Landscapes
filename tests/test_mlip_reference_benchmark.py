"""Tests for Phase 10 MLIP reference benchmark scaffold."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

from mendel.reference_data import (
    MLIPStructurePrediction,
    compute_energy_force_benchmark,
    load_reference_records_json,
)

_ROOT = Path(__file__).parent.parent
_CREATE_SCRIPT = _ROOT / "scripts" / "create_tiny_reference_example.py"
_BENCH_SCRIPT = _ROOT / "scripts" / "run_mlip_reference_benchmark.py"


def test_create_tiny_reference_example_creates_valid_json(tmp_path: Path) -> None:
    output = tmp_path / "tiny_reference.json"

    result = subprocess.run(
        [sys.executable, str(_CREATE_SCRIPT), "--output", str(output)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    records = load_reference_records_json(output)
    assert len(records) >= 2
    assert records[0].metadata["synthetic_test_data"] is True


@pytest.mark.skipif(
    importlib.util.find_spec("mace") is not None,
    reason="MACE is installed; missing-dep error path is unreachable",
)
def test_run_mlip_reference_benchmark_missing_dependencies_clear_error(tmp_path: Path) -> None:
    reference = tmp_path / "tiny_reference.json"
    subprocess.run(
        [sys.executable, str(_CREATE_SCRIPT), "--output", str(reference)],
        check=True,
        capture_output=True,
        text=True,
    )

    result = subprocess.run(
        [
            sys.executable,
            str(_BENCH_SCRIPT),
            "--reference",
            str(reference),
            "--predictions-output",
            str(tmp_path / "preds.json"),
            "--benchmark-output",
            str(tmp_path / "bench.json"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode in {0, 1}
    if result.returncode == 1:
        assert "pip install -e '.[mlip]'" in result.stderr


def test_benchmark_math_with_fake_predictions(tmp_path: Path) -> None:
    reference = tmp_path / "tiny_reference.json"
    subprocess.run(
        [sys.executable, str(_CREATE_SCRIPT), "--output", str(reference)],
        check=True,
        capture_output=True,
        text=True,
    )
    records = load_reference_records_json(reference)
    predictions = [
        MLIPStructurePrediction(
            structure_id=record.structure_id,
            backend_name="fake",
            model_name="fake",
            energy=record.reference_energy,
            energy_unit=record.reference_energy_unit,
            forces=record.reference_forces,
            force_unit=record.reference_force_unit,
            success=True,
            warnings=[],
            metadata={},
        )
        for record in records
    ]

    report = compute_energy_force_benchmark(records, predictions)

    assert report.energy_mae == 0.0
    assert report.force_rmse == 0.0


def test_reference_benchmark_reuses_calculator(monkeypatch, tmp_path: Path) -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location("run_mlip_reference_benchmark", _BENCH_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    reference = tmp_path / "tiny_reference.json"
    subprocess.run(
        [sys.executable, str(_CREATE_SCRIPT), "--output", str(reference)],
        check=True,
        capture_output=True,
        text=True,
    )
    calls = {"calculator": 0, "singlepoint": 0}

    class FakeAtoms:
        calc = None

    def fake_create(_config):
        calls["calculator"] += 1
        return object()

    def fake_singlepoint(atoms, config, calculator=None):
        calls["singlepoint"] += 1
        assert calculator is not None
        from mendel.mlip import MLIPResult

        return MLIPResult(
            0.0,
            "eV",
            [[0.0, 0.0, 0.0]],
            "eV/Angstrom",
            1,
            config.backend_name,
            config.model_name,
            "cpu",
            True,
            [],
            {"calculator_reused": True},
        )

    monkeypatch.setattr(module, "create_mlip_calculator", fake_create)
    monkeypatch.setattr(module, "xyz_to_ase_atoms", lambda _record: FakeAtoms())
    monkeypatch.setattr(module, "compute_mlip_singlepoint", fake_singlepoint)

    code = module.main([
        "--reference",
        str(reference),
        "--predictions-output",
        str(tmp_path / "predictions.json"),
        "--benchmark-output",
        str(tmp_path / "benchmark.json"),
    ])

    assert code == 0
    assert calls["calculator"] == 1
    assert calls["singlepoint"] == len(load_reference_records_json(reference))


def test_no_training_invoked() -> None:
    text = _BENCH_SCRIPT.read_text(encoding="utf-8").lower()
    for token in ("train_mlp", "fit(", "fine_tune", "neb", "irc", "md"):
        assert token not in text
