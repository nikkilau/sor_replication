from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from reproduction.utils import RESULTS_DIR

REPO_ROOT = Path(__file__).resolve().parents[1]


VARIANT_RUNS = {
    "paper_text": [
        [
            "reproduction.reproduce_stability",
            "--theta12",
            "3",
            "--theta21",
            "1",
        ],
        [
            "reproduction.reproduce_bounded_markov",
            "--service-rate2",
            "2.5",
        ],
        [
            "reproduction.reproduce_mc_vs_sim",
            "--service-rate2",
            "2.5",
        ],
        [
            "reproduction.reproduce_sojourn_variance",
            "--service-rate2",
            "2.5",
        ],
    ],
    "original_notebook": [
        [
            "reproduction.reproduce_stability",
            "--theta12",
            "2",
            "--theta21",
            "1",
        ],
        [
            "reproduction.reproduce_bounded_markov",
            "--service-rate2",
            "1.6666666667",
        ],
        [
            "reproduction.reproduce_mc_vs_sim",
            "--service-rate2",
            "1.6666666667",
        ],
        [
            "reproduction.reproduce_sojourn_variance",
            "--service-rate2",
            "1.6666666667",
        ],
    ],
}

COMMON_RUNS = [
    ["reproduction.reproduce_figure5"],
    ["reproduction.reproduce_effect_of_H"],
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run paper-text and original-notebook parameter variants."
    )
    parser.add_argument(
        "--variant",
        choices=["paper_text", "original_notebook", "both"],
        default="both",
        help="Which variant set to run.",
    )
    parser.add_argument(
        "--results-root",
        type=Path,
        default=RESULTS_DIR / "parameter_variants",
        help="Root output directory for variant-specific results.",
    )
    parser.add_argument(
        "--include-common",
        action="store_true",
        help="Also run scripts that do not have known paper/notebook conflicts.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without running experiments.",
    )
    return parser


def selected_variants(raw_variant: str) -> list[str]:
    if raw_variant == "both":
        return ["paper_text", "original_notebook"]
    return [raw_variant]


def run_module(module_args: list[str], results_dir: Path, dry_run: bool) -> None:
    command = [
        sys.executable,
        "-m",
        *module_args,
        "--results-dir",
        str(results_dir),
    ]
    print(" ".join(command), flush=True)
    if dry_run:
        return
    results_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def main() -> None:
    args = build_parser().parse_args()

    if args.include_common:
        common_dir = args.results_root / "common"
        for module_args in COMMON_RUNS:
            run_module(module_args, common_dir, args.dry_run)

    for variant in selected_variants(args.variant):
        variant_dir = args.results_root / variant
        for module_args in VARIANT_RUNS[variant]:
            run_module(module_args, variant_dir, args.dry_run)


if __name__ == "__main__":
    main()
