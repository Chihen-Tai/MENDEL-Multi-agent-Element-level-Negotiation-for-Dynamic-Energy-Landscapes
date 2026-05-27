"""CLI script: normalize and inspect MENDELV labeled datasets."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from mendel.dataset_quality import (
    build_dataset_quality_report,
    normalize_labeled_dataset,
    save_dataset_quality_report,
    save_labeled_reactions_json,
    suggest_dataset_improvements,
)
from mendel.labels import load_labeled_reactions


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize MENDELV labeled reaction datasets and report quality issues.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--input", type=Path, default=_ROOT / "data" / "reactions.json")
    parser.add_argument(
        "--output",
        type=Path,
        default=_ROOT / "data" / "reactions.normalized.json",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=_ROOT / "reports" / "dataset_quality_report.json",
    )
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--no-normalize", action="store_true")
    parser.add_argument("--fail-on-warning", action="store_true")
    parser.add_argument("--fail-on-error", action="store_true")
    return parser


def _severity_counts(report) -> dict[str, int]:
    raw = report.metadata.get("n_issues_by_severity", {})
    return dict(raw) if isinstance(raw, dict) else {}


def _print_report(pre_report, post_report, suggestions: list[str]) -> None:
    print(f"n_reactions:    {post_report.n_reactions}")
    print(f"n_group_labels: {post_report.n_group_labels}")
    print(f"role_distribution: {post_report.role_distribution}")
    print(f"mechanism_distribution before: {pre_report.mechanism_distribution}")
    print(f"mechanism_distribution after:  {post_report.mechanism_distribution}")
    print(f"split_distribution: {post_report.split_distribution}")
    print(f"issue counts by severity: {_severity_counts(post_report)}")
    print("suggestions:")
    for suggestion in suggestions:
        print(f"  - {suggestion}")


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    reactions = load_labeled_reactions(args.input)
    pre_report = build_dataset_quality_report(reactions)
    normalized = reactions if args.no_normalize else normalize_labeled_dataset(reactions)
    post_report = build_dataset_quality_report(normalized)

    save_labeled_reactions_json(normalized, args.output)
    save_dataset_quality_report(post_report, args.report)

    if args.overwrite:
        backup = Path(str(args.input) + ".backup_before_phase8_5")
        shutil.copy2(args.input, backup)
        shutil.copy2(args.output, args.input)
        print(f"Backed up input to: {backup}")
        print(f"Overwrote input with normalized dataset: {args.input}")

    suggestions = suggest_dataset_improvements(post_report)
    _print_report(pre_report, post_report, suggestions)
    print(f"normalized dataset: {args.output}")
    print(f"quality report:     {args.report}")

    severities = _severity_counts(post_report)
    if args.fail_on_error and severities.get("error", 0) > 0:
        return 1
    if args.fail_on_warning and (
        severities.get("warning", 0) > 0 or severities.get("error", 0) > 0
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
