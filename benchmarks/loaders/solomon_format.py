import pandas as pd
from typing import Tuple, Dict, Any


def parse_solomon_format(
    path: str, n_customers: int = 25
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Parse a Solomon (Format Like) VRPTW instance file.

    Returns
    -------
    customers_df : pd.DataFrame
        DataFrame with customer and depot info. Depot duplicated at the end.
        The columns are:
            id   x   y  demand  ready_time  due_date  service_time

        Example of customers_df output (for n_customers=25):

            id   x   y  demand  ready_time  due_date  service_time
        0    0  35  35       0           0       230             0
        1    1  45  68      10          60       120            10
        ...
        25  25  65  20       6         172       182            10
        26  26  35  35       0           0       230             0

        The depot (with id=0) is duplicated at the end with id = n_customers + 1.

    vehicle_info : dict
        Dictionary with {'num_vehicles': int, 'capacity': int}.
    """

    with open(path, "r") as f:
        lines = f.readlines()

    # Vehicle section
    vehicle_line = [line for line in lines if line.strip().startswith("VEHICLE")][0]
    vehicle_idx = lines.index(vehicle_line) + 2  # skip header
    num_vehicles, capacity = map(int, lines[vehicle_idx].split())

    vehicle_info = {"num_vehicles": num_vehicles, "capacity": capacity}

    # Customer section
    customer_line = [line for line in lines if line.strip().startswith("CUSTOMER")][0]
    customer_idx = lines.index(customer_line) + 2  # skip header

    customers = []
    for line in lines[customer_idx:]:
        if line.strip() == "":
            continue
        parts = line.split()
        if len(parts) != 7:  # stop at footer or invalid lines
            continue
        cust_id, x, y, demand, ready, due, service = map(int, parts)
        customers.append(
            {
                "id": cust_id,
                "x": x,
                "y": y,
                "demand": demand,
                "ready_time": ready,
                "due_date": due,
                "service_time": service,
            }
        )

    # Take depot (id=0) + first n_customers
    selected = customers[: n_customers + 1]

    # Duplicate depot at the end with new id (0 is depot at start and 26 is depot at the end)
    depot = selected[0].copy()
    depot["id"] = n_customers + 1
    selected.append(depot)

    customers_df = pd.DataFrame(selected).reset_index(drop=True)
    return customers_df, vehicle_info


if __name__ == "__main__":
    file_path = "./data/solomon/r1/r101.txt"
    customers_df, vehicle_info = parse_solomon_format(file_path, n_customers=25)

    print("Vehicle info:")
    print(vehicle_info)
    print("\nFirst rows of customers:")
    print(customers_df.head())
    print("\nLast rows of customers:")
    print(customers_df.tail())
