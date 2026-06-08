# Reproduction Scripts

Run all scripts from the repository root in module mode.

## Reproductions And Checks

| Module | Paper reference | What it does |
|---|---|---|
| `reproduction.reproduce_figure5` | Figure 5 | Overtaking distribution fitting over a coarse `theta` grid |
| `reproduction.reproduce_stability` | Proposition 1 | ADF check on stable-like vs unstable-like queue trajectories |
| `reproduction.reproduce_bounded_markov` | Bounded approximation | `L`, `W`, `Q(b)`, and `P(b)` versus truncation bound |
| `reproduction.reproduce_effect_of_H` | Effect of `H` | `L`, `W`, and `Var[W]` heatmaps over `theta12 x theta21` |
| `reproduction.reproduce_mc_vs_sim` | Validation | Bounded Markov chain vs simulation comparison |
| `reproduction.reproduce_sojourn_variance` | Eq. 13-14 | Sojourn-time variance convergence and heatmap |

## Extensions

| Module | What it adds |
|---|---|
| `reproduction.extension_calibrate_H` | Fine-grid 11x7 calibration of `theta12, theta21` using exploratory `calibration_loss` |

Not yet implemented: full stability-boundary map and non-exponential /
heavy-tailed switching or service-time experiments.

## Quick Start

```bash
# Single script:
.venv\Scripts\python.exe -m reproduction.reproduce_figure5

# All implemented scripts:
.venv\Scripts\python.exe -m reproduction.run_all

# Paper-text and original-notebook parameter variants:
.venv\Scripts\python.exe -m reproduction.run_parameter_variants --dry-run
.venv\Scripts\python.exe -m reproduction.run_parameter_variants --variant both
```

## Common CLI Options

| Flag | Description |
|---|---|
| `--trials` | Number of simulation trials |
| `--seed` | Random seed |
| `--bounds` | Comma-separated bound values for Markov truncation |
| `--arrival-rate` | Poisson arrival rate |
| `--service-rate` | Exponential service rate |
| `--results-dir` | Output directory, default `results/` |

Outputs are written as `.png` figures and `.csv` metric tables to the selected
results directory.

`reproduction.run_parameter_variants` writes conflict-sensitive runs to:

- `results/parameter_variants/paper_text`
- `results/parameter_variants/original_notebook`

By default it runs only scripts with known paper-vs-notebook parameter
conflicts. Add `--include-common` to also run Figure 5 and effect-of-H scripts
once under `results/parameter_variants/common`.

## Metric And Parameter Notes

- `reproduction.reproduce_figure5` reports the two paper metrics separately:
  Wasserstein distance and waiting-time MAPE. It does not rank the paper
  reproduction by a composite loss.
- `reproduction.extension_calibrate_H` is the only script that uses a composite
  `calibration_loss`; this is an exploratory calibration objective, not a
  paper-defined metric.
- Zero switching rates are exact. Simulation scripts pass `None` to Ciw for
  disabled class switching, while Markov-chain scripts use numeric `0.0`.
- Current defaults follow the paper text where it conflicts with notebooks:
  stability uses `theta12=3, theta21=1`; bounded Markov uses `mu2=5/2`.
  To match the original notebooks, pass `--theta12 2 --theta21 1` for the
  stability script and `--service-rate2 1.6666666667` for bounded Markov.
- Existing files in `results/` may be historical outputs from before these
  fixes. Rerun the scripts before using those numbers in a final report.

For quick development runs, you can intentionally reduce the paper-scale
defaults, for example `--bounds 2,3,4`, `--h12-step 0.3 --h21-step 0.3`, or
`--bound 12`. Label those outputs as exploratory rather than final
reproductions.
