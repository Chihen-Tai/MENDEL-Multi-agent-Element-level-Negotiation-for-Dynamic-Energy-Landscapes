"""Fine-tune ANI-2x with MENDEL-guided reactive-site force weighting (Route B).

Usage:
  python scripts/finetune_ani2x_reactive.py \\
    --reference data/reference/rmd17_ethanol_sample_converted.reference.json \\
    --output models/ani2x_reactive_finetuned.pt \\
    --report reports/finetune_ani2x_report.json \\
    --epochs 30 --lr 5e-5 --device cpu
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from mendel.weighted_finetune import (
    FineTuneConfig,
    finetune_ani2x,
    load_records,
    save_model,
    split_records,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="ANI-2x reactive-site weighted fine-tuning")
    parser.add_argument(
        "--reference",
        default="data/reference/rmd17_ethanol_sample_converted.reference.json",
    )
    parser.add_argument("--output", default="models/ani2x_reactive_finetuned.pt")
    parser.add_argument("--report", default="reports/finetune_ani2x_report.json")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--lr", type=float, default=5e-5)
    parser.add_argument("--reactive-weight", type=float, default=3.0,
                        help="Force loss multiplier for MENDEL-identified reactive atoms")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--test-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    ref_path = ROOT / args.reference
    out_path = ROOT / args.output
    report_path = ROOT / args.report

    print(f"loading reference: {ref_path}")
    records = load_records(ref_path, reactive_weight=args.reactive_weight)
    print(f"  loaded {len(records)} conformers")

    train, test = split_records(records, test_fraction=args.test_fraction, seed=args.seed)
    print(f"  split: {len(train)} train / {len(test)} test")
    print(f"  reactive atom weights (sample): {records[0].atom_weights}")
    print()

    config = FineTuneConfig(
        lr=args.lr,
        epochs=args.epochs,
        reactive_loss_weight=args.reactive_weight,
        batch_size=args.batch_size,
        seed=args.seed,
        device=args.device,
    )

    print("fine-tuning ANI-2x ...")
    model, result = finetune_ani2x(train, test, config)

    save_model(model, out_path)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(result.to_dict(), f, indent=2)
    print(f"saved report: {report_path}")
    print(f"final val force RMSE: {result.final_val_force_rmse:.4f} eV/Å")


if __name__ == "__main__":
    main()
