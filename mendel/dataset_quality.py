"""Phase 8.5: Dataset normalization and diagnostics for MENDELV.

These utilities inspect and normalize labeled reaction data before MLP training
or benchmark evaluation. They do not train models and do not import PyTorch.
Functional group = agent remains the data unit.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from mendel.labels import LabeledGroupRole, LabeledReaction
from mendel.types import FunctionalGroupType, Role

Scalar = str | int | float | bool

MECHANISM_ALIASES: dict[str, str] = {
    "SN2": "sn2",
    "sn2": "sn2",
    "E2": "e2",
    "e2": "e2",
    "Diels-Alder": "diels_alder",
    "diels_alder": "diels_alder",
    "Aldol": "aldol",
    "aldol": "aldol",
    "Radical bromination": "radical_bromination",
    "radical_bromination": "radical_bromination",
    "Benzylic radical bromination": "benzylic_radical_bromination",
    "benzylic_radical_bromination": "benzylic_radical_bromination",
    "cross_aldol": "cross_aldol",
    "carbonyl_addition": "carbonyl_addition",
    "control": "control",
    "control_or_acyl_substitution_precursor": "control",
    "control_or_nitrile_electrophile": "control",
    "nitroalkane_deprotonation": "nitroalkane_deprotonation",
}

CANONICAL_MECHANISMS: tuple[str, ...] = tuple(sorted(set(MECHANISM_ALIASES.values())))
_VALID_SPLITS = {"train", "val", "test"}


@dataclass
class DatasetQualityIssue:
    """One dataset quality issue for a labeled reaction."""

    reaction_id: str
    code: str
    message: str
    severity: str
    metadata: dict[str, Scalar] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "reaction_id": self.reaction_id,
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "metadata": dict(self.metadata),
        }


@dataclass
class DatasetQualityReport:
    """Aggregate labeled-dataset quality report."""

    n_reactions: int
    n_group_labels: int
    role_distribution: dict[str, int]
    group_type_distribution: dict[str, int]
    mechanism_distribution: dict[str, int]
    split_distribution: dict[str, int]
    issues: list[DatasetQualityIssue]
    metadata: dict[str, Scalar] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "n_reactions": self.n_reactions,
            "n_group_labels": self.n_group_labels,
            "role_distribution": dict(self.role_distribution),
            "group_type_distribution": dict(self.group_type_distribution),
            "mechanism_distribution": dict(self.mechanism_distribution),
            "split_distribution": dict(self.split_distribution),
            "issues": [issue.to_dict() for issue in self.issues],
            "metadata": dict(self.metadata),
        }


def canonicalize_mechanism_type(mechanism_type: str) -> str:
    """Return a canonical mechanism label without failing on unknown labels."""
    if mechanism_type in MECHANISM_ALIASES:
        return MECHANISM_ALIASES[mechanism_type]
    normalized = mechanism_type.strip().lower()
    normalized = re.sub(r"[\s\-]+", "_", normalized)
    normalized = re.sub(r"__+", "_", normalized)
    return normalized.strip("_")


def normalize_labeled_reaction(
    reaction: LabeledReaction,
    canonicalize_mechanism: bool = True,
    normalize_split: bool = True,
) -> LabeledReaction:
    """Return a normalized copy of a LabeledReaction without mutating input."""
    mechanism = reaction.mechanism_type
    split = reaction.split
    metadata: dict[str, Any] = dict(reaction.metadata)
    changed = False

    if canonicalize_mechanism:
        canonical = canonicalize_mechanism_type(mechanism)
        if canonical != mechanism:
            metadata["original_mechanism_type"] = mechanism
            mechanism = canonical
            changed = True

    if normalize_split and split == "draft" and metadata.get("needs_manual_review") is False:
        split = "train"
        changed = True

    if changed:
        metadata["normalized_by"] = "MENDELV Phase 8.5"

    return LabeledReaction(
        reaction_id=reaction.reaction_id,
        reaction_smiles=reaction.reaction_smiles,
        context=reaction.context,
        mechanism_type=mechanism,
        split=split,
        group_roles=[
            LabeledGroupRole(
                group_id=role.group_id,
                molecule_index=role.molecule_index,
                group_type=role.group_type,
                atom_indices=list(role.atom_indices),
                role=role.role,
                confidence=role.confidence,
                notes=role.notes,
            )
            for role in reaction.group_roles
        ],
        reaction_center_atoms=list(reaction.reaction_center_atoms),
        metadata=metadata,
    )


def normalize_labeled_dataset(
    reactions: list[LabeledReaction],
) -> list[LabeledReaction]:
    """Normalize every reaction while preserving deterministic ordering."""
    return [normalize_labeled_reaction(reaction) for reaction in reactions]


def _issue(
    reaction: LabeledReaction,
    code: str,
    message: str,
    severity: str,
    metadata: dict[str, Scalar] | None = None,
) -> DatasetQualityIssue:
    return DatasetQualityIssue(
        reaction_id=reaction.reaction_id,
        code=code,
        message=message,
        severity=severity,
        metadata=metadata or {},
    )


def check_labeled_reaction_quality(
    reaction: LabeledReaction,
) -> list[DatasetQualityIssue]:
    """Return deterministic quality issues for one labeled reaction."""
    issues: list[DatasetQualityIssue] = []

    if not reaction.group_roles:
        issues.append(_issue(
            reaction,
            "no_group_roles",
            "Reaction has no labeled functional-group roles.",
            "error",
        ))

    if not reaction.reaction_center_atoms:
        issues.append(_issue(
            reaction,
            "empty_reaction_center_atoms",
            "Reaction has no reaction-center atom labels.",
            "warning",
        ))

    if reaction.metadata.get("needs_manual_review") is True:
        issues.append(_issue(
            reaction,
            "needs_manual_review",
            "Reaction is still marked as needing manual review.",
            "error",
        ))

    if reaction.split not in _VALID_SPLITS:
        issues.append(_issue(
            reaction,
            "invalid_split",
            f"Split {reaction.split!r} is not train/val/test.",
            "error" if reaction.split != "draft" else "warning",
            {"split": reaction.split},
        ))

    canonical = canonicalize_mechanism_type(reaction.mechanism_type)
    if reaction.mechanism_type != canonical or canonical not in CANONICAL_MECHANISMS:
        severity = "warning" if canonical in CANONICAL_MECHANISMS else "info"
        issues.append(_issue(
            reaction,
            "noncanonical_mechanism_type",
            f"Mechanism {reaction.mechanism_type!r} normalizes to {canonical!r}.",
            severity,
            {
                "mechanism_type": reaction.mechanism_type,
                "canonical_mechanism_type": canonical,
            },
        ))

    seen: set[str] = set()
    roles = {role.role for role in reaction.group_roles}
    group_types = {role.group_type for role in reaction.group_roles}
    for role in reaction.group_roles:
        if role.group_id in seen:
            issues.append(_issue(
                reaction,
                "duplicate_group_id",
                f"Duplicate group_id {role.group_id!r}.",
                "error",
                {"group_id": role.group_id},
            ))
        seen.add(role.group_id)

        if role.confidence == "draft":
            issues.append(_issue(
                reaction,
                "draft_label",
                f"Group {role.group_id!r} still has draft confidence.",
                "error",
                {"group_id": role.group_id},
            ))

        if not role.notes:
            issues.append(_issue(
                reaction,
                "missing_notes",
                f"Group {role.group_id!r} has no label notes.",
                "info",
                {"group_id": role.group_id},
            ))

        if not isinstance(role.role, Role):
            issues.append(_issue(
                reaction,
                "unknown_role",
                f"Group {role.group_id!r} has an invalid role.",
                "error",
            ))
        if not isinstance(role.group_type, FunctionalGroupType):
            issues.append(_issue(
                reaction,
                "unknown_group_type",
                f"Group {role.group_id!r} has an invalid group type.",
                "error",
            ))

        if role.role == Role.spectator:
            issues.append(_issue(
                reaction,
                "spectator_label_present",
                "Spectator label included; confirm benchmark intentionally includes inactive groups.",
                "info",
                {"group_id": role.group_id},
            ))

    reactive_roles = {
        Role.reactive_nucleophile,
        Role.reactive_electrophile,
        Role.leaving_group,
        Role.reactive_radical,
    }
    if reaction.context.value == "ionic" and not (roles & reactive_roles):
        issues.append(_issue(
            reaction,
            "ionic_without_reactive_label",
            "Ionic reaction has no nucleophile/electrophile/leaving-group/reactive label.",
            "warning",
        ))

    if reaction.context.value == "radical" and Role.reactive_radical not in roles:
        note_text = " ".join(str(v).lower() for v in reaction.metadata.values())
        if "unsupported" not in note_text:
            issues.append(_issue(
                reaction,
                "radical_without_radical_label",
                "Radical reaction has no reactive_radical label.",
                "warning",
            ))

    if reaction.context.value == "pericyclic":
        pi_like = {
            FunctionalGroupType.alkene,
            FunctionalGroupType.alkyne,
            FunctionalGroupType.aromatic,
        }
        n_pi_like = sum(1 for gt in group_types if gt in pi_like)
        if n_pi_like < 2:
            issues.append(_issue(
                reaction,
                "pericyclic_few_pi_labels",
                "Pericyclic reaction has fewer than two alkene-like labels.",
                "warning",
                {"n_pi_like_group_types": n_pi_like},
            ))

    return issues


def build_dataset_quality_report(
    reactions: list[LabeledReaction],
) -> DatasetQualityReport:
    """Build aggregate counts and quality diagnostics."""
    role_counts: dict[str, int] = {}
    group_type_counts: dict[str, int] = {}
    mechanism_counts: dict[str, int] = {}
    split_counts: dict[str, int] = {}
    issues: list[DatasetQualityIssue] = []
    n_labels = 0

    for reaction in reactions:
        mechanism = canonicalize_mechanism_type(reaction.mechanism_type)
        mechanism_counts[mechanism] = mechanism_counts.get(mechanism, 0) + 1
        split_counts[reaction.split] = split_counts.get(reaction.split, 0) + 1
        issues.extend(check_labeled_reaction_quality(reaction))
        for role in reaction.group_roles:
            role_counts[role.role.value] = role_counts.get(role.role.value, 0) + 1
            group_type_counts[role.group_type.value] = (
                group_type_counts.get(role.group_type.value, 0) + 1
            )
            n_labels += 1

    severity_counts: dict[str, int] = {}
    for issue in issues:
        severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1

    return DatasetQualityReport(
        n_reactions=len(reactions),
        n_group_labels=n_labels,
        role_distribution=dict(sorted(role_counts.items())),
        group_type_distribution=dict(sorted(group_type_counts.items())),
        mechanism_distribution=dict(sorted(mechanism_counts.items())),
        split_distribution=dict(sorted(split_counts.items())),
        issues=issues,
        metadata={
            "n_issues_by_severity": severity_counts,
            "n_canonical_mechanisms": len(CANONICAL_MECHANISMS),
            "recommended_min_labels_per_role": 20,
        },
    )


def save_dataset_quality_report(
    report: DatasetQualityReport,
    path: str | Path,
) -> None:
    """Save a dataset quality report as readable JSON."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")


