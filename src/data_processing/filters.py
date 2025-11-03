import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple


def filter_arcs_vrptw(
    customers_df: pd.DataFrame,
    graph: Dict[str, np.ndarray],  # matrix form
    capacity: float
) -> Tuple[Dict[str, Any], float]:
    """
    Filter arcs (i, j) for VRPTW feasibility.

    An arc from i to j is infeasible if:
      - j == 0 (cannot return to depot at start)
      - i == last_node (cannot leave depot at end)
      - demand[i] + demand[j] > capacity
      - ready_time[i] + travel_time[i, j] > due_date[j]

    Returns
    result : dict
        {
            "graph": adjacency list (dict of lists),
            "costs": dict of (i, j) -> cost,
            "travel_times": dict of (i, j) -> travel_time,
        }
    ratio_filtered : float
        Percentage of arcs removed.
    """

    n = len(customers_df)
    last_node = n - 1

    demands = customers_df["demand"].to_numpy()
    ready_times = customers_df["ready_time"].to_numpy()
    due_dates = customers_df["due_date"].to_numpy()

    cost_matrix = graph["cost"]
    travel_time_matrix = graph["travel_time"]

    adjacency_list = {i: [] for i in range(n)}
    costs = {}
    travel_times = {}

    total_arcs = 0
    kept_arcs = 0

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            total_arcs += 1

            # Depot constraints
            if j == 0:  # cannot go to depot at start
                continue
            if i == last_node:  # cannot leave depot at end
                continue

            # Capacity constraint
            if demands[i] + demands[j] > capacity:
                continue

            # Time window constraint
            if ready_times[i] + travel_time_matrix[i, j] > due_dates[j]:
                continue

            # Keep feasible arc
            adjacency_list[i].append(j)
            costs[(i, j)] = cost_matrix[i, j]
            travel_times[(i, j)] = travel_time_matrix[i, j]
            kept_arcs += 1

    ratio_filtered = 1 - kept_arcs / total_arcs if total_arcs > 0 else 0

    return {
        "graph": adjacency_list,
        "costs": costs,
        "travel_times": travel_times,
    }, ratio_filtered


if __name__ == "__main__":
    from data_processing.parser import parse_solomon_instance
    from data_processing.graph import build_graph

    file_path = "./data/r1/r101.txt"
    customers_df, vehicle_info = parse_solomon_instance(file_path, n_customers=25)
    graph = build_graph(customers_df)

    filtered_graph, ratio = filter_arcs_vrptw(customers_df, graph, vehicle_info["capacity"])

    print("Adjacency list:")
    for k, v in list(filtered_graph["graph"].items())[:]:
        print(f"{k}: {v}")

    print("\nNumber of arcs kept:", len(filtered_graph["costs"]))
    print("Ratio filtered:", ratio)
