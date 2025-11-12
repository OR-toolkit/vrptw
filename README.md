# VRPTW & Variants Solving Framework

This project addresses the **Vehicle Routing Problem with Time Windows (VRPTW)** and its variants by employing a **Dantzig–Wolfe reformulation** combined with a **column generation approach**. The **pricing problem** is formulated as an **Elementary Shortest Path Problem with Resource Constraints (ESPPRC)**, solved efficiently using a **labeling algorithm**. This approach is foundational for solving VRPTW and related vehicle routing problems.

---

## Design Philosophy

The framework is designed with **modularity, extensibility, and separation of concerns** as core principles:

1. **Problem Data vs. Modeling** – Problem data (customers, time windows, demands) is kept separate from modeling decisions (how to represent constraints as resources). This separation enables experimentation with different formulations of the same problem.

2. **Generic ESPPRC Framework** – The base `ESPPRC` class provides reusable infrastructure for label-based algorithms, while subclasses (e.g., `ESPPTWC`) define problem-specific resource extension functions and feasibility rules.

3. **Solver Abstraction** – A generic solver interface allows seamless integration with different LP/MIP solvers (currently CPLEX, extensible to Gurobi, HiGHS, etc.).

4. **Benchmarking Pipeline** – A dedicated benchmarking infrastructure handles parsing standard instances (e.g., Solomon), preprocessing data, and running experiments in a reproducible manner.

---

## Project Structure

```
VRPTW/
├── src/                                  # Core solver package
│   ├── cg_orchestrator.py                # Column generation orchestrator
│   ├── model.py                          # High-level model interface
│   ├── espprc/                           # ESPPRC framework
│   │   ├── espprc_data.py                # Problem data structures
│   │   ├── espprc_model.py               # Base ESPPRC model class
│   │   ├── espptwc_model.py              # VRPTW-specific implementation
│   │   ├── espprc_solver.py              # Labeling algorithm
│   │   ├── label.py                      # Label representation
│   │   ├── resource.py                   # Resource definitions
│   │   ├── examples.py                   # Example instances
│   │   └── README.md                     # Detailed ESPPRC documentation
│   ├── restricted_master_problems/       # Master problem formulations
│   │   ├── set_covering.py               # Set covering RMP
│   │   └── examples.py
│   └── solvers/                          # LP/MIP solver abstractions
│       ├── base_solver.py                # Abstract solver interface
│       ├── cplex_solver.py               # CPLEX implementation
│       └── examples.py
├── benchmarks/                           # Benchmarking infrastructure
│   ├── loaders/                          # Instance file parsers
│   │   └── solomon_format.py             # Solomon VRPTW format parser
│   ├── processors/                       # Data preprocessing
│   │   ├── matrices.py                   # Cost/travel time matrix computation
│   │   └── arc_filter.py                 # Graph arc feasibility filtering
│   └── benchmark_runner.py               # Benchmark execution orchestrator
├── results/                              # Benchmarking results
├── data/                                 # Raw benchmark instances
│   └── solomon/                          # Solomon VRPTW instances
├── assets/                               # Documentation figures
├── environment.yml                       # Conda environment specification
├── LICENSE
└── README.md
```

> **Navigation:** See [`src/README.md`](src/README.md) for column generation workflow details and [`src/espprc/README.md`](src/espprc/README.md) for labeling algorithm explanation with diagrams.

---

## Core Components

### 1. ESPPRC Framework (`src/espprc/`)

The ESPPRC package provides a **generic, extensible framework** for solving Elementary Shortest Path Problems with Resource Constraints.

#### Architecture

**Problem Data Layer** (`espprc_data.py`)
- `ESPPRCProblemData`: Pure problem data (graph structure, arc costs, number of nodes)
- Agnostic to modeling decisions; describes only what the problem statement provides

**Modeling Layer** (`espprc_model.py`)
- `ESPPRC`: Abstract base class that transforms problem data into a solvable model
- Defines resources, resource windows, and resource extension functions (REFs)
- Handles label extension, feasibility checking, and dominance filtering

**Problem-Specific Models** (`espptwc_model.py`)
- `ESPPTWC`: Implements VRPTW-specific modeling choices
- Defines time, load, cost, and elementarity resources
- Registers appropriate REFs for each resource

**Label Representation** (`label.py`)
- `Label`: Encapsulates a partial path with current node, resource values, and path history
- Implements dominance checking between labels

**Solver** (`espprc_solver.py`)
- `LabelingSolver`: Implements the labeling algorithm with multiple label selection strategies
- Returns optimal or improving paths for column generation

#### Example Usage

```python
from src.espprc.espptwc_model import ESPPTWC
from src.espprc.espprc_data import ESPPTWCProblemData
from src.espprc.espprc_solver import LabelingSolver

# Define problem data
problem_data = ESPPTWCProblemData(
    num_customers=25,
    graph={0: [1, 2, 3], ...},
    costs={(0, 1): 5.0, ...},
    travel_times={(0, 1): 10.0, ...},
    demands={1: 7, 2: 5, ...},
    time_windows=[(0, 100), (10, 50), ...],
    vehicle_capacity=100
)

# Create model (builds resources and REFs internally)
model = ESPPTWC(problem_data)

# Solve using labeling algorithm
solver = LabelingSolver(model)
best_labels, best_cost = solver.solve()
```