def save_labeled_reactions_json(
    reactions: list[LabeledReaction],
    path: str | Path,
) -> None:
    """Save labeled reactions using the standard top-level reactions wrapper."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"reactions": [reaction.to_dict() for reaction in reactions]}
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def suggest_dataset_improvements(
    report: DatasetQualityReport,
) -> list[str]:
    """Return human-readable dataset improvement suggestions."""
    suggestions: list[str] = []
    for role in Role:
        count = report.role_distribution.get(role.value, 0)
        if count < 10:
            suggestions.append(
                f"Add more {role.value} labels; current count is {count}, target at least 10."
            )
    for mechanism, count in report.mechanism_distribution.items():
        if count < 3:
            suggestions.append(
                f"Add more {mechanism} reactions; current count is {count}, target at least 3."
            )
    if report.role_distribution.get(Role.spectator.value, 0) < 10:
        suggestions.append("Add more curated spectator examples to calibrate inactive groups.")
    if report.role_distribution.get(Role.reactive_nucleophile.value, 0) < 10:
        suggestions.append("Add more nucleophile examples, including free anions when representable.")
    if report.role_distribution.get(Role.reactive_electrophile.value, 0) < 10:
        suggestions.append("Add more electrophile examples across carbonyl and pi systems.")

    codes = [issue.code for issue in report.issues]
    if "draft_label" in codes or "needs_manual_review" in codes:
        suggestions.append("Resolve draft labels and manual-review flags before training MLPs.")
    if "noncanonical_mechanism_type" in codes:
        suggestions.append("Normalize mechanism labels before comparing per-mechanism metrics.")
    if "no_group_roles" in codes:
        suggestions.append("Either curate group labels for empty-label reactions or exclude them.")
    if not suggestions:
        suggestions.append("Dataset quality checks found no immediate low-count recommendations.")
    return suggestions
