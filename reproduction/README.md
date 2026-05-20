# Project Reproduction Scripts

Run from the repo root:

```bash
python reproduction/reproduce_figure5.py
python reproduction/reproduce_stability.py
python reproduction/reproduce_bounded_markov.py
python reproduction/extension_calibrate_H.py

# Or run all at once:
python reproduction/run_all.py
```

Outputs are written to `results/`.

The defaults are intentionally moderate so that they finish on a laptop. Increase
`--bounds`, `--trials`, or the calibration grids for the final presentation run.
