# Experiment Log

## Validation

Command:

```powershell
..\.venv\Scripts\python.exe -m pytest .
```

Result:

```text
28 passed
```

## Figure 5-style overtaking replication

Command:

```powershell
..\.venv\Scripts\python.exe project_reproduction\reproduce_figure5.py
```

Outputs:

- `results/figure5_replication.png`
- `results/figure5_metrics.csv`

The script runs the paper's 3 by 3 grid over `h12 in {1, 2, 3}` and
`h21 in {0, 1, 2}` with 5 trials. It uses common random numbers across grid
points by default, matching the notebook's use of a fixed default seed.

## Stability replication

Command:

```powershell
..\.venv\Scripts\python.exe project_reproduction\reproduce_stability.py
```

Outputs:

- `results/stability_replication.png`
- `results/stability_metrics.csv`
- `results/stability_histories.csv`

Note: `plan.md` lists `theta12=3, theta21=1`, but the repository notebook's
stability example uses `theta12=2, theta21=1`. The notebook setting produced the
expected ADF split:

- stable-like: ADF p-value about `0.00385`
- unstable-like: ADF p-value about `0.864`

## Bounded Markov approximation

Command:

```powershell
..\.venv\Scripts\python.exe project_reproduction\reproduce_bounded_markov.py
```

Outputs:

- `results/bounded_markov_replication.png`
- `results/bounded_markov_metrics.csv`

Default bounds are `2` through `10` to keep dense absorbing-chain solves fast.
The curves stabilize over the tested range, and boundary measures decrease.

## Extension 1: calibration of H

Command:

```powershell
..\.venv\Scripts\python.exe project_reproduction\extension_calibrate_H.py
```

Outputs:

- `results/extension_calibration_heatmap.png`
- `results/extension_calibration_metrics.csv`

Default grid:

- `h12 = 0, 0.5, ..., 5`
- `h21 = 0, 0.5, ..., 3`
- `trials = 3`

The calibration script also uses common random numbers across candidates by
default. This reduces noise when comparing nearby values of `H`.
