"""Reproduction: Effect of class-switching matrix H on queue metrics.

Grid search over (h12, h21) for three service-rate scenarios, using the
bounded Markov chain to compute L_k, W_k, and sojourn-time variance U.
Produces heatmaps comparable to the paper's effect-of-H figures.
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
)

SCENARIOS = {
    "A_prioritized_slower": {
        "label": "Prioritized class slower (mu1=2.5, mu2=3.5)",
        "arrival_rates": [1.0, 1.0],
        "service_rates": [2.5, 3.5],
    },
    "B_equal": {
        "label": "Equal service rates (mu1=3, mu2=3)",
        "arrival_rates": [1.0, 1.0],
        "service_rates": [3.0, 3.0],
    },
    "C_prioritized_faster": {
        "label": "Prioritized class faster (mu1=3.5, mu2=2.5)",
        "arrival_rates": [1.0, 1.0],
        "service_rates": [3.5, 2.5],
    },
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reproduce effect of H matrix heatmaps.")
    parser.add_argument("--h12-min", type=float, default=0.0)
    parser.add_argument("--h12-max", type=float, default=3.0)
    parser.add_argument("--h12-step", type=float, default=0.2)
    parser.add_argument("--h21-min", type=float, default=0.0)
    parser.add_argument("--h21-max", type=float, default=3.0)
    parser.add_argument("--h21-step", type=float, default=0.2)
    parser.add_argument("--bound", type=int, default=16)
    parser.add_argument("--num-servers", type=int, default=1)
    add_common_paths(parser)
    return parser


def compute_metrics_for_params(
    h12: float,
    h21: float,
    arrival_rates: list[float],
    service_rates: list[float],
    num_servers: int,
    bound: int,
) -> dict:
    """Compute all Markov-chain metrics for a single (h12, h21) point."""
    import models

    num_classes = len(arrival_rates)
    thetas = class_change_matrix(h12, h21)

    state_probs = models.get_state_probabilities(
        num_classes=num_classes,
        num_servers=num_servers,
        arrival_rates=arrival_rates,
        service_rates=service_rates,
        thetas=thetas,
        bound=bound,
    )

    state_space_sojourn, transition_matrix_sojourn = (
        models.build_state_space_and_transition_matrix_sojourn_mc(
            num_classes=num_classes,
            num_servers=num_servers,
            arrival_rates=arrival_rates,
            service_rates=service_rates,
            thetas=thetas,
            bound=bound,
        )
    )

    mean_customers = models.get_average_num_of_customers_from_state_probs(
        state_probs=state_probs, num_classes=num_classes
    )
    mean_sojourn = models.get_mean_sojourn_times(
        state_space_sojourn,
        transition_matrix_sojourn,
        num_classes,
        arrival_rates,
        state_probs,
    )
    var_sojourn = models.find_var_sojourn_time(
        state_space_sojourn, transition_matrix_sojourn, arrival_rates, state_probs
    )
    relative_boundary = models.get_relative_prob_at_boundary(state_probs, bound)
    hit_boundary = models.get_probability_of_hitting_boundary(
        state_space_sojourn,
        transition_matrix_sojourn,
        bound,
        arrival_rates,
        state_probs,
    )

    return {
        "h12": h12,
        "h21": h21,
        "L_1": mean_customers[0],
        "L_2": mean_customers[1],
        "L": mean_customers[-1],
        "W_1": mean_sojourn[0],
        "W_2": mean_sojourn[1],
        "W": mean_sojourn[-1],
        "U": var_sojourn,
        "Q_boundary": relative_boundary,
        "P_hit_boundary": hit_boundary,
    }


def plot_heatmaps(
    df: pd.DataFrame,
    scenario_name: str,
    scenario_label: str,
    out_dir: Path,
) -> None:
    """Generate heatmaps for L1, L2, W1, W2, and U."""
    h12_vals = sorted(df["h12"].unique())
    h21_vals = sorted(df["h21"].unique())

    def pivot(column: str) -> np.ndarray:
        return df.pivot(index="h21", columns="h12", values=column).sort_index(
            ascending=True
        ).to_numpy()

    metrics = [
        ("L_1", "E[L1] - Class 1 customers"),
        ("L_2", "E[L2] - Class 2 customers"),
        ("W_1", "E[W1] - Class 1 sojourn time"),
        ("W_2", "E[W2] - Class 2 sojourn time"),
        ("U", "Var[W] - Sojourn time variance"),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    axes = axes.flatten()

    for idx, (col, title) in enumerate(metrics):
        ax = axes[idx]
        data = pivot(col)
        im = ax.imshow(data, origin="lower", aspect="auto", cmap="viridis")
        ax.set_xticks(range(len(h12_vals)))
        ax.set_xticklabels([f"{x:.1f}" for x in h12_vals], rotation=45, fontsize=7)
        ax.set_yticks(range(len(h21_vals)))
        ax.set_yticklabels([f"{y:.1f}" for y in h21_vals], fontsize=7)
        ax.set_xlabel("theta12 (upgrade rate)")
        ax.set_ylabel("theta21 (downgrade rate)")
        ax.set_title(title, fontsize=11)
        plt.colorbar(im, ax=ax, shrink=0.82)

    # Remove unused sixth subplot
    axes[-1].set_visible(False)

    fig.suptitle(f"Scenario {scenario_name[-1]}: {scenario_label}", fontsize=13, y=1.01)
    fig.tight_layout()

    stem = f"effect_of_H_{scenario_name}"
    out_png = out_dir / f"{stem}.png"
    out_csv = out_dir / f"{stem}.csv"
    fig.savefig(out_png, dpi=200, bbox_inches="tight")
    df.to_csv(out_csv, index=False)
    print(f"wrote {out_png}")
    print(f"wrote {out_csv}")
    plt.close(fig)


def main() -> None:
    args = build_parser().parse_args()
    ensure_output_dirs()
    ensure_results_dir(args.results_dir)

    h12_values = np.arange(args.h12_min, args.h12_max + 0.5 * args.h12_step, args.h12_step)
    h21_values = np.arange(args.h21_min, args.h21_max + 0.5 * args.h21_step, args.h21_step)

    total = len(SCENARIOS) * len(h12_values) * len(h21_values)
    count = 0

    for scenario_name, cfg in SCENARIOS.items():
        rows = []
        for h12 in h12_values:
            for h21 in h21_values:
                count += 1
                print(
                    f"[{count}/{total}] {scenario_name}: h12={h12:.2f}, h21={h21:.2f}",
                    flush=True,
                )
                rows.append(
                    {
                        "scenario": scenario_name,
                        "bound": args.bound,
                        "num_servers": args.num_servers,
                        **compute_metrics_for_params(
                            h12=float(h12),
                            h21=float(h21),
                            arrival_rates=cfg["arrival_rates"],
                            service_rates=cfg["service_rates"],
                            num_servers=args.num_servers,
                            bound=args.bound,
                        ),
                    }
                )

        df = pd.DataFrame(rows)
        plot_heatmaps(df, scenario_name, cfg["label"], args.results_dir)


if __name__ == "__main__":
    main()
