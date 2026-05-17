# Project Plan: Queues under Stochastic Priority Switching

> Purpose: This document is written for an LLM / coding agent to understand the project goal, reproduce the paper's numerical results, and implement three possible extensions.
>
> Target course project type: read a related academic paper, analyze the stochastic models in the paper, and repeat numerical results.

---

## 0. Project Context

### Course requirement

The course project allows the group to choose an academic paper, analyze its stochastic models, and repeat its numerical results. The final deliverable is a presentation slide deck, not a formal report. The first slide must explicitly outline each group member's specific role.

The project should demonstrate:

- **Consistency**: answer the proposed question of interest.
- **Clarity**: make the modeling logic and results understandable.
- **Relevancy**: use stochastic models from the course, especially queues, CTMCs, Markov chains, and simulation.
- **Interest**: study a nontrivial and meaningful stochastic system.

### Selected paper

Paper: **Queues under stochastic priority switching**  
Authors: Geraint Ian Palmer, Michalis Panayidis, Vincent Knight, Elizabeth Williams  
Journal: *Journal of the Operational Research Society*, 2026

Core topic:

> A generalized `M/M/c` queueing system in which customers belong to multiple priority classes and may randomly switch priority class while waiting in the queue.

The paper develops:

1. A **discrete-event simulation model** using the Ciw Python library.
2. Two **continuous-time Markov chain models**:
   - an ergodic state Markov chain for system-level metrics such as queue length and class composition;
   - an absorbing tagged-customer Markov chain for sojourn-time metrics.
3. A **bounded approximation** for finite numerical computation.
4. A case study on a **surgical endoscopy waiting list** where FIFO does not explain the observed service order.

### Code repository

The source code is available in the file `代码网址.txt` and points to:

```text
https://github.com/geraintpalmer/DynamicClasses
```

Expected useful folders / files after cloning:

```text
DynamicClasses/
  requirements.txt
  src/
    experiments/
    models/
    motivating_data/
    Motivating Justification.ipynb
    Effect of Parameters.ipynb
    Checks for Steady State Simulation.ipynb
```

---

## 1. Core Research Question

Main project question:

> When customers' priority classes change stochastically while they wait, how do the priority-switching matrix, service rates, and arrival rates affect queue stability, queue length, sojourn time, and the ability to reproduce observed non-FIFO service behavior?

More concrete subquestions:

1. Can stochastic priority switching reproduce the observed overtaking behavior in the surgical endoscopy waiting-list data?
2. How do stochastic priority changes affect system stability?
3. How close are the simulation and Markov-chain calculations?
4. Can we improve the paper's numerical calibration of the class-switching matrix `H`?
5. What changes when class-switching times are not exponential?

---

## 2. Model Summary

### 2.1 Queueing system

The paper studies an `M/M/c` queue with `K` customer classes.

Parameters:

- `K`: number of priority classes.
- `c`: number of servers.
- `lambda_k`: arrival rate of class `k` customers.
- `mu_k`: service rate of class `k` customers.
- `h_ij`: rate at which a waiting class `i` customer changes to class `j`.
- `H = (h_ij)`: class-switching matrix.

Priority convention:

- Lower index means higher priority.
- Class `0` has higher priority than class `1`, and so on.
- Customers in the same class are served according to arrival order into that class.

### 2.2 Stochastic priority switching

While a customer waits, their class can change randomly:

```text
class i  --rate h_ij-->  class j
```

Interpretation:

- `h_i,i-1`: direct upgrade rate.
- `h_i,i+1`: direct downgrade rate.
- Other off-diagonal terms: skip-grade transitions.
- Diagonal terms are unused because a customer does not switch to the same class.

### 2.3 Preemptive priority

The paper assumes preemptive priority:

