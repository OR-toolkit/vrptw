import numpy as np


def compute_cost_matrix(xs: np.ndarray, ys: np.ndarray) -> np.ndarray:
    """
    Compute the Euclidean cost (distance) matrix for a set of points.

    Parameters
    ----------
    xs : np.ndarray
        1D array of x-coordinates, shape (n,)
    ys : np.ndarray
        1D array of y-coordinates, shape (n,)

    Returns
    -------
    np.ndarray
        2D array of shape (n, n), where entry [i, j] is the Euclidean distance between points i and j.
        cost_matrix[i, j] = sqrt((xs[i] - xs[j])**2 + (ys[i] - ys[j])**2)
    """
    n = xs.shape[0]
    cost_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            dx = xs[i] - xs[j]
            dy = ys[i] - ys[j]
            cost_matrix[i, j] = np.sqrt(dx**2 + dy**2)
    return cost_matrix


def compute_travel_time_matrix(
    cost_matrix: np.ndarray, service_times: np.ndarray
) -> np.ndarray:
    """
    Compute the travel time matrix for a set of nodes, given the cost matrix and service times.

    Each entry travel_time[i, j] = cost_matrix[i, j] + service_times[i]
    (Service time at the origin node is incurred before departing for j.)

    Parameters
    ----------
    cost_matrix : np.ndarray
        2D array of shape (n, n): cost/distance from node i to node j.
    service_times : np.ndarray
        1D array of shape (n,): service time required at each node.

    Returns
    -------
    np.ndarray
        2D array of shape (n, n), where travel_time[i, j] = cost_matrix[i, j] + service_times[i]
    """
    travel_time_matrix = cost_matrix + service_times.reshape(-1, 1)
    return travel_time_matrix


if __name__ == "__main__":
    from solomon_format import parse_solomon_instance

    file_path = "./data/solomon/r1/r101.txt"
    customers_df, vehicle_info = parse_solomon_instance(file_path, n_customers=25)

    xs = customers_df["x"].to_numpy()
    ys = customers_df["y"].to_numpy()
    service_times = customers_df["service_time"].to_numpy()

    cost_matrix = compute_cost_matrix(xs, ys)
    travel_time_matrix = compute_travel_time_matrix(cost_matrix, service_times)

    print("Vehicle info:")
    print(vehicle_info)

    print("\nCustomers shape:", customers_df.shape)

    shape = cost_matrix.shape
    print(f"\ncost_matrix (shape={shape}):")
    print(cost_matrix[:5, :5])  # print left-top part

    print(f"\ntravel_time_matrix (shape={shape}):")
    print(travel_time_matrix[:5, :5])  # print left-top part
