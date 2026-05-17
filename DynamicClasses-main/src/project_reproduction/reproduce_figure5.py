from __future__ import annotations

import argparse
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from project_reproduction.utils import (
    add_common_paths,
    ensure_output_dirs,
    load_surgery_data,
    overtaking_metrics,
    parse_float_list,
    simulate_overtaking,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reproduce Figure 5-style overtaking results.")
    parser.add_argument("--h12-values", default="1,2,3")
    parser.add_argument("--h21-values", default="0,1,2")
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--arrival-rate", type=float, default=0.463)
    parser.add_argument("--service-rate", type=float, default=0.5)
    add_common_paths(parser)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    ensure_output_dirs()
    args.results_dir.mkdir(exist_ok=True)

    observed = load_surgery_data()
    h12_values = parse_float_list(args.h12_values)
    h21_values = parse_float_list(args.h21_values)

    fig, axarr = plt.subplots(
        len(h12_values),
        len(h21_values),
        figsize=(5 * len(h21_values), 4 * len(h12_values)),
        squeeze=False,
    )
    rows = []
    bins = np.linspace(-25, 80, 27)

    for i, h12 in enumerate(h12_values):
        for j, h21 in enumerate(h21_values):
            ax = axarr[i][j]
            sim = simulate_overtaking(
                theta12=h12,
                theta21=h21,
                arrival_rate=args.arrival_rate,
                service_rate=args.service_rate,
                n_trials=args.trials,
                seed=args.seed,
            )
            metrics = overtaking_metrics(sim, observed)
            row = {"h12": h12, "h21": h21, **metrics}
            row["combined_loss"] = row["wasserstein"] + row["mape"]
            rows.append(row)

            ax.hist(
                observed["overtakes"],
                bins=bins,
                density=True,
                color="lightgrey",
                edgecolor="black",
                alpha=0.7,
                label="Observed",
            )
            if len(sim["overtakes"]) > 0:
                ax.hist(
                    sim["overtakes"],
                    bins=bins,
                    density=True,
                    histtype="step",
                    linewidth=2.0,
                    color="#2a788e",
                    label="Model",
                )
            ax.axvline(0, color="black", linestyle="dashed", linewidth=1.3)
            ax.set_xlim(-25, 80)
            ax.set_title(f"h12={h12:g}, h21={h21:g}")
            ax.set_xlabel("Rank difference")
            ax.set_yticklabels([])
            ax.text(
                0.97,
                0.95,
                f"W={metrics['wasserstein']:.3f}\nMAPE={metrics['mape']:.3f}",
                transform=ax.transAxes,
                ha="right",
                va="top",
                fontsize=9,
                bbox={"facecolor": "white", "edgecolor": "black", "pad": 4},
            )
            if i == 0 and j == 0:
                ax.legend(frameon=True)

    fig.tight_layout()
    out_png = args.results_dir / "figure5_replication.png"
    out_csv = args.results_dir / "figure5_metrics.csv"
    fig.savefig(out_png, dpi=220)
    pd.DataFrame(rows).sort_values("combined_loss").to_csv(out_csv, index=False)
    print(f"wrote {out_png}")
    print(f"wrote {out_csv}")


if __name__ == "__main__":
    main()