- If a higher-priority customer arrives while all servers are busy, the lowest-priority customer in service may be preempted.
- If a waiting customer upgrades to higher priority than someone currently in service, preemption may also occur.
- Under exponential service times, the Markov chain is equivalent regardless of whether preempted service is resumed, restarted, or resampled, because exponential service is memoryless.

---

## 3. Methods to Reproduce

The project should reproduce both the simulation model and the Markov-chain analysis.

### 3.1 Discrete-event simulation

Use Ciw to simulate:

- Poisson arrivals.
- Exponential service times.
- Exponential class-switching times.
- Preemptive priority.

Important simulation metrics:

- Queue length over time.
- Number of customers by class.
- Sojourn time.
- Waiting time.
- Overtaking / rank-difference distribution.
- Whether the queue appears stable or grows indefinitely.

### 3.2 State Markov chain

State:

```text
s = (s_0, s_1, ..., s_{K-1})
```

where `s_k` is the number of class `k` customers in the system.

Use this CTMC to compute:

- steady-state probability `p_s`;
- expected number of class `k` customers:

```text
L_k = sum_s p_s * s_k
```

- total expected number of customers:

```text
L = sum_k L_k
```

### 3.3 Tagged-customer absorbing Markov chain

Use this Markov chain to compute customer-level statistics:

- mean sojourn time `W`;
- class-specific mean sojourn time `W_k`;
- sojourn-time variance `U`;
- optionally, CDF of sojourn time through a phase-type distribution.

### 3.4 Bounded approximation

The exact state space is infinite. Use a finite bound `b`:

```text
s_k in {0, 1, ..., b}
```

Replicate the bounded approximation and accuracy checks:

- `Q(b)`: relative steady-state probability of hitting the boundary for the ergodic chain.
- `P(b)`: probability that an arriving tagged customer experiences the boundary for the absorbing chain.

Interpretation:

- Smaller `Q(b)` and `P(b)` mean the finite approximation is more reliable.
- Increasing `b` should make the approximation closer to the unbounded system, but the state space grows quickly.

---

## 4. Environment Setup Plan

### 4.1 Clone and install

```bash
# Clone repository
git clone https://github.com/geraintpalmer/DynamicClasses.git
cd DynamicClasses

# Create virtual environment
python -m venv env
source env/bin/activate  # macOS/Linux
# env\Scripts\activate   # Windows PowerShell alternative

# Install dependencies
python -m pip install -r requirements.txt

# Run tests
cd src
python -m pytest .
```

### 4.2 First files to inspect

Inspect these before modifying anything:

```text
src/Motivating Justification.ipynb
src/Effect of Parameters.ipynb
src/Checks for Steady State Simulation.ipynb
src/experiments/main.py
src/models/models.py
src/motivating_data/Surgery Treatment.csv
```

### 4.3 Coding-agent instruction

Do not refactor the entire repository at first. First create a separate reproducibility layer:

```text
src/project_reproduction/
  reproduce_figure5.py
  reproduce_stability.py
  reproduce_bounded_markov.py
  extension_calibrate_H.py
  extension_stability_map.py
  extension_non_exponential_switching.py
  utils.py
  README.md
```

This avoids breaking the original code.

---

## 5. Concrete Reproduction Plan

### Reproduction 1: Surgical endoscopy overtaking distribution

Goal:

> Reproduce the paper's Figure 5: comparison between observed and simulated overtakes under different values of `h12` and `h21`.

Paper setting:

```text
lambda_1 = 0.463
lambda_2 = 0
mu_1 = 0.5
mu_2 = 0.5
c = 1
h12 in {1, 2, 3}
h21 in {0, 1, 2}
simulation horizon = 365 days
number of trials = 5
```

Metrics:

- Overtake / rank-difference distribution.
- Wasserstein distance between actual and simulated overtake distributions.
- MAPE between actual and simulated mean waiting times for bumped-up and bumped-down patients.

Expected original conclusion:

```text
h12 = 3, h21 = 1
```

is the best tested pair among the coarse grid in the paper.

