"""Reproduction: Sojourn time variance analysis.

Computes Var[W] via the phase-type absorbing Markov chain (Eq. 13-14 in the
paper) and produces:
  1. Variance convergence plot vs bound b
  2. Variance heatmap over (theta12, theta21) parameter space
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sojourn time variance analysis.")
    # Convergence part
    parser.add_argument("--bounds", default="4,6,8,10,12,14,16")
    parser.add_argument("--theta12", type=float, default=3)
    parser.add_argument("--theta21", type=float, default=1)
    parser.add_argument("--arrival-rate1", type=float, default=2 / 3)
    parser.add_argument("--arrival-rate2", type=float, default=1 / 3)
    parser.add_argument("--service-rate1", type=float, default=1.5)
    parser.add_argument("--service-rate2", type=float, default=2.5)
    # Heatmap part
    parser.add_argument("--h12-min", type=float, default=0.0)
    parser.add_argument("--h12-max", type=float, default=3.0)
    parser.add_argument("--h12-step", type=float, default=0.2)
    parser.add_argument("--h21-min", type=float, default=0.0)
    parser.add_argument("--h21-max", type=float, default=3.0)
    parser.add_argument("--h21-step", type=float, default=0.2)
    parser.add_argument("--heatmap-bound", type=int, default=16)
    parser.add_argument("--num-servers", type=int, default=1)
    add_common_paths(parser)
    return parser


def parse_int_list(raw: str) -> list[int]:
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def compute_variance(
    arrival_rates: list[float],
    service_rates: list[float],
    thetas: list[list[float | None]],
    bound: int,
    num_servers: int,
) -> dict:
    """Compute mean and variance of sojourn time via the Markov chain."""
    import models

    num_classes = len(arrival_rates)

    state_probs = models.get_state_probabilities(
        num_classes=num_classes, num_servers=num_servers,
        arrival_rates=arrival_rates, service_rates=service_rates,
        thetas=thetas, bound=bound,
    )

    ss_sojourn, tm_sojourn = models.build_state_space_and_transition_matrix_sojourn_mc(
        num_classes=num_classes, num_servers=num_servers,
        arrival_rates=arrival_rates, service_rates=service_rates,
        thetas=thetas, bound=bound,
    )

    mean_sojourn = models.get_mean_sojourn_times(
        ss_sojourn, tm_sojourn, num_classes, arrival_rates, state_probs,
    )
    var_sojourn = models.find_var_sojourn_time(
        ss_sojourn, tm_sojourn, arrival_rates, state_probs,
    )

    mean_customers = models.get_average_num_of_customers_from_state_probs(
        state_probs=state_probs, num_classes=num_classes,
    )

    return {
        "bound": bound,
        "W_1": mean_sojourn[0], "W_2": mean_sojourn[1], "W": mean_sojourn[-1],
        "Var_W": var_sojourn,
        "L_1": mean_customers[0], "L_2": mean_customers[1], "L": mean_customers[-1],
    }


def plot_convergence(
    df: pd.DataFrame, args: argparse.Namespace, out_dir: Path,
) -> None:
    """Plot mean and variance convergence vs bound."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))

    ax = axes[0]
    for col, label in [("W_1", "W1"), ("W_2", "W2"), ("W", "W overall")]:
        ax.plot(df["bound"], df[col], marker="o", label=label, linewidth=1.5)
    ax.set_xlabel("Bound b")
    ax.set_ylabel("Mean sojourn time")
    ax.set_title("E[W] convergence")
    ax.legend(frameon=True)

    ax = axes[1]
    ax.plot(df["bound"], df["Var_W"], marker="s", color="#2a788e", linewidth=1.5)
    ax.set_xlabel("Bound b")
    ax.set_ylabel("Var[W]")
    ax.set_title("Var[W] convergence")
    ax.set_yscale("log")

    ax = axes[2]
    cv = np.sqrt(df["Var_W"]) / df["W"]
    ax.plot(df["bound"], cv, marker="D", color="#d95f02", linewidth=1.5)
    ax.set_xlabel("Bound b")
    ax.set_ylabel("CV[W] = sigma / E[W]")
    ax.set_title("Coefficient of variation convergence")

    fig.suptitle(
        f"Sojourn time moments: theta12={args.theta12}, theta21={args.theta21}, "
        f"lambda=({args.arrival_rate1:.3f},{args.arrival_rate2:.3f})",
        fontsize=11,
    )
    fig.tight_layout()

    out_png = out_dir / "sojourn_variance_convergence.png"
    out_csv = out_dir / "sojourn_variance_convergence.csv"
    fig.savefig(out_png, dpi=200)
    df.to_csv(out_csv, index=False)
    print(f"wrote {out_png}")
    print(f"wrote {out_csv}")
    plt.close(fig)


