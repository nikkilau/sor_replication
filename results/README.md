# Results Directory

The files in this directory are generated artifacts, not source of truth.

## Directory structure

```
results/
├── parameter_variants/       # Authoritative outputs by parameter variant
│   ├── common/               # Experiments without paper/notebook conflicts
│   ├── paper_text/           # Runs using paper-text parameters
│   └── original_notebook/    # Runs using original-notebook parameters
└── extension_calibration/    # Fine-grid calibration extension
```

Earlier (pre-fix) outputs have been moved to `legacy_results/` at the repo root.

## Important notes

- zero switching rates now use exact semantics (`None` for Ciw simulation,
  `0.0` for Markov-chain transition rates);
- Figure 5 reproduction now reports Wasserstein distance and MAPE separately,
  without a composite loss column;
- effect-of-H defaults now match the paper grid (`0.2` steps, bound `16`);
- bounded Markov defaults now expose paper-vs-notebook service-rate choices.

Use `python -m reproduction.run_parameter_variants --dry-run` to inspect the
commands before launching experiments.
