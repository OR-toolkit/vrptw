import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple


def filter_arcs_vrptw(
    customers_df: pd.DataFrame,
    cost_matrix: np.ndarray,
    travel_time_matrix: np.ndarray,
    capacity: float,
) -> Tuple[Dict[str, Any], float]:
    """
    Filter arcs (i, j) for VRPTW feasibility.

    An arc from i to j is infeasible if:
      - j == 0 (cannot return to depot at start)
      - i == last_node (cannot leave depot at end)
      - demand[i] + demand[j] > capacity
      - ready_time[i] + travel_time[i, j] > due_date[j]

    Parameters:
    -------
        customers_df : pd.DataFrame
            DataFrame with customer and depot info. Depot duplicated at the end.
            The columns are:
                id   x   y  demand  ready_time  due_date  service_time

            Example of customers_df output (for n_customers=25):

                id   x   y  demand  ready_time  due_date  service_time
            0    0  35  35       0           0       230             0
            ...
            25  25  65  20       6         172       182            10
            26  26  35  35       0           0       230             0

            The depot (with id=0) is duplicated at the end with id = n_customers + 1.

        cost_matrix: np.ndarray
            A (n, n) array where cost[i, j] is the Euclidean distance from node i to node j.

        travel_time_matrix: np.ndarray
            A (n, n) array where travel_time[i, j] = cost[i, j] + service_time[i].
            This value represents the total time required to depart from node i, service node i, and travel to node j.
    Returns
    -------

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
    from parser import parse_solomon_format
    from matrices import compute_cost_matrix, compute_travel_time_matrix

    file_path = "./data/solomon/r1/r101.txt"
    customers_df, vehicle_info = parse_solomon_format(file_path, n_customers=25)
    xs = customers_df["x"].to_numpy()
    ys = customers_df["y"].to_numpy()
    service_times = customers_df["service_time"].to_numpy()
    cost_matrix = compute_cost_matrix(xs, ys)
    travel_time_matrix = compute_travel_time_matrix(cost_matrix, service_times)

    filtered_graph, ratio = filter_arcs_vrptw(
        customers_df, cost_matrix, travel_time_matrix, vehicle_info["capacity"]
    )

    print("Adjacency list:")
    for k, v in list(filtered_graph["graph"].items())[:]:
        print(f"{k}: {v}")

    print("\nNumber of arcs kept:", len(filtered_graph["costs"]))
    print(f"{100 * ratio:.0f}% of arcs are filtered.")
