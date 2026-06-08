from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


MODULES = [
    "reproduction.reproduce_figure5",
    "reproduction.reproduce_stability",
    "reproduction.reproduce_bounded_markov",
    "reproduction.reproduce_effect_of_H",
    "reproduction.reproduce_mc_vs_sim",
    "reproduction.reproduce_sojourn_variance",
    "reproduction.extension_calibrate_H",
]


def run(module: str) -> None:
    print("running:", module, flush=True)
    subprocess.run([sys.executable, "-m", module], cwd=REPO_ROOT, check=True)


def main() -> None:
    for module in MODULES:
        run(module)


if __name__ == "__main__":
    main()
