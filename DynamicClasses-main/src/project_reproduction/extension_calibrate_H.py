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
    parser = argparse.ArgumentParser(description="Finer calibration search for H.")
    parser.add_argument("--h12-values", default="0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5")
    parser.add_argument("--h21-values", default="0,0.5,1,1.5,2,2.5,3")
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--seed", type=int, default=100)
    parser.add_argument("--alpha", type=float, default=1.0)
    parser.add_argument("--beta", type=float, default=1.0)
    add_common_paths(parser)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    ensure_output_dirs()
    args.results_dir.mkdir(exist_ok=True)

    observed = load_surgery_data()
    h12_values = parse_float_list(args.h12_values)
    h21_values = parse_float_list(args.h21_values)
    rows = []

    for i, h12 in enumerate(h12_values):
        for j, h21 in enumerate(h21_values):
            print(f"running h12={h12:g}, h21={h21:g}", flush=True)
            sim = simulate_overtaking(
                theta12=h12,
                theta21=h21,
                n_trials=args.trials,
                seed=args.seed,
            )
            metrics = overtaking_metrics(sim, observed)
            loss = args.alpha * metrics["wasserstein"] + args.beta * metrics["mape"]
            rows.append({"h12": h12, "h21": h21, **metrics, "loss": loss})

    df = pd.DataFrame(rows).sort_values("loss")
    out_csv = args.results_dir / "extension_calibration_metrics.csv"
    df.to_csv(out_csv, index=False)

    pivot = df.pivot(index="h21", columns="h12", values="loss").sort_index(ascending=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    image = ax.imshow(pivot.to_numpy(), origin="lower", aspect="auto", cmap="viridis")
    ax.set_xticks(np.arange(len(pivot.columns)))
    ax.set_xticklabels([f"{x:g}" for x in pivot.columns], rotation=45)
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels([f"{y:g}" for y in pivot.index])
    ax.set_xlabel("h12")
    ax.set_ylabel("h21")
    ax.set_title("Calibration loss")
    fig.colorbar(image, ax=ax, label="loss")

    best = df.iloc[0]
    if best["h12"] in pivot.columns and best["h21"] in pivot.index:
        ax.scatter(
            [list(pivot.columns).index(best["h12"])],
            [list(pivot.index).index(best["h21"])],
            color="white",
            edgecolor="black",
            s=100,
            label="best",
        )
        ax.legend(frameon=True)

    fig.tight_layout()
    out_png = args.results_dir / "extension_calibration_heatmap.png"
    fig.savefig(out_png, dpi=220)
    print(f"wrote {out_png}")
    print(f"wrote {out_csv}")


if __name__ == "__main__":
    main()