Deliverables:

- One 3-by-3 figure showing observed vs simulated overtakes.
- One table:

```text
h12 | h21 | Wasserstein distance | MAPE | comment
```

- Short explanation of why both downgrades and upgrades are needed.

Success criteria:

- The best or near-best grid point should be close to `(h12, h21) = (3, 1)`.
- The simulated distribution should visually resemble the paper's Figure 5.

---

### Reproduction 2: Stability and queue growth

Goal:

> Reproduce the phenomenon that small changes in class-specific service rates can switch the system from stable behavior to an infinitely growing queue.

Part A: Figure 6-style comparison

Use the endoscopy-inspired setting:

```text
lambda_1 = 0.463
lambda_2 = 0
c = 1
h12 = 3
h21 = 1
```

Compare:

```text
Scenario Stable-like:
  mu_1 = 0.5
  mu_2 = 0.5

Scenario Unstable-like:
  mu_1 = 0.4
  mu_2 = 0.6
```

Deliverable:

- Queue length time-series plot for both scenarios.

Part B: ADF-test stationarity check

The paper uses the Augmented Dickey-Fuller test after converting irregular event-time traces into regular time series.

Implement:

1. Record total number of customers over time.
2. Resample / moving-average onto a regular time grid.
3. Run ADF test.
4. Report p-values.

Suggested output table:

```text
scenario | parameters | ADF p-value | interpreted status
```

Expected behavior:

- Stable system: small p-value, reject non-stationarity.
- Unstable system: large p-value, fail to reject non-stationarity.

---

### Reproduction 3: Bounded Markov-chain approximation

Goal:

> Reproduce the convergence behavior of Figures 7 and 8: as bound `b` increases, Markov-chain estimates approach long-run simulation results.

Paper setting:

```text
K = 2
lambda_1 = 2/3
lambda_2 = 1/3
mu_1 = 3/2
mu_2 = 5/2
h12 = 3
h21 = 1
c = 1
```

Vary:

```text
b = 1, 2, 3, ..., maybe 20
```

Metrics:

- Expected number of class 1 customers, `L_1`.
- Expected number of class 2 customers, `L_2`.
- Total expected number of customers, `L`.
- Mean sojourn time by initial class, `W_1`, `W_2`.
- Overall mean sojourn time, `W`.

Deliverables:

- Plot `L_1`, `L_2`, and `L` versus `b`.
- Plot `W_1`, `W_2`, and `W` versus `b`.
- Optional: overlay long-run simulation benchmarks.
- Table of `Q(b)` and `P(b)` values.

Success criteria:

- The curves should stabilize as `b` grows.
- Larger `b` should reduce boundary-error measures.

---

### Reproduction 4: Effect of class-switching matrix `H`

Goal:

> Reproduce the paper's heatmap-style analysis of how `h12` and `h21` affect class composition and sojourn time.

Use the paper's three scenarios:

```text
Scenario A: prioritized class has slower service
  lambda_1 = 1, lambda_2 = 1, c = 1, mu_1 = 5/2, mu_2 = 7/2

Scenario B: both classes have equal service rate
  lambda_1 = 1, lambda_2 = 1, c = 1, mu_1 = 3, mu_2 = 3

Scenario C: prioritized class has faster service
  lambda_1 = 1, lambda_2 = 1, c = 1, mu_1 = 7/2, mu_2 = 5/2
```

Grid:

```text
h12 in {0, 0.2, 0.4, ..., 3.0}
h21 in {0, 0.2, 0.4, ..., 3.0}
b = 16
```

Metrics:

- `L_1`, `L_2`: average number of customers in each class.
- `W_1`, `W_2`: mean sojourn time by starting class.
- `U`: variance of sojourn time.

Deliverables:

- Heatmaps for `L_1`, `L_2`.
- Heatmaps for `W_1`, `W_2`.
- Heatmap or contour plot for `U`.