### 2. Column Generation Orchestrator (`src/cg_orchestrator.py`)

The `ColumnGenerationOrchestrator` implements the complete Dantzig–Wolfe decomposition workflow:

1. **Initialize** restricted master problem (RMP) as a set covering formulation
2. **Iterate:**
   - Solve RMP to obtain dual values
   - Update arc costs with dual information
   - Solve pricing problem (ESPPRC) to find improving columns
   - Add new columns (routes) to RMP
3. **Terminate** when no negative reduced cost columns exist

**Key Features:**
- Modular interface to LP/MIP solvers via `base_solver.py`
- Configurable convergence criteria and iteration limits
- Integration with any ESPPRC variant

```python
from src.cg_orchestrator import ColumnGenerationOrchestrator

orchestrator = ColumnGenerationOrchestrator(problem_data)
objective, routes = orchestrator.run(max_iterations=100, tolerance=1e-6)
```

### 3. Solver Abstractions (`src/solvers/`)

**Abstract Interface** (`base_solver.py`)
- Defines common operations: add variables, add constraints, set objective, solve
- Enables solver-agnostic algorithm implementation

**CPLEX Implementation** (`cplex_solver.py`)
- Concrete implementation using IBM CPLEX
- Supports both continuous relaxation and integer programming

**Extensibility:** Additional solvers (Gurobi, HiGHS, SCIP) can be added by implementing the `BaseSolver` interface.

---

## Benchmarking Infrastructure

The `benchmarks/` module provides a reproducible pipeline for evaluating the solver on standard instances.

### Architecture

```
Raw Instance Files (Solomon format)
        ↓ [loaders/solomon_format.py]
Parsed Data (coordinates, demands, time windows)
        ↓ [processors/matrices.py]
Cost & Travel Time Matrices
        ↓ [processors/arc_filter.py]
Feasible Graph (time window and capacity filtering)
        ↓ [Convert to ESPPRCProblemData]
Solver Input Format
        ↓ [benchmark_runner.py]
Results (objective, computation time, routes)
```

### Components

**Loaders** (`benchmarks/loaders/`)
- Parse standard benchmark file formats
- `solomon_format.py`: Handles Solomon VRPTW instances (C1, C2, R1, R2, RC1, RC2)
- Outputs: NumPy arrays of coordinates, demands, time windows, service times

**Processors** (`benchmarks/processors/`)
- `matrices.py`: Computes Euclidean cost and travel time matrices from coordinates
- `arc_filter.py`: Pre-filters infeasible arcs based on time windows and capacity constraints
- Reduces graph density for improved performance

**Runner** (`benchmarks/benchmark_runner.py`)
- Orchestrates the complete benchmark workflow
- Handles multiple instances, timeout management, and result collection
- Exports results in structured format for analysis

### Usage Example

```python
from benchmarks.loaders.solomon_format import parse_solomon_format
from benchmarks.processors.matrices import compute_cost_matrix, compute_travel_time_matrix
from benchmarks.processors.arc_filter import filter_arcs_vrptw

# Parse Solomon instance
customers_df, vehicle_info = parse_solomon_format("data/solomon/r101.txt")

# Build matrices
xs, ys = customers_df['x'].values, customers_df['y'].values
cost_matrix = compute_cost_matrix(xs, ys)
travel_time_matrix = compute_travel_time_matrix(cost_matrix, customers_df['service_time'].values)

# Filter infeasible arcs
graph_data, filter_ratio = filter_arcs_vrptw(
    customers_df, cost_matrix, travel_time_matrix, vehicle_info['capacity']
)

# Convert to solver format and solve
# ... (create ESPPTWCProblemData and run orchestrator)
```

---

## Data & Benchmarks

The project uses **Solomon benchmark instances** for VRPTW validation:

> M. M. Solomon, *Algorithms for the Vehicle Routing and Scheduling Problems with Time Window Constraints*, Operations Research, 35(2), 1987.

**Instance Categories:**
- **R1, R2**: Randomly distributed customers (tight vs. wide time windows)
- **C1, C2**: Clustered customers (tight vs. wide time windows)
- **RC1, RC2**: Mixed random-clustered distribution

Instances are stored in `data/solomon/` and processed via the benchmarking pipeline.

---

## References

- Desrosiers, J., Lübbecke, M., Desaulniers, G., & Gauthier, J. B. (2024). Branch-and-Price. Springer. ISBN: 978-3-031-96916-4. [Chapter 5: Vehicle Routing and Crew Scheduling Problems, pp. 291-338]

---

## License

This project is licensed under the **MIT License** – see the [LICENSE](./LICENSE) file for details.

---

## Acknowledgments

This work is part of ongoing PhD research in combinatorial optimization and column generation methods for vehicle routing problems.
