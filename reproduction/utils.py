from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance

REPO_ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_SRC = REPO_ROOT / "original" / "src"
RESULTS_DIR = REPO_ROOT / "results"
NOTES_DIR = REPO_ROOT / "original" / "notes"
DATA_PATH = ORIGINAL_SRC / "motivating_data" / "Surgery Treatment.csv"

if str(ORIGINAL_SRC) not in sys.path:
    sys.path.insert(0, str(ORIGINAL_SRC))

import models  # noqa: E402


def ensure_output_dirs() -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    NOTES_DIR.mkdir(exist_ok=True)


def parse_float_list(raw: str) -> list[float]:
    return [float(x.strip()) for x in raw.split(",") if x.strip()]


def parse_int_list(raw: str) -> list[int]:
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def add_common_paths(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=RESULTS_DIR,
        help="Directory for figures and CSV outputs.",
    )


def load_surgery_data(path: Path = DATA_PATH) -> pd.DataFrame:
    data = pd.read_csv(
        path,
        parse_dates=["START_DATE", "DATE_BOOKING_MADE", "TCI_DATE"],
        date_format="%d-%b-%y",
    )
    data["START_DATE_rank"] = data["START_DATE"].rank()
    data["TCI_DATE_rank"] = data["TCI_DATE"].rank()
    data["overtakes"] = data["TCI_DATE_rank"] - data["START_DATE_rank"]
    data["bumped_down"] = data["overtakes"] > 0
    data["wait"] = (data["TCI_DATE"] - data["START_DATE"]).dt.days
    return data


def class_change_matrix(theta12: float | None, theta21: float | None) -> list[list[float | None]]:
    t12 = None if theta12 is None or theta12 <= 0 else float(theta12)
    t21 = None if theta21 is None or theta21 <= 0 else float(theta21)
    return [[None, t12], [t21, None]]


def records_to_frame(records) -> pd.DataFrame:
    rows = [record._asdict() for record in records]
    return pd.DataFrame(rows)


def simulate_overtaking(
    theta12: float,
    theta21: float,
    arrival_rate: float = 0.463,
    service_rate: float = 0.5,
    horizon: int = 365,
    n_trials: int = 5,
    seed: int = 0,
) -> dict:
    max_time = horizon * ((2 * n_trials) + 1)
    Q = models.build_and_run_simulation(
        num_classes=2,
        num_servers=1,
        arrival_rates=[arrival_rate, 1e-15],
        service_rates=[service_rate, service_rate],
        class_change_rate_matrix=class_change_matrix(theta12, theta21),
        max_simulation_time=max_time,
        progress_bar=False,
        seed=seed,
    )
    recs = records_to_frame(Q.get_all_records())
    if len(recs) == 0:
        return {
            "overtakes": np.array([]),
            "mean_wait_up": math.nan,
            "mean_wait_down": math.nan,
            "records": recs,
        }

    recs = recs[recs["record_type"] == "service"].copy()
    overtakes: list[float] = []
    mean_wait_ups: list[float] = []
    mean_wait_downs: list[float] = []

    for trial in range(n_trials):
        start = horizon * ((2 * trial) + 1)
        end = horizon * ((2 * trial) + 2)
        recs_t = recs[
            (recs["arrival_date"] >= start) & (recs["arrival_date"] <= end)
        ].copy()
        if len(recs_t) == 0:
            continue
        recs_t["arrival_rank"] = recs_t["arrival_date"].rank()
        recs_t["service_start_rank"] = recs_t["service_start_date"].rank()
        recs_t["overtakes"] = recs_t["service_start_rank"] - recs_t["arrival_rank"]
        overtakes.extend(recs_t["overtakes"].to_numpy(dtype=float))

        down_wait = recs_t[recs_t["overtakes"] > 0]["waiting_time"].mean()
        up_wait = recs_t[recs_t["overtakes"] <= 0]["waiting_time"].mean()
        if not pd.isna(down_wait):
            mean_wait_downs.append(float(down_wait))
        if not pd.isna(up_wait):
            mean_wait_ups.append(float(up_wait))

    return {
        "overtakes": np.asarray(overtakes, dtype=float),
        "mean_wait_up": float(np.mean(mean_wait_ups)) if mean_wait_ups else math.nan,
        "mean_wait_down": float(np.mean(mean_wait_downs)) if mean_wait_downs else math.nan,
        "records": recs,
    }


def overtaking_metrics(sim: dict, observed: pd.DataFrame) -> dict[str, float]:
    sim_overtakes = sim["overtakes"]
    obs_overtakes = observed["overtakes"].to_numpy(dtype=float)
    obs_wait_up = observed[~observed["bumped_down"]]["wait"].mean()
    obs_wait_down = observed[observed["bumped_down"]]["wait"].mean()

    W = (
        float(wasserstein_distance(sim_overtakes, obs_overtakes))
        if len(sim_overtakes) > 0
        else math.nan
    )
    mape_terms = []
    if not math.isnan(sim["mean_wait_up"]) and obs_wait_up:
        mape_terms.append(abs(sim["mean_wait_up"] - obs_wait_up) / obs_wait_up)
    if not math.isnan(sim["mean_wait_down"]) and obs_wait_down:
        mape_terms.append(abs(sim["mean_wait_down"] - obs_wait_down) / obs_wait_down)

    return {
        "wasserstein": W,
        "mape": float(np.mean(mape_terms)) if mape_terms else math.nan,
        "sim_mean_wait_up": sim["mean_wait_up"],
        "sim_mean_wait_down": sim["mean_wait_down"],
        "obs_mean_wait_up": float(obs_wait_up),
        "obs_mean_wait_down": float(obs_wait_down),
        "n_sim_records": int(len(sim_overtakes)),
    }


def queue_history_frame(Q) -> pd.DataFrame:
    rows = [
        {
            "time": float(timestamp),
            "class_0": int(state[0][0]),
            "class_1": int(state[0][1]),
            "total": int(sum(state[0])),
        }
        for timestamp, state in Q.statetracker.history
    ]
    return pd.DataFrame(rows)


def markov_metrics_for_bound(
    bound: int,
    arrival_rates: list[float],
    service_rates: list[float],
    thetas: list[list[float | None]],
    num_servers: int,
) -> dict:
    num_classes = len(arrival_rates)
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
        state_probs=state_probs,
        num_classes=num_classes,
    )
    mean_sojourn = models.get_mean_sojourn_times(
        state_space_sojourn,
        transition_matrix_sojourn,
        num_classes,
        arrival_rates,
        state_probs,
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
        "bound": bound,
        "L_1": mean_customers[0],
        "L_2": mean_customers[1],
        "L": mean_customers[-1],
        "W_1": mean_sojourn[0],
        "W_2": mean_sojourn[1],
        "W": mean_sojourn[-1],
        "Q_boundary": relative_boundary,
        "P_hit_boundary": hit_boundary,
    }
