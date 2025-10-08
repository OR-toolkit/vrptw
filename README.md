# VRPTW & Variants Solving Framework

This project addresses the **Vehicle Routing Problem with Time Windows (VRPTW)** and its variants by employing a **Dantzig–Wolfe reformulation** combined with a **column generation approach**. In this context, the **pricing problem** is formulated as an **Elementary Shortest Path Problem with Resource Constraints (ESPPRC)**, which can be efficiently solved using a **labeling algorithm**. This approach is foundational in solving VRPTW and related vehicle routing problems.

---

## Design Overview

The framework is designed to be **modular and extensible**, with a clear separation between:

1. **Problem Abstraction** – The **ESPPRC base class** provides generic methods for label initialization, extension, dominance checking, and feasibility verification.
2. **Problem-Specific Implementations** – Each variant, like **ESPPTWC**, extends the base class and defines **resource extension functions (REFs)** and feasibility rules.
3. **Label Representation** – Partial paths are encapsulated in a **Label class**, which stores the current node, resources, and full path, enabling easy manipulation and comparison.

---

## Project Structure

```
VRPTW/
├── data/                      # Raw and processed datasets
├── assets/                    # Visualizations of problem data
├── data_processing/           # Modules to parse and prepare problem data
│   └── **init**.py
├── espprc/                    # Core ESPPRC framework
│   ├── **init**.py
│   ├── base.py                # Generic ESPPRC base class and Label definition
│   ├── espptwc.py             # ESPPTWC implementation (Time Windows + Capacity)
│   ├── solver.py              # Labeling algorithm implementation
│   ├── problem_data_test.py   # Small test instances for ESPPTWC
├── .gitignore
├── LICENSE
└── README.md
```

---

## Core Components

### 1. ESPPRC Base Class (`espprc/base.py`)

The `ESPPRC` class defines a **generic framework** for solving Elementary Shortest Path Problems with Resource Constraints.  
It handles:
- Generic **label initialization** and **extension** via Resource Extension Functions (REFs)
- **Feasibility checks** for all registered resources
- **Dominance filtering** through the `Label` class
- Unified support for **constant** and **node-dependent** resource windows

#### Expected `problem_data` Structure

```python
   {
      "num_customers": int,
      "resource_windows": {
         "constant": {
               <resource_name>: ([lower_bounds], [upper_bounds]),
               ...
         },
         "node_dependent": {
               <resource_name>: ([lower_i, ..., lower_n], [upper_i, ..., upper_n]),
               ...
         }
      },
      "graph": {i: [neighbors], ...},             # adjacency list
      "reduced_costs": {(i, j): float, ...},      # arc cost or reduced cost
      # Optional problem-specific fields (defined by subclasses)
   }
```
> The following graph illustrates how such a `problem_data` structure translates into an ESPPTWC instance, where nodes, arcs, and resource windows correspond to the defined fields.

![Problem Data Example](./assets/problem_data_2.png)
---

### 2. Label Class (`espprc/label.py`)

The `Label` class represents a **partial path** (state) during the labeling process.

* Stores **current node**, **path**, and a **resource dictionary** (`Dict[str, np.ndarray]`)
* Implements its own **dominance rule** via `dominates(self, other)`
* Supports deep copies of resource vectors for safe propagation

Example structure:

```python
Label(
    node=3,
    resources={"time": np.array([12.0]), "load": np.array([7.0])},
    path=[0, 1, 3]
)
```

---

### 3. ESPPTWC (`espprc/espptwc.py`)

Implements the **Elementary Shortest Path Problem with Time Windows and Capacity** (ESPPTWC).
This subclass registers **problem-specific REFs** for:

* `time` (scalar, respecting node-dependent time windows)
* `load` (vehicle capacity constraint)
* `reduced_cost` (accumulated reduced cost)
* `is_visited` (vector of visited customers)



---

### 4. Labeling Algorithm (`espprc/solver.py`)

Implements a **generic labeling algorithm** to solve ESPPRC instances.

Main steps:

1. Initialize feasible labels at the start depot.
2. Extend labels along feasible arcs.
3. Apply dominance filtering to prune suboptimal labels.
4. Collect non-dominated labels reaching the end depot.

Example usage:

```python
from espprc.espptwc import ESPPTWC
from espprc.problem_data_test import problem_data_test_2
from espprc.solver import labeling_algorithm

if __name__ == "__main__":
    problem = ESPPTWC(problem_data_test_2)
    best_labels = labeling_algorithm(problem)
    print(best_labels)
```

---

## Example Problem Data Tests

Three small **ESPPTWC test instances** are included to validate the labeling algorithm:

* `problem_data_test_1`
* `problem_data_test_2`
* `problem_data_test_3`

Each defines a toy problem with capacity and time window constraints, useful for debugging and algorithm verification.

---

## Data & Benchmarks

The project will later leverage **Solomon benchmark instances** for VRPTW problems:

> M. M. Solomon, *Algorithms for the Vehicle Routing and Scheduling Problems with Time Window Constraints*, Operations Research, 35(2), 1987.

These datasets will be parsed and converted into the above `problem_data` format via the `data_processing` module.

---

## Future Directions

1. **Integration with Column Generation**
   * Use the labeling algorithm within a Dantzig–Wolfe master problem for VRPTW.
2. **Additional ESPPRC Variants**
   * Extend framework to handle stochastic or multi-resource problems.

---

## License

This project is licensed under the **MIT License** – see the [LICENSE](./LICENSE) file for details.
