"""CLI script: run MENDELV Phase 8 benchmark evaluators.

This script evaluates existing predictors only. It does not train.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from mendel.benchmark import (
    BenchmarkReport,
    compare_benchmark_reports,
    evaluate_mlp_checkpoint,
    evaluate_negotiated_mlp_checkpoint,
    evaluate_negotiated_rule_based,
    evaluate_rule_based_predictor,
    save_benchmark_comparison,
    save_benchmark_report,
)
from mendel.labels import load_labeled_reactions


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run MENDELV Phase 8 role-predictor benchmarks.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--data", type=Path, default=_ROOT / "data" / "reactions.json")
    parser.add_argument("--rule-based", action="store_true")
    parser.add_argument("--negotiated", action="store_true")
    parser.add_argument("--mlp-checkpoint", type=Path)
    parser.add_argument(
        "--device",
        choices=("cpu", "cuda", "mps", "auto"),
        default="cpu",
        help="Device for MLP checkpoint evaluation only.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=_ROOT / "reports" / "benchmark",
    )
    parser.add_argument(
        "--comparison-output",
        type=Path,
        default=None,
        help="Comparison JSON path. Defaults to <output-dir>/comparison.json.",
    )
    return parser


def _resolve_device(device: str) -> str:
    if device != "auto":
        return device
    try:
        import torch
    except ImportError:
        return "cpu"
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def _print_report(report: BenchmarkReport) -> None:
    print(f"\n{report.predictor_name}")
    print(f"  n_reactions:     {report.n_reactions}")
    print(f"  n_group_labels:  {report.n_group_labels}")
    print(f"  overall accuracy:{report.overall_role_accuracy: .4f}")
    print("  by mechanism:")
    for mechanism, accuracy in sorted(report.role_accuracy_by_mechanism.items()):
        print(f"    {mechanism}: {accuracy:.4f}")
    print("  by role:")
    for role, accuracy in sorted(report.role_accuracy_by_role.items()):
        print(f"    {role}: {accuracy:.4f}")
    if (
        report.reaction_center_precision is not None
        or report.reaction_center_recall is not None
        or report.reaction_center_f1 is not None
    ):
        print("  reaction center:")
        print(f"    precision: {report.reaction_center_precision}")
        print(f"    recall:    {report.reaction_center_recall}")
        print(f"    f1:        {report.reaction_center_f1}")


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    run_rule_based = args.rule_based
    run_negotiated = args.negotiated
    if not run_rule_based and not run_negotiated and args.mlp_checkpoint is None:
        run_rule_based = True
        run_negotiated = True

    reactions = load_labeled_reactions(args.data)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    comparison_output = args.comparison_output or (args.output_dir / "comparison.json")

    reports: list[BenchmarkReport] = []
    if run_rule_based:
        report = evaluate_rule_based_predictor(reactions)
        save_benchmark_report(report, args.output_dir / "rule_based_local.json")
        reports.append(report)

    if run_negotiated:
        report = evaluate_negotiated_rule_based(reactions)
        save_benchmark_report(report, args.output_dir / "rule_based_negotiated.json")
        reports.append(report)

    if args.mlp_checkpoint is not None:
        device = _resolve_device(args.device)
        report = evaluate_mlp_checkpoint(reactions, args.mlp_checkpoint, device=device)
        report.metadata["device"] = device
        report.metadata["checkpoint_path"] = str(args.mlp_checkpoint)
        save_benchmark_report(report, args.output_dir / "mlp_local.json")
        reports.append(report)

        negotiated_report = evaluate_negotiated_mlp_checkpoint(
            reactions, args.mlp_checkpoint, device=device
        )
        negotiated_report.metadata["device"] = device
        negotiated_report.metadata["checkpoint_path"] = str(args.mlp_checkpoint)
        save_benchmark_report(negotiated_report, args.output_dir / "mlp_negotiated.json")
        reports.append(negotiated_report)

    if not reports:
        parser.error("No benchmark mode selected.")

    comparison = compare_benchmark_reports(reports)
    save_benchmark_comparison(comparison, comparison_output)

    print(f"Loaded {len(reactions)} labeled reaction(s) from {args.data}")
    for report in reports:
        _print_report(report)
    print(f"\nReports saved to:    {args.output_dir}")
    print(f"Comparison saved to: {comparison_output}")
    print(
        "Best overall accuracy: "
        f"{comparison['best_predictor_by_overall_accuracy']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
