"""
Benchmark runner for VRPTW problems.
Prepares problem data from Solomon format files for ESPPTWC solving.
"""

import logging
from typing import Tuple, Dict, Any, List
import sys
from pathlib import Path
from datetime import datetime
import gc

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


def solve_and_save_results(
    file_path: str,
    n_customers: int = 25,
    output_dir: str = "./results",
    max_iterations: int = 50,
) -> Dict[str, Any]:
    """
    Solve the column generation problem and save results to a file.

    Parameters
    ----------
    file_path : str
        Path to the Solomon format file
    n_customers : int, optional
        Number of customers to include (default: 25)
    output_dir : str, optional
        Directory to save results (default: "./results")
    max_iterations : int, optional
        Maximum number of column generation iterations (default: 50)

    Returns
    -------
    Dict[str, Any]
        Dictionary containing:
        - 'objective_value': float
        - 'num_vehicles': int
        - 'routes': Dict with variable names, values, and paths
        - 'problem_info': Dict with problem metadata
        - 'arc_filter_ratio': float
    """
    orchestrator = None
    try:
        # Prepare problem data from Solomon format file
        problem_data, ratio_filtered = prepare_problem_data_from_solomon(
            file_path, n_customers
        )

        print("=" * 60)
        print("Final master problem solution:")
        print("=" * 60)

        # Run column generation
        orchestrator = ColumnGenerationOrchestrator(problem_data)
        objective_value, nonzero_results = orchestrator.run(
            max_iterations=max_iterations
        )

        # Display results
        for var_name, (value, path) in nonzero_results.items():
            print(f"Variable: {var_name} | Path: {path} | Value: {value:.2f}")

        num_vehicles = len(nonzero_results)
        print(
            f"Objective value: {objective_value:.2f} | Num of Needed Vehicules: {num_vehicles}"
        )

        # Prepare results dictionary
        results = {
            "objective_value": objective_value,
            "num_vehicles": num_vehicles,
            "routes": {
                var_name: {"value": value, "path": path}
                for var_name, (value, path) in nonzero_results.items()
            },
            "problem_info": {
                "file_path": file_path,
                "num_customers": problem_data.num_customers,
                "capacity": problem_data.capacity,
                "num_arcs": len(problem_data.costs),
                "arc_filter_ratio": ratio_filtered,
                "timestamp": datetime.now().isoformat(),
            },
        }

        # Save results to file
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Generate output filename based on input file
        input_filename = Path(file_path).stem
        output_filename = f"{input_filename}_n{problem_data.num_customers}_results.txt"
        output_path = Path(output_dir) / output_filename

        with open(output_path, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("VRPTW Column Generation Results\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"Problem File: {file_path}\n")
            f.write(f"Number of Customers: {problem_data.num_customers}\n")
            f.write(f"Vehicle Capacity: {problem_data.capacity}\n")
            f.write(f"Number of Arcs: {len(problem_data.costs)}\n")
            f.write(f"Arc Filter Ratio: {ratio_filtered * 100:.1f}%\n")
            f.write(f"Timestamp: {results['problem_info']['timestamp']}\n\n")
            f.write(f"Max iterations: {max_iterations}\n\n")

            f.write("=" * 60 + "\n")
            f.write("Solution\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"Objective Value: {objective_value:.2f}\n")
            f.write(f"Number of Vehicles Needed: {num_vehicles}\n\n")

            f.write("Routes:\n")
            for var_name, route_info in results["routes"].items():
                f.write(
                    f"  {var_name}: {route_info['path']} (value: {route_info['value']:.2f})\n"
                )

            f.write("\n" + "=" * 60 + "\n")

        print(f"\nResults saved to: {output_path}")

        return results

    finally:
        # Explicit cleanup to prevent memory accumulation
        if orchestrator is not None:
            del orchestrator
        # Force garbage collection
        gc.collect()


def benchmark_multiple_files(
    data_dir: str = "./data/solomon/r1",
    file_prefix: str = "r1",
    start_num: int = 1,
    end_num: int = 12,
    n_customers: int = 25,
    output_dir: str = "./results",
    max_iterations: int = 50,
) -> List[Dict[str, Any]]:
    """
    Benchmark multiple Solomon instance files.

    Parameters
    ----------
    data_dir : str, optional
        Directory containing Solomon format files (default: "./data/solomon/r1")
    file_prefix : str, optional
        Prefix for file names (default: "r1")
    start_num : int, optional
        Starting file number (default: 1)
    end_num : int, optional
        Ending file number (default: 12)
    n_customers : int, optional
        Number of customers to include (default: 25)
    output_dir : str, optional
        Directory to save results (default: "./results")
    max_iterations : int, optional
        Maximum number of column generation iterations (default: 50)

    Returns
    -------
    List[Dict[str, Any]]
        List of results dictionaries for each file

    Examples
    --------
    >>> # Benchmark r101.txt through r112.txt
    >>> results = benchmark_multiple_files(
    ...     data_dir="./data/solomon/r1",
    ...     file_prefix="r1",
    ...     start_num=1,
    ...     end_num=12,
    ...     n_customers=25
    ... )
    """
    all_results = []

    print("=" * 60)
    print("Benchmark Multiple Files")
    print("=" * 60)
    print(f"Directory: {data_dir}")
    print(f"Files: {file_prefix}{start_num:02d}.txt to {file_prefix}{end_num:02d}.txt")
    print(f"Number of customers: {n_customers}")
    print(f"Max iterations: {max_iterations}")
    print("=" * 60)
    print()

    for file_num in range(start_num, end_num + 1):
        file_name = f"{file_prefix}{file_num:02d}.txt"
        file_path = str(Path(data_dir) / file_name)

        print(f"\n{'=' * 60}")
        print(f"Processing: {file_name}")
        print(f"{'=' * 60}")

        try:
            # Check if file exists
            if not Path(file_path).exists():
                print(f"File not found: {file_path}")
                print("Skipping...")
                continue

            # Solve and save results
            result = solve_and_save_results(
                file_path=file_path,
                n_customers=n_customers,
                output_dir=output_dir,
                max_iterations=max_iterations,
            )

            all_results.append(result)

            print(f"  Completed: {file_name}")
            print(f"  Objective: {result['objective_value']:.2f}")
            print(f"  Vehicles: {result['num_vehicles']}")

        except Exception as e:
            print(f"✗ Error processing {file_name}: {str(e)}")
            import traceback

            traceback.print_exc()
            continue

    # Summary
    print("\n" + "=" * 60)
    print("Benchmark Summary")
    print("=" * 60)
    print(f"Total files processed: {len(all_results)}/{end_num - start_num + 1}")

    if all_results:
        print("\nResults:")
        print(f"{'File':<15} {'Objective':<12} {'Vehicles':<10}")
        print("-" * 40)
        for result in all_results:
            file_name = Path(result["problem_info"]["file_path"]).name
            obj_val = result["objective_value"]
            num_veh = result["num_vehicles"]
            print(f"{file_name:<15} {obj_val:<12.2f} {num_veh:<10}")

    print("=" * 60)

    return all_results


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )

    problem_data, ratio = prepare_problem_data_from_solomon(
        file_path="./data/solomon/r1/r102.txt", n_customers=5
    )

    print("=" * 60)
    print("Problem Data Prepared Successfully")
    print("=" * 60)
    print(f"Number of customers: {problem_data.num_customers}")
    print(f"Vehicle capacity: {problem_data.capacity}")
    print(f"Time windows: {len(problem_data.time_windows[0])} nodes")
    print(
        f"Number of arcs: {len(problem_data.costs)} ({ratio * 100:.0f}% are filtered)."
    )

    print("\nGraph structure (sample):")
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
    print("Trying on one file:")
    print("=" * 60)
    # Solve and save results
    results = solve_and_save_results(
        file_path="./data/solomon/r1/r102.txt",
        n_customers=5,
        output_dir="./results",
        max_iterations=50,
    )

    benchmark_multiple_files(n_customers=25, start_num=1, max_iterations=50)