Success criteria:

- Trends should match the paper:
  - increasing `h12` tends to move mass from class 1 to class 2;
  - increasing `h21` tends to move mass from class 2 to class 1;
  - the effect on overall queue length depends strongly on whether the high-priority class has faster or slower service.

---

## 6. Three Extensions / Improvements

The project should include all three extensions in the plan. If time is limited, implement Extension 1 fully, Extension 2 partially, and Extension 3 as a focused simulation comparison.

---

### Extension 1: More systematic calibration of `H`

#### Motivation

The original paper uses a coarse grid:

```text
h12 in {1, 2, 3}
h21 in {0, 1, 2}
```

and reports that `(h12, h21) = (3, 1)` is best among those tested. This leaves room for better parameter calibration.

#### Research question

> Can we improve the fit to observed overtaking and waiting-time behavior by using a finer or optimized search over `H`?

#### Objective function

Define:

```text
Loss(h12, h21)
  = alpha * WassersteinDistance(simulated_overtakes, observed_overtakes)
  + beta  * MAPE(simulated_waiting_KPIs, observed_waiting_KPIs)
```

Default:

```text
alpha = 1
beta = 1
```

Also try sensitivity analysis:

```text
(alpha, beta) in {(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)}
```

#### Candidate methods

Implement at least one of the following:

1. Finer grid search:

```text
h12 in [0, 5] with step 0.1 or 0.2
h21 in [0, 5] with step 0.1 or 0.2
```

2. Random search:

```text
sample h12, h21 uniformly from [0, 5]
run N candidates, e.g. N = 100 or 200
```

3. Nelder-Mead / derivative-free optimization:

```text
start from (3, 1)
minimize simulation-based noisy objective
```

Because simulation output is noisy, repeated trials are required for each candidate.

#### Deliverables

- Table comparing:

```text
method | best h12 | best h21 | Wasserstein | MAPE | combined loss
```

- Heatmap of calibration loss over `(h12, h21)`.
- Compare original best `(3, 1)` against improved best.
- Discuss robustness across random seeds.

#### Success criteria

The extension succeeds if it can show at least one of the following:

- a lower loss than the paper's coarse-grid candidate;
- a clear loss basin around the paper's selected `H`;
- evidence that `H` is weakly or strongly identifiable from overtaking data.

---

### Extension 2: Stability boundary map over `H`

#### Motivation

The paper gives a simple stability sufficient/necessary check:

```text
stable if      sum(lambda_i) / (c * min_i mu_i) < 1
unstable if    sum(lambda_i) / (c * max_i mu_i) >= 1
```

But there is a gap region:

```text
c * min_i mu_i <= sum(lambda_i) < c * max_i mu_i
```

In this gap, the class-switching matrix `H` matters. The paper demonstrates this with a few examples. We can make the analysis more systematic.

#### Research question

> For service-rate regimes where the simple traffic-intensity condition is inconclusive, which values of `h12` and `h21` lead to stable or unstable behavior?

#### Experimental design

Use two-class single-server systems:

```text
lambda_1 = 2
lambda_2 = 2
c = 1
```

Compare three service-rate regimes:

```text
Regime A: high-priority class slower
  mu_1 = 3
  mu_2 = 5

Regime B: equal service rates
  mu_1 = 4
  mu_2 = 4

Regime C: high-priority class faster
  mu_1 = 5
  mu_2 = 3
```

Grid:

```text
h12 in [0, 3]
h21 in [0, 3]
step = 0.1 or 0.2
```

For each grid point:

1. Simulate long enough, e.g. `T = 500` or `T = 1000`.
2. Track total queue length over time.
3. Convert irregular trace to regular time series.
4. Apply ADF test.
5. Classify stable / unstable.

Suggested classification:

```text
if ADF p-value < 0.05 and terminal queue length is not too large:
    stable
else:
    unstable or inconclusive
```

Use multiple seeds to reduce false classifications.