def plot_variance_heatmap(
    df: pd.DataFrame, out_dir: Path,
) -> None:
    """Plot heatmap of Var[W] over (h12, h21) grid."""
    h12_vals = sorted(df["h12"].unique())
    h21_vals = sorted(df["h21"].unique())

    pivot_var = df.pivot(index="h21", columns="h12", values="Var_W").sort_index(ascending=True)
    pivot_cv = df.pivot(index="h21", columns="h12", values="CV_W").sort_index(ascending=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    for ax, pivot, title, label in [
        (axes[0], pivot_var, "Var[W] - Sojourn time variance", "Var[W]"),
        (axes[1], pivot_cv, "CV[W] - Coefficient of variation", "CV[W]"),
    ]:
        data = pivot.to_numpy()
        im = ax.imshow(data, origin="lower", aspect="auto", cmap="viridis")
        ax.set_xticks(range(len(h12_vals)))
        ax.set_xticklabels([f"{x:.1f}" for x in h12_vals], rotation=45, fontsize=8)
        ax.set_yticks(range(len(h21_vals)))
        ax.set_yticklabels([f"{y:.1f}" for y in h21_vals], fontsize=8)
        ax.set_xlabel("theta12 (upgrade rate)")
        ax.set_ylabel("theta21 (downgrade rate)")
        ax.set_title(title)
        plt.colorbar(im, ax=ax, label=label)

    fig.tight_layout()

    out_png = out_dir / "sojourn_variance_heatmap.png"
    out_csv = out_dir / "sojourn_variance_heatmap.csv"
    fig.savefig(out_png, dpi=200)
    df.to_csv(out_csv, index=False)
    print(f"wrote {out_png}")
    print(f"wrote {out_csv}")
    plt.close(fig)


def main() -> None:
    import models

    args = build_parser().parse_args()
    ensure_output_dirs()
    ensure_results_dir(args.results_dir)

    # ---- Part 1: Convergence over bounds ----
    print("=== Part 1: Variance convergence over bounds ===")
    rows = []
    bounds = parse_int_list(args.bounds)
    thetas = class_change_matrix(args.theta12, args.theta21)
    arrival_rates = [args.arrival_rate1, args.arrival_rate2]
    service_rates = [args.service_rate1, args.service_rate2]

    for bound in bounds:
        print(f"bound={bound}...", flush=True)
        row = compute_variance(
            arrival_rates=arrival_rates, service_rates=service_rates,
            thetas=thetas, bound=bound, num_servers=args.num_servers,
        )
        rows.append(row)

    df_conv = pd.DataFrame(rows)
    df_conv.insert(1, "theta12", args.theta12)
    df_conv.insert(2, "theta21", args.theta21)
    df_conv.insert(3, "arrival_rate1", args.arrival_rate1)
    df_conv.insert(4, "arrival_rate2", args.arrival_rate2)
    df_conv.insert(5, "service_rate1", args.service_rate1)
    df_conv.insert(6, "service_rate2", args.service_rate2)
    df_conv.insert(7, "num_servers", args.num_servers)
    plot_convergence(df_conv, args, args.results_dir)

    # ---- Part 2: Variance heatmap over (h12, h21) ----
    print("\n=== Part 2: Variance heatmap over (h12, h21) ===")
    h12_values = np.arange(args.h12_min, args.h12_max + 0.5 * args.h12_step, args.h12_step)
    h21_values = np.arange(args.h21_min, args.h21_max + 0.5 * args.h21_step, args.h21_step)
    total = len(h12_values) * len(h21_values)
    count = 0

    heatmap_rows = []
    for h12 in h12_values:
        for h21 in h21_values:
            count += 1
            if count % 10 == 0 or count == 1:
                print(f"[{count}/{total}] h12={h12:.2f}, h21={h21:.2f}", flush=True)
            result = compute_variance(
                arrival_rates=arrival_rates, service_rates=service_rates,
                thetas=class_change_matrix(float(h12), float(h21)),
                bound=args.heatmap_bound, num_servers=args.num_servers,
            )
            result["h12"] = float(h12)
            result["h21"] = float(h21)
            result["heatmap_bound"] = args.heatmap_bound
            result["arrival_rate1"] = args.arrival_rate1
            result["arrival_rate2"] = args.arrival_rate2
            result["service_rate1"] = args.service_rate1
            result["service_rate2"] = args.service_rate2
            result["num_servers"] = args.num_servers
            result["CV_W"] = np.sqrt(result["Var_W"]) / result["W"] if result["W"] > 0 else np.nan
            heatmap_rows.append(result)

    df_heat = pd.DataFrame(heatmap_rows)
    plot_variance_heatmap(df_heat, args.results_dir)


if __name__ == "__main__":
    main()
