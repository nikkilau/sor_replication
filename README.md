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
(MIT License — see [LICENSE](DynamicClasses-main/LICENSE))

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

## Repository structure

```
.
├── DynamicClasses-main/         # Original code + our additions
│   ├── src/                     # Paper source code (Ciw models, experiments)
│   │   └── project_reproduction/  # Our reproduction & extension scripts
│   ├── results/                 # Generated figures and CSVs
│   └── notes/                   # Working notes
├── Queues under stochastic priority switching.pdf  # Original paper
├── SOR proposal.md              # Project proposal (Chinese)
└── plan.md                      # Detailed project plan
```

## Running the reproduction scripts

```bash
# From DynamicClasses-main/src, with the virtual environment active:
python project_reproduction/reproduce_figure5.py
python project_reproduction/reproduce_stability.py
python project_reproduction/reproduce_bounded_markov.py
python project_reproduction/extension_calibrate_H.py
```

Increase `--bounds`, `--trials`, or calibration grid sizes for higher-resolution
final runs.

## License

The original code by Geraint Palmer is distributed under the MIT License
(see [DynamicClasses-main/LICENSE](DynamicClasses-main/LICENSE)). Our
reproduction and extension code is also available under the same terms.