#### Deliverables

- Stability heatmap:

```text
x-axis = h12
 y-axis = h21
 color = stable / unstable / inconclusive
```

- ADF p-value heatmap.
- Queue-length example plots for representative stable and unstable points.
- Explanation of why moving customers out of the slow-service class can stabilize the queue.

#### Success criteria

The extension succeeds if it shows a clear region in `H`-space where the queue is stable and another where it is unstable, especially in the inconclusive region of the simple traffic-intensity test.

---

### Extension 3: Non-exponential priority switching

#### Motivation

The Markov-chain model relies on exponential class-switching times because it needs memorylessness. However, the Ciw simulation framework can use more general distributions. This allows the project to test whether memoryless switching is a restrictive assumption.

#### Research question

> How do waiting-time and overtaking behavior change when priority switching is deterministic, Erlang, or Weibull instead of exponential?

#### Experimental design

Use the endoscopy-inspired setting:

```text
lambda_1 = 0.463
lambda_2 = 0
mu_1 = 0.5
mu_2 = 0.5
c = 1
```

Use the calibrated or original switching rates:

```text
h12 = 3
h21 = 1
```

Compare switching-time distributions with matched means:

```text
Exponential(rate = h)
Deterministic(time = 1/h)
Erlang(shape = 2 or 4, mean = 1/h)
Weibull(mean approximately 1/h, choose shape < 1 or > 1)
```

Metrics:

- Mean sojourn time.
- 95th percentile of sojourn time.
- Variance of sojourn time.
- Overtake distribution.
- Wasserstein distance to observed overtakes.
- Fraction of customers who ever switch class.

#### Deliverables

- Boxplot or CDF of sojourn times by switching distribution.
- Table of mean, variance, and 95th percentile.
- Overtake distribution comparison.
- Discussion:
  - deterministic switching may create more regular priority transitions;
  - exponential switching can create more early and very late switches;
  - Weibull with increasing hazard can represent “waiting longer makes upgrade more likely.”

#### Success criteria

The extension succeeds if it shows that the memoryless assumption materially affects at least one KPI, such as tail waiting time, sojourn-time variance, or overtaking distribution.

---

## 7. Suggested Project Timeline

### Phase 1: Reading and model extraction

Tasks:

- Read Sections 1–2 of the paper.
- Write a concise model summary.
- Define all parameters and variables.
- Understand Figure 2 and Figure 3 visually:
  - Figure 2: two-class priority queue example.
  - Figure 3: matrix `H` showing upgrades, downgrades, and skip-grades.

Output:

```text
notes/model_summary.md
```

### Phase 2: Run the repository

Tasks:

- Clone the repo.
- Install dependencies.
- Run tests.
- Run at least one notebook without modification.
- Identify where simulations and Markov models are implemented.

Output:

```text
notes/repo_walkthrough.md
```

### Phase 3: Reproduce core results

Tasks:

- Reproduce Figure 5-style overtaking distribution.
- Reproduce Figure 6-style stable vs unstable queue-size time series.
- Reproduce bounded Markov approximation convergence.

Output:

```text
results/figure5_replication.png
results/stability_replication.png
results/bounded_markov_replication.png
results/replication_metrics.csv
```

### Phase 4: Implement extensions

Tasks:

- Implement improved calibration of `H`.
- Implement stability boundary heatmap.
- Implement non-exponential switching comparison.

Output:

```text
results/extension_calibration_heatmap.png
results/extension_stability_boundary.png
results/extension_non_exponential_switching.png
results/extension_summary.csv
```

### Phase 5: Prepare presentation

Tasks:

- Select the clearest plots.
- Explain stochastic model assumptions.
- Compare original paper results and our extensions.
- Add slide with each member's role.
- Practice presentation to ensure each person participates.

Output:

```text
slides/final_presentation.pptx
```

---

## 8. Final Presentation Structure

