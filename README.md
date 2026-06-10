# Queues under Stochastic Priority Switching - Reproduction & Extension

Course project for **Stochastic Operations Research (SOR)**, reproducing and
extending the paper:

> Palmer, G. I., Panayidis, M., Knight, V., & Williams, E. (2026).
> *Queues under stochastic priority switching.*
> Journal of the Operational Research Society.

## Overview

The paper proposes a generalized `M/M/c` queueing model where customers
randomly switch priority classes while waiting in the queue. It develops a
discrete-event simulation model using Ciw and continuous-time Markov chain
formulations for system-level and sojourn-time metrics.

Original code: [geraintpalmer/DynamicClasses](https://github.com/geraintpalmer/DynamicClasses)
(MIT License, see `archive/original/LICENSE`).

## Implemented Reproductions

- **Figure 5 style overtaking fit**: observed vs simulated overtaking
  distributions, with Wasserstein distance and waiting-time MAPE. The
  reproduction script reports these two paper metrics separately; composite
  calibration loss is kept in the extension script only.
- **Stability analysis**: stable-like vs unstable-like queue trajectories with
  ADF stationarity checks.
- **Bounded Markov chain**: finite-bound estimates for `L`, `W`, `Q(b)`, and
  `P(b)`.
- **Effect of switching matrix**: heatmaps for queue-length, sojourn-time, and
  variance metrics over the two-class switching-rate grid.
- **Markov chain vs simulation validation**: finite-bound CTMC comparisons
  against a long discrete-event simulation.

## Implemented Extensions

- **Fine-grid calibration of the switching matrix**: an 11x7 grid search over
  `(theta12, theta21)` using an exploratory `calibration_loss` built from the
  same overtaking/waiting-time loss components.
- **Sojourn-time variance visualization**: phase-type second-moment calculations
  and heatmaps over the switching-rate grid.

Not yet implemented: heavy-tailed / non-exponential switching experiments and
the full stability-boundary map. These remain in `plan.md` as future work.

## Quick Start

Open `results_summary.ipynb` to browse the generated figures, metrics tables,
and explanations in one place. The slide deck source is in `slides/main.tex`,
with a compiled PDF at `slides/main.pdf`.

## Repository Structure

```text
.
|-- README.md
|-- results_summary.ipynb
|-- results/
|   |-- parameter_variants/
|   |   |-- common/
|   |   |-- paper_text/
|   |   `-- original_notebook/
|   `-- extension_calibration/
|-- report/
|   |-- reproduction_report_zh.tex
|   `-- reproduction_report_zh.pdf
|-- reproduction/
|   |-- reproduce_figure5.py
|   |-- reproduce_stability.py
|   |-- reproduce_bounded_markov.py
|   |-- reproduce_effect_of_H.py
|   |-- reproduce_mc_vs_sim.py
|   |-- reproduce_sojourn_variance.py
|   |-- extension_calibrate_H.py
|   |-- run_parameter_variants.py
|   `-- run_all.py
|-- archive/
|   |-- legacy_results/
|   `-- original/
|       `-- src/models/
|-- slides/
|   |-- main.tex
|   |-- main.pdf
|   `-- presentation_script_zh.md
|-- SOR proposal.md
|-- plan.md
`-- Queues under stochastic priority switching.pdf
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r archive/original/requirements.txt  # if available; see reproduction/ for current scripts
```

The current local `.venv` may contain newer package versions than the
archived `requirements.txt`; record exact package versions before reporting
final numerical values.

## Reproduction Scope Notes

The paper text and the original notebooks disagree in two places that affect
numerical reproduction:

- The stability illustration is described in the paper text with
  `theta12=3, theta21=1`, while the original notebook at `archive/original/src/Motivating Justification.ipynb`
  uses `theta12=2, theta21=1`. The default reproduction follows the paper text;
  use `--theta12 2 --theta21 1` to reproduce the notebook setting.
- The bounded Markov approximation is described in the paper/LaTeX with
  `mu2=5/2`, while the original notebook at `archive/original/src/Demonstrate Checks.ipynb` uses `mu2=5/3`.
  The default reproduction follows the paper text; use
  `--service-rate2 1.6666666667` to reproduce the notebook setting.

Zero switching rates are now handled exactly. Discrete-event simulations pass
`None` to Ciw for disabled switching, while Markov-chain calculations use
exact `0.0` transition rates.

Earlier pre-fix outputs have been moved to `archive/legacy_results/`.
The authoritative outputs are in `results/`.
Rerun the relevant scripts before treating any metric table as final evidence.

## Running The Scripts

Run scripts from the repository root in module mode:

```bash
python -m reproduction.reproduce_figure5
python -m reproduction.reproduce_stability
python -m reproduction.reproduce_bounded_markov
python -m reproduction.reproduce_effect_of_H
python -m reproduction.extension_calibrate_H
```

Run the implemented suite:

```bash
python -m reproduction.run_all
```

Run the paper-text and original-notebook parameter variants into separate
directories:

```bash
# Preview commands without running experiments:
python -m reproduction.run_parameter_variants --dry-run

# Run only the scripts affected by known paper/notebook parameter conflicts:
python -m reproduction.run_parameter_variants --variant both
```

Increase `--bounds`, `--trials`, or calibration grid sizes for higher-resolution
final runs.

## License

The original code by Geraint Palmer is distributed under the MIT License. This
reproduction and extension code follows the same license terms.
