"""Run draft labeling and conservative filtering for auto candidates.

This pipeline turns DraftReactionInput-style candidates into reviewable draft
labels. It does not create ground truth and does not modify data/reactions.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from mendel.curation import (
    DraftLabelConfig,
    DraftReactionInput,
    draft_labeled_reactions,
    load_draft_inputs,
    summarize_draft_labels,
)
from mendel.dataset_quality import (
    build_dataset_quality_report,
    save_labeled_reactions_json,
    suggest_dataset_improvements,
)
from mendel.labels import LabeledReaction
from mendel.types import Role

DEFAULT_INPUT = Path("data/draft_inputs.auto_candidates.json")
DEFAULT_DRAFT_OUTPUT = Path("data/reactions.draft.auto_candidates.json")
DEFAULT_REVIEW_OUTPUT = Path("data/reactions.auto_review_queue.json")
DEFAULT_REPORT = Path("reports/auto_candidates_report.json")


def _append_note(existing: str | None, note: str) -> str:
    if existing:
        return f"{existing}; {note}"
    return note


def _apply_conservative_review_rules(
    reactions: list[LabeledReaction],
) -> dict[str, int]:
    """Downgrade known over-reactive draft assignments before review export.

    These corrections remain draft labels. They encode manual-review guidance
    for cases where the current flat taxonomy/rules over-assign reactivity.
    """
    counts: Counter[str] = Counter()

    for reaction in reactions:
        reaction_adjustments = 0
        for group_role in reaction.group_roles:
            group_type = group_role.group_type.value

            if (
                reaction.mechanism_type == "carbonyl_addition"
                and group_type == "alpha_carbon"
                and group_role.role == Role.reactive_nucleophile
            ):
                group_role.role = Role.spectator
                group_role.notes = _append_note(
                    group_role.notes,
                    "auto_review_rule: hydride/cyanide carbonyl addition; "
                    "alpha_carbon downgraded to spectator pending manual review",
                )
                counts["carbonyl_addition_alpha_carbon_to_spectator"] += 1
                reaction_adjustments += 1

            if (
                reaction.mechanism_type == "diels_alder"
                and group_type in {"nitrile", "ester", "carbonyl"}
                and group_role.role == Role.reactive_electrophile
            ):
                group_role.role = Role.spectator
                group_role.notes = _append_note(
                    group_role.notes,
                    "auto_review_rule: Diels-Alder electrophilic substituent/EWG; "
                    "true dienophile partner should be the alkene",
                )
                counts["diels_alder_ewg_substituent_to_spectator"] += 1
                reaction_adjustments += 1

            if (
                reaction.mechanism_type in {"ester_control", "nitrile_control"}
                and group_type in {"ester", "nitrile", "alpha_carbon", "carbonyl"}
                and group_role.role != Role.spectator
            ):
                group_role.role = Role.spectator
                group_role.notes = _append_note(
                    group_role.notes,
                    "auto_review_rule: control example; reactive draft label "
                    "downgraded to spectator pending manual review",
                )
                counts["control_reactive_group_to_spectator"] += 1
                reaction_adjustments += 1

        if reaction_adjustments:
            reaction.metadata["auto_review_adjusted"] = True
            reaction.metadata["auto_review_adjustment_count"] = reaction_adjustments

    return dict(sorted(counts.items()))


def _dedupe_inputs(
    inputs: list[DraftReactionInput],
) -> tuple[list[DraftReactionInput], list[dict[str, object]]]:
    seen_ids: set[str] = set()
    seen_smiles: set[str] = set()
    deduped: list[DraftReactionInput] = []
    skipped: list[dict[str, object]] = []

    for inp in inputs:
        if inp.reaction_id in seen_ids:
            skipped.append({
                "reaction_id": inp.reaction_id,
                "reason": "duplicate_reaction_id",
            })
            continue
        if inp.reaction_smiles in seen_smiles:
            skipped.append({
                "reaction_id": inp.reaction_id,
                "reason": "duplicate_reaction_smiles",
            })
            continue
        deduped.append(inp)
        seen_ids.add(inp.reaction_id)
        seen_smiles.add(inp.reaction_smiles)

    return deduped, skipped


def _has_malformed_draft_role(reaction: LabeledReaction) -> bool:
    for role in reaction.group_roles:
        if role.confidence == "draft" and (
            not role.group_id or role.group_type is None or role.role is None
        ):
            return True
    return False


def _review_filter(
    reactions: list[LabeledReaction],
) -> tuple[list[LabeledReaction], list[dict[str, object]], dict[str, int]]:
    review_queue: list[LabeledReaction] = []
    skipped: list[dict[str, object]] = []
    marked = Counter()

    for reaction in reactions:
        if not reaction.group_roles:
            skipped.append({
                "reaction_id": reaction.reaction_id,
                "reason": "no_group_roles",
            })
            continue
        if _has_malformed_draft_role(reaction):
            skipped.append({
                "reaction_id": reaction.reaction_id,
                "reason": "malformed_draft_group_role",
            })
            continue

        if reaction.metadata.get("warning_count", 0):
            marked["warnings_from_negotiation"] += 1
        if reaction.metadata.get("product_simplified"):
            marked["product_simplified"] += 1
        if reaction.metadata.get("unsupported_reagent_note"):
            marked["unsupported_reagent_or_group"] += 1
        if not reaction.reaction_center_atoms:
            marked["empty_reaction_center_atoms"] += 1

        review_queue.append(reaction)

    return review_queue, skipped, dict(sorted(marked.items()))


def _skip_reason_counts(skips: list[dict[str, object]]) -> dict[str, int]:
    counts = Counter(str(skip.get("reason", "draft_generation_failed")) for skip in skips)
    for skip in skips:
        if "error" in skip and "reason" not in skip:
            counts["draft_generation_failed"] += 1
    return dict(sorted(counts.items()))


def run_auto_draft_pipeline(
    input_path: str | Path = DEFAULT_INPUT,
    draft_output: str | Path = DEFAULT_DRAFT_OUTPUT,
    review_output: str | Path = DEFAULT_REVIEW_OUTPUT,
    report_output: str | Path = DEFAULT_REPORT,
) -> dict[str, object]:
    """Run candidate draft labeling, quality checks, and review filtering."""
    inputs = load_draft_inputs(input_path)
    unique_inputs, duplicate_skips = _dedupe_inputs(inputs)

    config = DraftLabelConfig(
        include_spectators=True,
        include_low_confidence=True,
        source_tag="auto_candidate_template_draft",
    )
    draft_reactions, draft_report = draft_labeled_reactions(unique_inputs, config)
    adjustment_counts = _apply_conservative_review_rules(draft_reactions)
    save_labeled_reactions_json(draft_reactions, draft_output)

    quality_report = build_dataset_quality_report(draft_reactions)
    review_queue, review_skips, marked_counts = _review_filter(draft_reactions)
    save_labeled_reactions_json(review_queue, review_output)

    draft_skips: list[dict[str, object]] = []
    for skip in draft_report.skipped:
        item = dict(skip)
        item.setdefault("reason", "draft_generation_failed")
        draft_skips.append(item)

    all_skips = duplicate_skips + draft_skips + review_skips
    summary = summarize_draft_labels(draft_reactions)
    report: dict[str, object] = {
        "n_inputs": len(inputs),
        "n_unique_inputs": len(unique_inputs),
        "n_draft_reactions": len(draft_reactions),
        "n_review_queue": len(review_queue),
        "draft_label_report": draft_report.to_dict(),
        "draft_summary": summary,
        "quality_report": quality_report.to_dict(),
        "quality_suggestions": suggest_dataset_improvements(quality_report),
        "review_queue": {
            "n_reactions": len(review_queue),
            "filter": "successful_nonempty_draft_labels",
            "marked_not_removed": marked_counts,
            "conservative_adjustments": adjustment_counts,
        },
        "skipped": all_skips,
        "skip_reasons": _skip_reason_counts(all_skips),
        "outputs": {
            "draft_output": str(draft_output),
            "review_output": str(review_output),
            "report": str(report_output),
        },
        "metadata": {
            "source": "MENDELV template starter set",
            "labels_are_ground_truth": False,
            "needs_manual_review": True,
        },
    }

    report_path = Path(report_output)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate draft labels and review queue for auto candidates."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--draft-output", type=Path, default=DEFAULT_DRAFT_OUTPUT)
    parser.add_argument("--review-output", type=Path, default=DEFAULT_REVIEW_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        report = run_auto_draft_pipeline(
            input_path=args.input,
            draft_output=args.draft_output,
            review_output=args.review_output,
            report_output=args.report,
        )
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Loaded inputs: {report['n_inputs']}")
    print(f"Draft labeled reactions: {report['n_draft_reactions']}")
    print(f"Review queue reactions: {report['n_review_queue']}")
    print(f"Skipped: {len(report['skipped'])} {report['skip_reasons']}")
    print(f"Draft output: {args.draft_output}")
    print(f"Review output: {args.review_output}")
    print(f"Report: {args.report}")
    print("Auto-generated labels are draft only and require manual review.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
