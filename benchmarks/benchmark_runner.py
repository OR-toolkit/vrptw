"""
Benchmark runner for VRPTW problems.
Prepares problem data from Solomon format files for ESPPTWC solving.
"""

import logging
from typing import Tuple
import sys
from pathlib import Path

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmarks.loaders.solomon_format import parse_solomon_format
from benchmarks.processors.matrices import (
    compute_cost_matrix,
    compute_travel_time_matrix,
)
from benchmarks.processors.arc_filter import filter_arcs_vrptw
from src.espprc.espprc_data import ESPPTWCProblemData
from src.cg_orchestrator import ColumnGenerationOrchestrator


def prepare_problem_data_from_solomon(
    file_path: str, n_customers: int = 25
) -> Tuple[ESPPTWCProblemData, float]:
    """
    Prepare ESPPTWCProblemData from a Solomon format VRPTW instance file.

    This function:
    1. Parses the Solomon format file
    2. Computes cost and travel time matrices
    3. Filters arcs based on VRPTW constraints
    4. Converts to ESPPTWCProblemData format

    Parameters
    ----------
    file_path : str
        Path to the Solomon format file
    n_customers : int, optional
        Number of customers to include (default: 25)

    Returns
    -------
    ESPPTWCProblemData
        Problem data ready for ESPPTWC solving
    float
        Ratio of arcs filtered out (0.0 to 1.0)

    Examples
    --------
    >>> problem_data, ratio = prepare_problem_data_from_solomon(
    ...     "./data/solomon/r1/r101.txt", n_customers=25
    ... )
    >>> print(f"Filtered {ratio*100:.1f}% of arcs")
    >>> print(f"Number of customers: {problem_data.num_customers}")
    """
    # Step 1: Parse Solomon format file
    customers_df, vehicle_info = parse_solomon_format(file_path, n_customers)

    # Step 2: Extract coordinates and service times
    xs = customers_df["x"].to_numpy()
    ys = customers_df["y"].to_numpy()
    service_times = customers_df["service_time"].to_numpy()

    # Step 3: Compute cost and travel time matrices
    cost_matrix = compute_cost_matrix(xs, ys)
    travel_time_matrix = compute_travel_time_matrix(cost_matrix, service_times)

    # Step 4: Filter arcs based on VRPTW constraints
    filtered_data, ratio_filtered = filter_arcs_vrptw(
        customers_df,
        cost_matrix,
        travel_time_matrix,
        vehicle_info["capacity"],
    )

    # Step 5: Extract time windows
    # time_windows is a tuple of (lower_bounds, upper_bounds)
    # lower_bounds = ready_time, upper_bounds = due_date
    ready_times = customers_df["ready_time"].tolist()
    due_dates = customers_df["due_date"].tolist()
    time_windows = (ready_times, due_dates)

    # Step 6: Extract demands as a dictionary keyed by node id
    demands_dict = {
        int(row["id"]): float(row["demand"]) for _, row in customers_df.iterrows()
    }

    # Step 7: Create ESPPTWCProblemData
    problem_data = ESPPTWCProblemData(
        num_customers=n_customers,
        capacity=float(vehicle_info["capacity"]),
        graph=filtered_data["graph"],
        costs=filtered_data["costs"],
        travel_times=filtered_data["travel_times"],
        demands=demands_dict,
        time_windows=time_windows,
    )

    return problem_data, ratio_filtered


