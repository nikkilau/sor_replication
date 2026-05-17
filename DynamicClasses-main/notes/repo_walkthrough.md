# Repository Walkthrough

## Environment

- Project directory: `DynamicClasses-main`
- Python used for this run: project-local `.venv`
- Original test suite: `28 passed`
- The pinned `numpy==1.24.4` in `requirements.txt` does not provide a wheel for Python 3.12, so the run used compatible current wheels while keeping `ciw==3.0.1`.

## Important source files

- `src/models/models.py`: core Ciw simulation, CTMC state probabilities, absorbing sojourn-time chain, boundary checks, ADF stationarity test.
- `src/Motivating Justification.ipynb`: surgical waiting-list data processing and Figure 5-style overtaking comparison.
- `src/Effect of Parameters.ipynb`: parameter-effect experiments.
- `src/Checks for Steady State Simulation.ipynb`: steady-state and ADF examples.
- `src/motivating_data/Surgery Treatment.csv`: motivating surgical data.

## Added reproducibility layer

- `src/project_reproduction/reproduce_figure5.py`
- `src/project_reproduction/reproduce_stability.py`
- `src/project_reproduction/reproduce_bounded_markov.py`
- `src/project_reproduction/extension_calibrate_H.py`
- `src/project_reproduction/run_all.py`
- `src/project_reproduction/utils.py`

Outputs are written to `results/`.