Recommended slide deck: 12–15 slides.

### Slide 1: Title and roles

Title:

```text
Queues under Stochastic Priority Switching:
Model Analysis, Numerical Replication, and Extensions
```

Include member roles explicitly:

```text
Member A: paper/model explanation
Member B: simulation reproduction
Member C: Markov-chain reproduction
Member D: extensions and slide integration
Member E: visualization and presentation coordination  # if group has 5 members
```

### Slide 2: Motivation

Main message:

- FIFO is often unrealistic in healthcare queues.
- Patients may become more urgent or less urgent while waiting.
- Unknown service disciplines can sometimes be approximated by stochastic priority switching.

Use surgical endoscopy waiting list as motivating example.

### Slide 3: Basic queueing model

Explain:

```text
M/M/c queue
K priority classes
arrival rates lambda_k
service rates mu_k
class-switching rates h_ij
```

Show a simple two-class diagram.

### Slide 4: Class-switching matrix `H`

Explain:

```text
H = (h_ij)
```

- upgrades;
- downgrades;
- skip-grade transitions;
- why `H` controls priority dynamics.

### Slide 5: Simulation method

Explain:

- Ciw discrete-event simulation.
- Arrival events.
- Service-completion events.
- Class-switching events.
- Preemption events.

Mention why simulation is useful: flexible and can handle non-exponential switching.

### Slide 6: Markov-chain method

Explain the two CTMCs:

1. State Markov chain for queue length and class composition.
2. Tagged-customer absorbing Markov chain for sojourn time.

Mention bounded approximation with finite `b`.

### Slide 7: Replication result 1 — overtaking distribution

Show:

- observed vs simulated overtaking distributions;
- table of Wasserstein distance and MAPE;
- best original grid point near `(h12, h21) = (3, 1)`.

Main takeaway:

> Stochastic priority switching can reproduce non-FIFO overtaking patterns.

### Slide 8: Replication result 2 — stability behavior

Show:

- queue length time series under stable and unstable service-rate scenarios;
- ADF p-values.

Main takeaway:

> Small changes in service rates and class-switching dynamics can change whether the queue stabilizes.

### Slide 9: Replication result 3 — bounded Markov approximation

Show:

- `L_k` and `W_k` versus bound `b`;
- boundary accuracy measures `Q(b)` and/or `P(b)`.

Main takeaway:

> Finite Markov-chain approximations converge as the boundary becomes less relevant.

### Slide 10: Extension 1 — improved calibration of `H`

Show:

- calibration loss heatmap;
- original best `(3, 1)` vs improved best;
- table of metrics.

Main takeaway:

> A more systematic search can improve or validate the paper's coarse-grid estimate of `H`.

### Slide 11: Extension 2 — stability boundary map

Show:

- stable / unstable heatmap over `(h12, h21)`;
- examples of representative stable and unstable trajectories.

Main takeaway:

> In the inconclusive traffic-intensity region, stability depends strongly on the direction and speed of priority switching.

### Slide 12: Extension 3 — non-exponential priority switching

Show:

- comparison of exponential, deterministic, Erlang, and Weibull switching;
- table of mean / variance / 95th percentile of sojourn times.

Main takeaway:

> Memoryless switching is analytically convenient, but non-exponential switching can materially change tail waiting-time behavior.

### Slide 13: Discussion

Discuss:

- what the model captures well;
- what assumptions are strong;
- whether stochastic priority switching is a good proxy for unknown service disciplines;
- why healthcare queue managers might care about variability and tail waiting times.

### Slide 14: Limitations

Mention:

- Real endoscopy scheduling may depend on covariates unavailable in the model.
- Simulation calibration is noisy.
- Markov-chain state space grows quickly with `K` and `b`.
- ADF-based stability classification is empirical, not a proof.
- Non-exponential switching breaks the simple CTMC formulation.

### Slide 15: Conclusion

Final message:

