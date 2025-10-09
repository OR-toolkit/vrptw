from typing import Dict, Any
import numpy as np
from espprc.base import ESPPRC


class ESPPTWC(ESPPRC):
    """Elementary Shortest Path Problem with Time Windows and Capacity (ESPPTWC).

    Expected problem_data structure:
    (I will tackle this data parsing in another package)

    {
        "num_customers": int,
        "resource_windows": {
            "constant": {
                "load": ([0.0], [vehicle_capacity]),
                "is_visited": ([0.0, ..., 0.0], [1.0, ..., 1.0]),
                "reduced_cost": ([0.0], [np.inf])
            },
            "node_dependent": {
                "time": ([lower_0, ..., lower_n], [upper_0, ..., upper_n])
            }
        },
        "graph": {i: [neighbors], ...},
        "reduced_costs": {(i, j): float, ...},
        "travel_times": {(i, j): float, ...},
        "demands": {i: float, ...}
    }
    """

    def __init__(self, problem_data: Dict[str, Any]):
        super().__init__(problem_data)

        # Register REFs
        self.add_ref("reduced_cost", self.ref_reduced_cost)
        self.add_ref("time", self.ref_time)
        self.add_ref("load", self.ref_load)
        self.add_ref("is_visited", self.ref_visited)

    def ref_reduced_cost(self, label_resources, current_node, dest, problem_data):
        """Extend reduced cost along arc (current_node, dest)."""
        return (
            label_resources["reduced_cost"]
            + problem_data["reduced_costs"][(current_node, dest)]
        )

    def ref_time(self, label_resources, current_node, dest, problem_data):
        """
        Extend time resource considering travel times and destination time window.
        Can also use other resources (e.g., load, reduced_cost) if needed.
        """
        travel_time = problem_data["travel_times"][(current_node, dest)]
        arrival = label_resources["time"][0] + travel_time

        # Wait until lower bound at destination node
        lower_bounds, _ = problem_data["resource_windows"]["node_dependent"]["time"]
        arrival = max(arrival, lower_bounds[dest])

        return np.array([arrival], dtype=float)

    def ref_load(self, label_resources, current_node, dest, problem_data):
        """Add demand of destination to current load."""
        return label_resources["load"] + problem_data["demands"][dest]

    def ref_visited(self, label_resources, current_node, dest, problem_data):
        """Mark destination as visited."""
        new_resource = label_resources["is_visited"].copy()
        new_resource[dest] = 1
        return new_resource


if __name__ == "__main__":
    from espprc.problem_data_test import problem_data_test_1

    problem_data = problem_data_test_1

    # Create ESPPTWC instance
    espptwc = ESPPTWC(problem_data)

    # Initialize label at depot node 0
    depot_label = espptwc.initialize_label(start_node=0)

    print("Initial depot label resources:")
    for r, val in depot_label.resources.items():
        print(f"{r}: {val}")
    print("Path:", depot_label.path)

    # Extend from depot to customer 1
    label1 = espptwc.extend_label(depot_label, destination=1)
    if label1:
        print("\nExtended label to customer 1:")
        for r, val in label1.resources.items():
            print(f"{r}: {val}")
        print("Path:", label1.path)
    else:
        print("\nExtension to customer 1 is infeasible")

    # Extend from depot to customer 2
    label2 = espptwc.extend_label(depot_label, destination=2)
    if label2:
        print("\nExtended label to customer 2:")
        for r, val in label2.resources.items():
            print(f"{r}: {val}")
        print("Path:", label2.path)
    else:
        print("\nExtension from depot to customer 2 is infeasible")

    # Extend from depot to customer 3 (infeasible)
    label3 = espptwc.extend_label(depot_label, destination=3)
    if label3:
        print("\nExtended depot label from depot to customer 3:")
        for r, val in label3.resources.items():
            print(f"{r}: {val}")
        print("Path:", label2.path)
    else:
        print("\n depot extension to customer 3 is infeasible")

    # Extend from label1 to customer 3
    label13 = espptwc.extend_label(label1, destination=3)
    if label13:
        print("\nExtended label1 to customer 3:")
        for r, val in label13.resources.items():
            print(f"{r}: {val}")
        print("Path:", label13.path)
    else:
        print("\nExtension to customer 3 is infeasible from label1")

    # Extend from label2 to customer 3
    label23 = espptwc.extend_label(label2, destination=3)
    if label23:
        print("\nExtended label2 to customer 3:")
        for r, val in label23.resources.items():
            print(f"{r}: {val}")
        print("Path:", label23.path)
    else:
        print("\nExtension to customer 3 is infeasible from label2")

    # chceck feasibility
    print(espptwc.check_feasibility(label1))
    print(espptwc.check_feasibility(label2))
    print(espptwc.check_feasibility(label13))
    print(espptwc.check_feasibility(label23))

    # check dominance
    print(label1.dominates(label1))
    print(label1.dominates(label2))
    print(label2.dominates(label1))
