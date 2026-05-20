# Model Summary

The paper studies an `M/M/c` priority queue with multiple customer classes. A
lower class index means higher priority. Customers may switch class while
waiting, with transition rate `h_ij` from class `i` to class `j`.

The simulation model uses Ciw with:

- Poisson arrivals by initial class.
- Exponential service times by current class.
- Exponential class-switching times while customers wait.
- Preemptive priority.

The Markov-chain reproduction uses two finite approximations:

- A system-state CTMC over `(s_0, ..., s_{K-1})`, where `s_k` is the number of
  class `k` customers in the system.
- A tagged-customer absorbing CTMC for mean sojourn times.

The finite bound controls tractability. Larger bounds improve accuracy but make
the dense absorbing-chain solve much more expensive.
