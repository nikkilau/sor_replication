from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from reproduction.utils import (
    add_common_paths,
    class_change_matrix,
    ensure_output_dirs,
    ensure_results_dir,
    markov_metrics_for_bound,
    parse_int_list,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reproduce bounded Markov approximation convergence.")
    parser.add_argument(
        "--bounds",
        default="1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22",
    )
    parser.add_argument("--theta12", type=float, default=3)
    parser.add_argument("--theta21", type=float, default=1)
    parser.add_argument("--arrival-rate1", type=float, default=2 / 3)
    parser.add_argument("--arrival-rate2", type=float, default=1 / 3)
    parser.add_argument("--service-rate1", type=float, default=3 / 2)
    parser.add_argument("--service-rate2", type=float, default=5 / 2)
    add_common_paths(parser)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    ensure_output_dirs()
    ensure_results_dir(args.results_dir)
    bounds = parse_int_list(args.bounds)

    arrival_rates = [args.arrival_rate1, args.arrival_rate2]
    service_rates = [args.service_rate1, args.service_rate2]
    thetas = class_change_matrix(args.theta12, args.theta21)
    rows = []

    for bound in bounds:
        print(f"running bound={bound}", flush=True)
        rows.append(
            markov_metrics_for_bound(
                bound=bound,
                arrival_rates=arrival_rates,
                service_rates=service_rates,
                thetas=thetas,
                num_servers=1,
            )
        )

    df = pd.DataFrame(rows)
    df.insert(1, "theta12", args.theta12)
    df.insert(2, "theta21", args.theta21)
    df.insert(3, "arrival_rate1", args.arrival_rate1)
    df.insert(4, "arrival_rate2", args.arrival_rate2)
    df.insert(5, "service_rate1", args.service_rate1)
    df.insert(6, "service_rate2", args.service_rate2)
    df.insert(7, "num_servers", 1)
    df.insert(8, "parameter_source", "paper_text_default")
    out_csv = args.results_dir / "bounded_markov_metrics.csv"
    df.to_csv(out_csv, index=False)

    fig, axarr = plt.subplots(1, 3, figsize=(16, 4.5))
    for col, label in [("L_1", "L1"), ("L_2", "L2"), ("L", "L")]:
        axarr[0].plot(df["bound"], df[col], marker="o", label=label)
    axarr[0].set_xlabel("Bound")
    axarr[0].set_ylabel("Expected number in system")
    axarr[0].legend(frameon=True)

    for col, label in [("W_1", "W1"), ("W_2", "W2"), ("W", "W")]:
        axarr[1].plot(df["bound"], df[col], marker="o", label=label)
    axarr[1].set_xlabel("Bound")
    axarr[1].set_ylabel("Mean sojourn time")
    axarr[1].legend(frameon=True)

    axarr[2].semilogy(df["bound"], df["Q_boundary"], marker="o", label="Q(b)")
    axarr[2].semilogy(df["bound"], df["P_hit_boundary"], marker="o", label="P(b)")
    axarr[2].set_xlabel("Bound")
    axarr[2].set_ylabel("Boundary error measure")
    axarr[2].legend(frameon=True)

    fig.tight_layout()
    out_png = args.results_dir / "bounded_markov_replication.png"
    fig.savefig(out_png, dpi=220)
    print(f"wrote {out_png}")
    print(f"wrote {out_csv}")


if __name__ == "__main__":
    main()
