# Project Reproduction Scripts

Run from `DynamicClasses-main/src` with the project virtual environment:

```powershell
..\.venv\Scripts\python.exe project_reproduction\reproduce_figure5.py
..\.venv\Scripts\python.exe project_reproduction\reproduce_stability.py
..\.venv\Scripts\python.exe project_reproduction\reproduce_bounded_markov.py
..\.venv\Scripts\python.exe project_reproduction\extension_calibrate_H.py
```

Outputs are written to `DynamicClasses-main/results`.

The defaults are intentionally moderate so that they finish on a laptop. Increase
`--bounds`, `--trials`, or the calibration grids for the final presentation run.
