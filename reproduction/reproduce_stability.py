from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

import models
from reproduction.utils import add_common_paths, class_change_matrix, ensure_output_dirs, queue_history_frame


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reproduce stable vs unstable queue trajectories.")
    parser.add_argument("--horizon", type=float, default=3650)
    parser.add_argument("--warmup", type=float, default=365)
    parser.add_argument("--cooldown", type=float, default=365)
    parser.add_argument("--theta12", type=float, default=2)
    parser.add_argument("--theta21", type=float, default=1)
    parser.add_argument("--arrival-rate", type=float, default=0.463)
    parser.add_argument("--seed", type=int, default=0)
    add_common_paths(parser)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    ensure_output_dirs()
    args.results_dir.mkdir(exist_ok=True)

    scenarios = [
        {"scenario": "stable_like", "mu1": 0.5, "mu2": 0.5},
        {"scenario": "unstable_like", "mu1": 0.4, "mu2": 0.6},
    ]

    fig, ax = plt.subplots(figsize=(11, 5))
    rows = []
    history_frames = []

    for idx, scenario in enumerate(scenarios):
        Q = models.build_and_run_simulation(
            num_classes=2,
            num_servers=1,
            arrival_rates=[args.arrival_rate, 1e-15],
            service_rates=[scenario["mu1"], scenario["mu2"]],
            class_change_rate_matrix=class_change_matrix(args.theta12, args.theta21),
            max_simulation_time=args.horizon,
            progress_bar=False,
            seed=args.seed + idx,
        )
        hist = queue_history_frame(Q)
        hist["scenario"] = scenario["scenario"]
        history_frames.append(hist)
        p_value = models.adf_test_on_simulation(
            Q,
            max_simulation_time=args.horizon,
            warmup=args.warmup,
            cooldown=args.cooldown,
        )
        terminal_queue = int(hist["total"].iloc[-1])
        rows.append(
            {
                **scenario,
                "arrival_rate": args.arrival_rate,
                "theta12": args.theta12,
                "theta21": args.theta21,
                "adf_p_value": p_value,
                "terminal_queue": terminal_queue,
                "interpreted_status": "stationary-like" if p_value < 0.05 else "nonstationary-like",
            }
        )
        ax.step(hist["time"], hist["total"], where="post", label=scenario["scenario"], linewidth=1.2)

    ax.set_xlabel("Time")
    ax.set_ylabel("Total customers in system")
    ax.set_title("Queue length trajectories")
    ax.legend(frameon=True)
    fig.tight_layout()

    out_png = args.results_dir / "stability_replication.png"
    out_csv = args.results_dir / "stability_metrics.csv"
    out_hist = args.results_dir / "stability_histories.csv"
    fig.savefig(out_png, dpi=220)
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    pd.concat(history_frames, ignore_index=True).to_csv(out_hist, index=False)
    print(f"wrote {out_png}")
    print(f"wrote {out_csv}")
    print(f"wrote {out_hist}")


if __name__ == "__main__":
    main()