def run_benchmarks_all_r1_files(
    base_dir: str = "./data/solomon/r1",
    n_customers: int = 25,
    max_iterations: int = 100,
    file_range: Tuple[int, int] = (1, 12),
    verbose: bool = False,
) -> dict:
    """
    Run benchmarks for all r1*.txt files in the specified directory.

    This function iterates over files r101.txt through r112.txt (or custom range)
    and runs the column generation algorithm for each file.

    Parameters
    ----------
    base_dir : str, optional
        Base directory containing the Solomon format files (default: "./data/solomon/r1")
    n_customers : int, optional
        Number of customers to include (default: 25)
    max_iterations : int, optional
        Maximum number of CG iterations (default: 50)
    file_range : Tuple[int, int], optional
        Range of file numbers to process, e.g., (1, 12) for r101.txt to r112.txt (default: (1, 12))
    verbose : bool, optional
        If True, print detailed information for each file (default: False)

    Returns
    -------
    dict
        Dictionary with file names as keys and results as values. Each result contains:
            - 'file_path': Path to the file
            - 'objective_value': Final RMP objective value
            - 'num_vehicles': Number of vehicles needed (nonzero variables)
            - 'nonzero_results': Dictionary of nonzero variables with paths
            - 'arc_filter_ratio': Ratio of arcs filtered
            - 'problem_data': The problem data instance used
            - 'success': Boolean indicating if the benchmark ran successfully
            - 'error': Error message if success is False

    Examples
    --------
    >>> results = run_benchmarks_all_r1_files(
    ...     base_dir="./data/solomon/r1",
    ...     n_customers=25,
    ...     max_iterations=50
    ... )
    >>> for file_name, result in results.items():
    ...     if result['success']:
    ...         print(f"{file_name}: Objective = {result['objective_value']:.2f}")
    """
    results = {}
    start_num, end_num = file_range

    for file_num in range(start_num, end_num + 1):
        # Format file number with leading zero (e.g., 01, 02, ..., 12)
        file_name = f"r1{file_num:02d}.txt"
        file_path = Path(base_dir) / file_name

        if not file_path.exists():
            print(f"Warning: File {file_path} does not exist. Skipping...")
            results[file_name] = {
                "file_path": str(file_path),
                "success": False,
                "error": f"File not found: {file_path}",
            }
            continue

        if verbose:
            print("=" * 80)
            print(f"Processing file: {file_name}")
            print("=" * 80)

        try:
            # Prepare problem data
            problem_data, arc_filter_ratio = prepare_problem_data_from_solomon(
                str(file_path), n_customers=n_customers
            )

            if verbose:
                print(f"Number of customers: {problem_data.num_customers}")
                print(f"Vehicle capacity: {problem_data.capacity}")
                print(f"Number of arcs (after filtering): {len(problem_data.costs)}")
                print(f"Ratio of arcs filtered: {arc_filter_ratio * 100:.1f}%")

            # Run column generation
            orchestrator = ColumnGenerationOrchestrator(problem_data)
            if not verbose:
                # Set logging to WARNING level to reduce output
                orchestrator.logger.setLevel(logging.WARNING)
            else:
                orchestrator.logger.setLevel(logging.INFO)

            objective_value, nonzero_results = orchestrator.run(
                max_iterations=max_iterations
            )

            # Store results
            results[file_name] = {
                "file_path": str(file_path),
                "objective_value": objective_value,
                "num_vehicles": len(nonzero_results),
                "nonzero_results": nonzero_results,
                "arc_filter_ratio": arc_filter_ratio,
                "problem_data": problem_data,
                "success": True,
                "error": None,
            }

            if verbose:
                print(f"Objective value: {objective_value:.2f}")
                print(f"Number of vehicles needed: {len(nonzero_results)}")
                print("\nNonzero variables:")
                for var_name, (value, path) in nonzero_results.items():
                    print(f"  {var_name}: Path = {path}, Value = {value:.2f}")
            else:
                print(
                    f"{file_name}: Objective = {objective_value:.2f}, "
                    f"Vehicles = {len(nonzero_results)}, "
                    f"Arc filter = {arc_filter_ratio * 100:.1f}%"
                )

        except Exception as e:
            error_msg = f"Error processing {file_name}: {str(e)}"
            print(f"ERROR: {error_msg}")
            if verbose:
                import traceback

                traceback.print_exc()

            results[file_name] = {
                "file_path": str(file_path),
                "success": False,
                "error": error_msg,
            }

        if verbose:
            print()

    # Print summary
    print("=" * 80)
    print("Benchmark Summary")
    print("=" * 80)
    successful = [r for r in results.values() if r.get("success", False)]
    failed = [r for r in results.values() if not r.get("success", False)]

    print(f"Total files processed: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")


    if successful:
        print("\nSuccessful benchmarks:")
        for file_name, result in results.items():
            if result.get("success", False):
                print(
                    f"  {file_name}: Objective = {result['objective_value']:.2f}, "
                    f"Vehicles = {result['num_vehicles']}"
                )

    if failed:
        print("\nFailed benchmarks:")
        for file_name, result in results.items():
            if not result.get("success", False):
                print(f"  {file_name}: {result.get('error', 'Unknown error')}")

    return results


if __name__ == "__main__":
    # Example usage
    file_path = "./data/solomon/r1/r101.txt"
    problem_data, ratio = prepare_problem_data_from_solomon(file_path, n_customers=25)

    print("=" * 60)
    print("Problem Data Prepared Successfully")
    print("=" * 60)
    print(f"Number of customers: {problem_data.num_customers}")
    print(f"Vehicle capacity: {problem_data.capacity}")
    print(f"Time windows: {len(problem_data.time_windows[0])} nodes")
    print(f">>>Time windows lower bounds: {problem_data.time_windows[0]}")
    print(f">>>Time windows upper bounds: {problem_data.time_windows[1]}")
    print(f"Number of arcs (after filtering): {len(problem_data.costs)}")
    print(f"Ratio of arcs filtered: {ratio * 100:.1f}%")
    for node in sorted(list(problem_data.graph.keys())[:5]):
        print(f"  Node {node}: {problem_data.graph[node]}")
    print("  ...")
    for node in sorted(list(problem_data.graph.keys())[-5:]):
        print(f"  Node {node}: {problem_data.graph[node]}")
    print("\nDemands:")
    for node_id in sorted(problem_data.demands.keys())[:5]:
        print(f"  Node {node_id}: {problem_data.demands[node_id]}")
    print("  ...")
    for node_id in sorted(problem_data.demands.keys())[-5:]:
        print(f"  Node {node_id}: {problem_data.demands[node_id]}")

    print("=" * 60)
    print("Final master problem solution:")
    print("=" * 60)
    # Configure the logger
    orchestrator = ColumnGenerationOrchestrator(problem_data)

    objective_value, nonzero_results = orchestrator.run(max_iterations=50)

    for var_name, (value, path) in nonzero_results.items():
        print(f"Variable: {var_name} | Path: {path} | Value: {value:.2f}")
    print(
        f"Objective value: {objective_value:.2f} | Num of Needed Vehicules: {len(nonzero_results)}"
    )
    print("=" * 60)
    print("Benchmark All Files ")
    print("=" * 60)
    run_benchmarks_all_r1_files()
    
