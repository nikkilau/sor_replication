# Results Status

The files in this directory are generated artifacts, not source of truth.

Some CSV and PNG files were produced before the latest reproduction fixes:

- zero switching rates now use exact semantics (`None` for Ciw simulation,
  `0.0` for Markov-chain transition rates);
- Figure 5 reproduction now reports Wasserstein distance and MAPE separately,
  without a composite loss column;
- effect-of-H defaults now match the paper grid (`0.2` steps, bound `16`);
- bounded Markov defaults now expose paper-vs-notebook service-rate choices.

Do not treat the current numeric tables as final reproduction evidence until
the corresponding scripts are rerun. New CSV outputs include their main
parameter settings to make stale or mismatched runs easier to spot.

For final comparison runs, prefer writing parameter variants under:

- `results/parameter_variants/paper_text`
- `results/parameter_variants/original_notebook`
- `results/parameter_variants/common` for scripts without known conflicts

Use `python -m reproduction.run_parameter_variants --dry-run` to inspect the
commands before launching experiments.
