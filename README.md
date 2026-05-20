# Queues under Stochastic Priority Switching — Reproduction & Extension

Course project for **Stochastic Operations Research (SOR)**, reproducing and
extending the paper:

> Palmer, G. I., Panayidis, M., Knight, V., & Williams, E. (2026).
> *Queues under stochastic priority switching.*
> Journal of the Operational Research Society.

## Overview

The paper proposes a generalized `M/M/c` queueing model where customers
randomly switch priority classes while waiting in the queue. It develops both
a discrete-event simulation (using Ciw) and two continuous-time Markov chain
formulations for system-level and sojourn-time metrics.

**Original code:** [geraintpalmer/DynamicClasses](https://github.com/geraintpalmer/DynamicClasses)
(MIT License — see [original/LICENSE](original/LICENSE))

## What was reproduced

- **Figure 5** — Black-box service fitting via Wasserstein distance / MAPE
  minimization
- **Stability analysis** — ADF test replication for non-stationary queue
  identification (Proposition 1)
- **Bounded Markov chain** — The b-bounded truncation approximation, including
  boundary accuracy metrics Q(b) and P(b)

## Extensions beyond the original paper

- **Heavy-tailed service times**: replaced the exponential service-time
  assumption with Pareto-distributed service times in the simulation engine to
  probe whether the stochastic switching mechanism degrades under long-tail
  workloads.
- **Parameter sensitivity calibration**: grid-based search over the Θ matrix
  space to quantify how robust the fitting approach is to prior
  misspecification.

## Quick start: browse results

Open **[results_summary.ipynb](results_summary.ipynb)** — a Jupyter notebook that
displays all reproduction figures, metrics tables, and explanations in one place.
Recommended for the course presentation.

## Repository structure

```
.
├── README.md                    # Project overview (this file)
├── results_summary.ipynb        # All results in one notebook
├── results/                     # Reproduction figures and CSV metrics
│   ├── figure5_replication.png
│   ├── stability_replication.png
│   ├── bounded_markov_replication.png
│   └── extension_calibration_heatmap.png
├── reproduction/                # Our reproduction & extension scripts
│   ├── reproduce_figure5.py
│   ├── reproduce_stability.py
│   ├── reproduce_bounded_markov.py
│   ├── extension_calibrate_H.py
│   └── run_all.py               # Run all scripts in order
├── original/                    # Original paper code (geraintpalmer/DynamicClasses)
│   └── src/models/              # Ciw queue models
├── SOR proposal.md              # Project proposal (Chinese)
├── plan.md                      # Detailed project plan
└── Queues under stochastic priority switching.pdf  # Original paper
```

## Running the reproduction scripts

```bash
# From the repo root:
python reproduction/reproduce_figure5.py
python reproduction/reproduce_stability.py
python reproduction/reproduce_bounded_markov.py
python reproduction/extension_calibrate_H.py

# Or run all at once:
python reproduction/run_all.py
```

Increase `--bounds`, `--trials`, or calibration grid sizes for higher-resolution
final runs.

## License

The original code by Geraint Palmer is distributed under the MIT License
(see [original/LICENSE](original/LICENSE)). Our
reproduction and extension code is also available under the same terms.