> The paper's stochastic priority-switching model gives a tractable way to represent non-FIFO queueing behavior. We reproduced the main simulation and Markov-chain results, then extended the analysis by improving `H` calibration, mapping stability regions, and testing non-exponential switching assumptions.

---

## 9. Suggested Division of Labor

### Four-person group

| Member | Main responsibility | Concrete outputs |
|---|---|---|
| A | Paper reading and model explanation | Slides 2–4, model summary notes |
| B | Simulation reproduction | Figure 5 and Figure 6 replications |
| C | Markov-chain reproduction | bounded approximation, `L`, `W`, `Q(b)`, `P(b)` |
| D | Extensions and integration | calibration, stability map, non-exponential switching, final slides |

### Five-person group

| Member | Main responsibility | Concrete outputs |
|---|---|---|
| A | Paper motivation and model assumptions | Slides 2–4 |
| B | Ciw simulation and overtaking replication | Slide 7 |
| C | Markov-chain and bounded approximation | Slides 6 and 9 |
| D | Extension experiments | Slides 10–12 |
| E | Visualization, slide design, presentation coordination | polished final deck and rehearsal |

---

## 10. Implementation Checklist for Coding Agent

### Must complete

- [ ] Clone and run original repository.
- [ ] Identify functions/classes for Ciw simulations.
- [ ] Identify functions/classes for Markov-chain calculations.
- [ ] Reproduce endoscopy overtaking distribution.
- [ ] Reproduce stable vs unstable queue-size trajectories.
- [ ] Reproduce bounded Markov approximation convergence.
- [ ] Save all plots under `results/`.
- [ ] Save all metric tables as `.csv`.

### Should complete

- [ ] Implement finer grid search for `H`.
- [ ] Plot calibration loss heatmap.
- [ ] Implement stability boundary map.
- [ ] Implement non-exponential switching comparison.

### Nice to have

- [ ] Add random seeds and confidence intervals.
- [ ] Add a clean command-line interface:

```bash
python src/project_reproduction/reproduce_figure5.py
python src/project_reproduction/reproduce_stability.py
python src/project_reproduction/reproduce_bounded_markov.py
python src/project_reproduction/extension_calibrate_H.py
python src/project_reproduction/extension_stability_map.py
python src/project_reproduction/extension_non_exponential_switching.py
```

- [ ] Create a single script:

```bash
python src/project_reproduction/run_all.py
```

---

## 11. Expected Final Deliverables

```text
results/
  figure5_replication.png
  stability_replication.png
  bounded_markov_replication.png
  effect_of_H_replication.png
  extension_calibration_heatmap.png
  extension_stability_boundary.png
  extension_non_exponential_switching.png
  replication_metrics.csv
  extension_summary.csv

slides/
  final_presentation.pptx

notes/
  model_summary.md
  repo_walkthrough.md
  experiment_log.md
```

---

## 12. Minimal Viable Version

If time is limited, prioritize this version:

1. Explain the model clearly.
2. Reproduce Figure 5-style overtaking results.
3. Reproduce Figure 6-style stable vs unstable behavior.
4. Reproduce one bounded Markov-chain convergence plot.
5. Implement Extension 1 only: improved calibration of `H`.
6. Briefly discuss Extensions 2 and 3 as planned future work.

This is enough to satisfy the course requirement of paper analysis plus numerical replication, while still showing independent thinking.

---

## 13. Strong Version

If time allows, complete:

1. All four reproduction tasks.
2. Full Extension 1 calibration.
3. Full Extension 2 stability boundary heatmap.
4. A compact Extension 3 comparison using matched-mean switching distributions.
5. A polished final deck with clear figures and short explanations.

This version should be a strong course presentation because it combines:

- queueing theory;
- CTMC analysis;
- absorbing Markov chains;
- discrete-event simulation;
- empirical calibration;
- stability investigation;
- sensitivity analysis beyond the original paper.
