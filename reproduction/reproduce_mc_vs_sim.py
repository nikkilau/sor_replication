"""Reproduction: Systematic Markov Chain vs Simulation comparison.

Compares the bounded CTMC approximation against discrete-event simulation
for state probabilities and sojourn times across different bound values.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from reproduction.utils import (
    add_common_paths,
    class_change_matrix,
    ensure_output_dirs,
    ensure_results_dir,
    simulation_class_change_matrix,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Systematic MC vs Simulation comparison.")
    parser.add_argument("--bounds", default="6,8,10,12,14")
    parser.add_argument("--theta12", type=float, default=3)
    parser.add_argument("--theta21", type=float, default=1)
    parser.add_argument("--arrival-rate1", type=float, default=2 / 3)
    parser.add_argument("--arrival-rate2", type=float, default=1 / 3)
    parser.add_argument("--service-rate1", type=float, default=1.5)
    parser.add_argument("--service-rate2", type=float, default=2.5)
    parser.add_argument("--sim-time", type=float, default=5000)
    parser.add_argument("--warmup", type=float, default=500)
    parser.add_argument("--cooldown", type=float, default=500)
    parser.add_argument("--seed", type=int, default=42)
    add_common_paths(parser)
    return parser


def parse_int_list(raw: str) -> list[int]:
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def main() -> None:
    import models

    args = build_parser().parse_args()
    ensure_output_dirs()
    ensure_results_dir(args.results_dir)

    bounds = parse_int_list(args.bounds)
    arrival_rates = [args.arrival_rate1, args.arrival_rate2]
    service_rates = [args.service_rate1, args.service_rate2]
    markov_thetas = class_change_matrix(args.theta12, args.theta21)
    simulation_thetas = simulation_class_change_matrix(args.theta12, args.theta21)
    num_classes = 2
    num_servers = 1

    # ---- Run simulation once ----
    print("Running long simulation as ground truth...", flush=True)
    Q = models.build_and_run_simulation(
        num_classes=num_classes,
        num_servers=num_servers,
        arrival_rates=arrival_rates,
        service_rates=service_rates,
        class_change_rate_matrix=simulation_thetas,
        max_simulation_time=args.sim_time,
        progress_bar=False,
        seed=args.seed,
    )
    sim_probs = models.get_state_probabilities_from_simulation(
        Q, warmup=args.warmup, cooldown=args.cooldown
    )
    sim_agg = models.aggregate_states(sim_probs)
    sim_sojourn = models.find_mean_sojourn_time_by_class_from_simulation(
        Q, num_classes=num_classes, warmup=args.warmup
    )

    # ---- Run MC for each bound ----
    rows = []
    for bound in bounds:
        print(f"MC bound={bound}...", flush=True)
        mc_probs = models.get_state_probabilities(
            num_classes=num_classes,
            num_servers=num_servers,
            arrival_rates=arrival_rates,
            service_rates=service_rates,
            thetas=markov_thetas,
            bound=bound,
        )
        mc_agg = models.aggregate_states(mc_probs)

        ss_sojourn, tm_sojourn = models.build_state_space_and_transition_matrix_sojourn_mc(
            num_classes=num_classes,
            num_servers=num_servers,
            arrival_rates=arrival_rates,
            service_rates=service_rates,
            thetas=markov_thetas,
            bound=bound,
        )
        mc_sojourn = models.get_mean_sojourn_times(
            ss_sojourn, tm_sojourn, num_classes, arrival_rates, mc_probs,
        )

        # Wasserstein distance between state-probability distributions
        max_n = max(max(mc_agg.keys()), max(sim_agg.keys()))
        mc_vec = np.array([mc_agg.get(i, 0.0) for i in range(max_n + 1)])
        sim_vec = np.array([sim_agg.get(i, 0.0) for i in range(max_n + 1)])
        from scipy.stats import wasserstein_distance
        w_dist = wasserstein_distance(
            np.arange(len(mc_vec)), np.arange(len(sim_vec)),
            u_weights=mc_vec, v_weights=sim_vec,
        )

        sojourn_errors = {
            f"W_{c}_mc": mc_sojourn[c] for c in range(num_classes)
        }
        sojourn_errors.update({
            f"W_{c}_sim": sim_sojourn[c] for c in range(num_classes)
        })
        sojourn_errors.update({
            f"W_{c}_err": abs(mc_sojourn[c] - sim_sojourn[c]) / max(sim_sojourn[c], 1e-9)
            for c in range(num_classes)
        })

        rows.append({
            "bound": bound,
            "theta12": args.theta12,
            "theta21": args.theta21,
            "arrival_rate1": args.arrival_rate1,
            "arrival_rate2": args.arrival_rate2,
            "service_rate1": args.service_rate1,
            "service_rate2": args.service_rate2,
            "sim_time": args.sim_time,
            "warmup": args.warmup,
            "cooldown": args.cooldown,
            "seed": args.seed,
            "wasserstein_L": w_dist,
            **sojourn_errors,
            "W_mc": mc_sojourn[-1],
            "W_sim": sim_sojourn[-1],
            "W_err": abs(mc_sojourn[-1] - sim_sojourn[-1]) / max(sim_sojourn[-1], 1e-9),
        })

    df = pd.DataFrame(rows)

    # ---- Plots ----
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))

    # State probability comparison at largest bound
    ax = axes[0]
    best_bound = bounds[-1]
    mc_probs_best = models.get_state_probabilities(
        num_classes=num_classes,
        num_servers=num_servers,
        arrival_rates=arrival_rates,
        service_rates=service_rates,
        thetas=markov_thetas,
        bound=best_bound,
    )
    mc_agg_best = models.aggregate_states(mc_probs_best)
    max_show = 20
    xs = range(max_show)
    ax.bar(
        [x - 0.15 for x in xs], [mc_agg_best.get(i, 0) for i in xs],
        width=0.3, label=f"MC (b={best_bound})", color="#2a788e", alpha=0.85,
    )
    ax.bar(
        [x + 0.15 for x in xs], [sim_agg.get(i, 0) for i in xs],
        width=0.3, label="Simulation", color="lightgrey", edgecolor="black", alpha=0.7,
    )
    ax.set_xlabel("Total customers in system")
    ax.set_ylabel("Probability")
    ax.set_title(f"State distribution (b={best_bound})")
    ax.legend(frameon=True)

    # Wasserstein convergence
    ax = axes[1]
    ax.plot(df["bound"], df["wasserstein_L"], marker="o", linewidth=1.5, color="#2a788e")
    ax.set_xlabel("Bound b")
    ax.set_ylabel("Wasserstein distance")
    ax.set_title("State distribution error vs bound")
    ax.set_yscale("log")

    # Sojourn time convergence
    ax = axes[2]
    for c in range(num_classes):
        ax.plot(
            df["bound"], df[f"W_{c}_err"], marker="o",
            label=f"W{c+1} relative error", linewidth=1.5,
        )
    ax.plot(df["bound"], df["W_err"], marker="s", label="W overall", linewidth=1.5, color="black")
    ax.set_xlabel("Bound b")
    ax.set_ylabel("Relative error")
    ax.set_title("Sojourn time error vs bound")
    ax.set_yscale("log")
    ax.legend(frameon=True)

    fig.suptitle(
        f"MC vs Simulation: theta12={args.theta12}, theta21={args.theta21}, "
        f"lambda=({args.arrival_rate1:.3f},{args.arrival_rate2:.3f}), "
        f"mu=({args.service_rate1},{args.service_rate2})",
        fontsize=11,
    )
    fig.tight_layout()

    out_png = args.results_dir / "mc_vs_sim_comparison.png"
    out_csv = args.results_dir / "mc_vs_sim_metrics.csv"
    fig.savefig(out_png, dpi=200)
    df.to_csv(out_csv, index=False)
    print(f"wrote {out_png}")
    print(f"wrote {out_csv}")


if __name__ == "__main__":
    main()
