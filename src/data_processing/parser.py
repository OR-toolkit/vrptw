import pandas as pd


def parse_solomon_instance(path: str, n_customers: int = 25):
    """
    Parse a Solomon VRPTW instance file.

    Returns
    customers_df : pd.DataFrame
        DataFrame with customer and depot info. Depot duplicated at the end.
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
    file_path = "./data/r1/r101.txt"
    customers_df, vehicle_info = parse_solomon_instance(file_path, n_customers=25)

    print("Vehicle info:")
    print(vehicle_info)
    print("\nFirst rows of customers:")
    print(customers_df.head())
    print("\nLast rows of customers:")
    print(customers_df.tail())
