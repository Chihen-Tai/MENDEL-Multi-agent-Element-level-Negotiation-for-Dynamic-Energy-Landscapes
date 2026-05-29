"""Compare baseline ANI-2x vs MENDEL-reactive-weighted fine-tuned ANI-2x.

Outputs a per-group force RMSE table and a bar chart showing before/after.

Usage:
  python scripts/benchmark_finetuned_ani2x.py \\
    --reference data/reference/rmd17_ethanol_sample_converted.reference.json \\
    --checkpoint models/ani2x_reactive_finetuned.pt \\
    --output reports/benchmark_finetuned_ani2x.json \\
    --figure reports/figures/finetuned_vs_baseline_ani2x.png \\
    --device cpu
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from mendel.weighted_finetune import (
    _eval_force_rmse,
    load_finetuned_model,
    load_records,
    per_group_rmse,
    split_records,
)


def _baseline_ani2x(device: str) -> object:
    try:
        import torchani
    except ImportError as exc:
        raise ImportError("pip install -e '.[ani2x]'") from exc
    return torchani.models.ANI2x(periodic_table_index=True).to(device)


def main() -> None:
    parser = argparse.ArgumentParser(description="Baseline vs fine-tuned ANI-2x benchmark")
    parser.add_argument(
        "--reference",
        default="data/reference/rmd17_ethanol_sample_converted.reference.json",
    )
    parser.add_argument("--checkpoint", default="models/ani2x_reactive_finetuned.pt")
    parser.add_argument("--output", default="reports/benchmark_finetuned_ani2x.json")
    parser.add_argument("--figure", default="reports/figures/finetuned_vs_baseline_ani2x.png")
    parser.add_argument("--test-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    import torch
    device = torch.device(args.device)

    records = load_records(ROOT / args.reference)
    _, test = split_records(records, test_fraction=args.test_fraction, seed=args.seed)
    print(f"test set: {len(test)} conformers")

    print("loading baseline ANI-2x ...")
    baseline = _baseline_ani2x(args.device)

    print("loading fine-tuned ANI-2x ...")
    finetuned = load_finetuned_model(ROOT / args.checkpoint, device=args.device)

    print("computing per-group RMSE ...")
    baseline_group = per_group_rmse(baseline, test, device)
    finetuned_group = per_group_rmse(finetuned, test, device)
    baseline_global = _eval_force_rmse(baseline, test, device)
    finetuned_global = _eval_force_rmse(finetuned, test, device)

    print()
    print(f"{'Group':<28}  {'Baseline':>10}  {'Fine-tuned':>10}  {'Δ':>8}")
    print("-" * 62)
    for group in baseline_group:
        b = baseline_group[group]
        f = finetuned_group[group]
        marker = " ←" if "reactive" in group else ""
        print(f"  {group:<26}  {b:10.4f}  {f:10.4f}  {f - b:+8.4f}{marker}")
    print("-" * 62)
    print(f"  {'global':<26}  {baseline_global:10.4f}  {finetuned_global:10.4f}  {finetuned_global - baseline_global:+8.4f}")

    report = {
        "baseline_global_force_rmse": baseline_global,
        "finetuned_global_force_rmse": finetuned_global,
        "per_group": {
            g: {"baseline": baseline_group[g], "finetuned": finetuned_group[g]}
            for g in baseline_group
        },
        "checkpoint": str(ROOT / args.checkpoint),
        "n_test": len(test),
    }
    out_path = ROOT / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nsaved: {out_path}")

    _make_figure(
        baseline_group, finetuned_group, baseline_global, finetuned_global,
        ROOT / args.figure,
    )


def _make_figure(
    baseline: dict[str, float],
    finetuned: dict[str, float],
    baseline_global: float,
    finetuned_global: float,
    path: Path,
) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("matplotlib not installed — skipping figure")
        return

    labels = list(baseline.keys())
    display = [g.replace("_", "\n") for g in labels]
    b_vals = [baseline[g] for g in labels]
    f_vals = [finetuned[g] for g in labels]

    C_BASE = "#DD8452"
    C_FINE = "#2ca02c"
    W = 0.35
    x = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(11, 5))
    fig.suptitle(
        "ANI-2x  Baseline vs MENDEL Reactive-Weighted Fine-tuned\n"
        "rMD17 ethanol · test set · revPBE-D3 reference",
        fontweight="bold", fontsize=11,
    )

    bb = ax.bar(x - W / 2, b_vals, W, color=C_BASE, alpha=0.85, label="ANI-2x baseline")
    bf = ax.bar(x + W / 2, f_vals, W, color=C_FINE, alpha=0.85, label="ANI-2x fine-tuned (MENDEL ×3)")
    for bar in list(bb) + list(bf):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f"{bar.get_height():.3f}", ha="center", va="bottom", fontsize=8)

    ax.axhline(baseline_global, color=C_BASE, lw=1.2, ls="--", alpha=0.5,
               label=f"baseline global ({baseline_global:.3f})")
    ax.axhline(finetuned_global, color=C_FINE, lw=1.2, ls="--", alpha=0.5,
               label=f"fine-tuned global ({finetuned_global:.3f})")

    r_idx = next(i for i, lb in enumerate(labels) if "reactive" in lb)
    top = max(b_vals[r_idx], f_vals[r_idx])
    ax.annotate("MENDEL:\nreactive site", xy=(r_idx, top + 0.01),
                xytext=(r_idx, top + 0.07),
                ha="center", va="bottom", fontsize=8, color="#333",
                arrowprops=dict(arrowstyle="->", color="#333", lw=0.8))

    ax.set_xticks(x)
    ax.set_xticklabels(display, fontsize=9)
    ax.set_ylabel("Force RMSE (eV/Å)", fontsize=10)
    ax.set_ylim(0, max(b_vals + f_vals) * 1.45)
    ax.legend(fontsize=8.5, loc="upper right")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    print(f"saved figure: {path}")


if __name__ == "__main__":
    main()
