import numpy as np


def build_graph(customers_df):
    """Build cost and travel time matrices for a dense graph.

    Notes:
    - Cost is the same as distance, so we only return distance.
    - service time is included in travel time

    Returns
    -------
    dict
        {
            "distance": np.ndarray,
            "travel_time": np.ndarray
        }
    """

    n = len(customers_df)
    cost_matrix = np.zeros((n, n))
    travel_time_matrix = np.zeros((n, n))

    coords = customers_df[["x", "y"]].to_numpy()
    service_times = customers_df["service_time"].to_numpy()

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            dx = coords[i][0] - coords[j][0]
            dy = coords[i][1] - coords[j][1]
            cost = np.sqrt(dx**2 + dy**2)

            cost_matrix[i, j] = cost
            travel_time_matrix[i, j] = cost + service_times[i]

    return {
        "cost": cost_matrix,
        "travel_time": travel_time_matrix,
    }


if __name__ == "__main__":
    from data_processing.parser import parse_solomon_instance
    file_path = "./data/r1/r101.txt"
    customers_df, vehicle_info = parse_solomon_instance(file_path, n_customers=25)
    graph = build_graph(customers_df)

    print("Vehicle info:")
    print(vehicle_info)

    print("\nCustomers shape:", customers_df.shape)
    print("Graph matrices:")
    for key, mat in graph.items():
        print(f"\n{key} matrix (shape={mat.shape}):")
        print(mat[:5, :5])  # print left-top part
