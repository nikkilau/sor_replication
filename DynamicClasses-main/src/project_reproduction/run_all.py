from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1]


def run(args: list[str]) -> None:
    print("running:", " ".join(args), flush=True)
    subprocess.run([sys.executable, *args], cwd=SRC_DIR, check=True)


def main() -> None:
    run(["project_reproduction/reproduce_figure5.py"])
    run(["project_reproduction/reproduce_stability.py"])
    run(["project_reproduction/reproduce_bounded_markov.py"])
    run(["project_reproduction/extension_calibrate_H.py"])


if __name__ == "__main__":
    main()
