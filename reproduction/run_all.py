from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str]) -> None:
    print("running:", " ".join(args), flush=True)
    subprocess.run([sys.executable, *args], cwd=REPO_ROOT, check=True)


def main() -> None:
    run(["reproduction/reproduce_figure5.py"])
    run(["reproduction/reproduce_stability.py"])
    run(["reproduction/reproduce_bounded_markov.py"])
    run(["reproduction/extension_calibrate_H.py"])


if __name__ == "__main__":
    main()
