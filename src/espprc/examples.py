import numpy as np
from .espprc_instance import BaseResourceWindows, ESPPTWCProblemData

# DEPRECATED: Raw dict version for reference only.
espptwc_test_1 = {
    "num_customers": 3,  # customers 1, 2, 3
    # ---- Resource windows ----
    "resource_windows": {
        "constant": {
            "reduced_cost": ([0.0], [np.inf]),
            "load": ([0.0], [10.0]),  # vehicle capacity = 10
            "is_visited": ([0.0, 0.0, 0.0, 0.0, 0.0], [1.0, 1.0, 1.0, 1.0, 1.0]),
        },
        "node_dependent": {
            # time windows (lower, upper) for each node (0=start depot, 4=end depot)
            "time": (
                [0.0, 5.0, 10.0, 0.0, 0.0],  # lower bounds
                [100.0, 20.0, 25.0, 40.0, 100.0],  # upper bounds
            )
        },
    },
    # ---- Graph structure ----
    "graph": {
        0: [1, 2, 3],  # start depot can go to any customer
        1: [2, 3, 4],  # customer 1 can go to 2, 3, or end depot
        2: [3, 4],  # customer 2 can go to 3 or end depot
        3: [4],  # customer 3 can only go to depot (end)
        4: [],  # end depot
    },
    # ---- Arc costs ----
    "reduced_costs": {
        (0, 1): 3.0,
        (0, 2): 6.0,
        (0, 3): 7.0,
        (1, 2): 2.0,
        (1, 3): 5.0,
        (1, 4): 8.0,
        (2, 3): 1.0,
        (2, 4): 3.0,
        (3, 4): 2.0,
    },
    # ---- Travel times ----
    "travel_times": {
        (0, 1): 6.0,
        (0, 2): 10.0,
        (0, 3): 12.0,
        (1, 2): 8.0,
        (1, 3): 15.0,
        (1, 4): 5.0,
        (2, 3): 4.0,
        (2, 4): 6.0,
        (3, 4): 5.0,
    },
    # ---- Demands ----
    "demands": {
        1: 4.0,
        2: 7.0,  # makes some routes infeasible (e.g., 1→2→3 exceeds capacity)
        3: 3.0,
        4: 0.0,  # depot
    },
}

# Variant of the previous data with BIGGER reduced cost 0 -> 3
espptwc_test_2 = {
    "num_customers": 3,
    # ---- Resource windows ----
    "resource_windows": {
        "constant": {
            "reduced_cost": ([0.0], [np.inf]),
            "load": ([0.0], [10.0]),
            "is_visited": ([0.0, 0.0, 0.0, 0.0, 0.0], [1.0, 1.0, 1.0, 1.0, 1.0]),
        },
        "node_dependent": {
            "time": (
                [0.0, 5.0, 10.0, 0.0, 0.0],
                [100.0, 20.0, 25.0, 40.0, 100.0],
            )
        },
    },
    # ---- Graph structure ----
    "graph": {
        0: [1, 2, 3],
        1: [2, 3, 4],
        2: [3, 4],
        3: [4],
        4: [],
    },
    # ---- Arc costs ----
    "reduced_costs": {
        (0, 1): 3.0,
        (0, 2): 6.0,
        (0, 3): 10.0,  # BIGGER REDUCED COST
        (1, 2): 2.0,
        (1, 3): 5.0,
        (1, 4): 8.0,
        (2, 3): 1.0,
        (2, 4): 3.0,
        (3, 4): 2.0,
    },
    # ---- Travel times ----
    "travel_times": {
        (0, 1): 6.0,
        (0, 2): 10.0,
        (0, 3): 12.0,
        (1, 2): 8.0,
        (1, 3): 15.0,
        (1, 4): 5.0,
        (2, 3): 4.0,
        (2, 4): 6.0,
        (3, 4): 5.0,
    },
    # ---- Demands ----
    "demands": {
        1: 4.0,
        2: 7.0,
        3: 3.0,
        4: 0.0,
    },
}

# Variant of the previous data with SMALLER reduced cost 0 -> 3
espptwc_test_3 = {
    "num_customers": 3,
    # ---- Resource windows ----
    "resource_windows": {
        "constant": {
            "reduced_cost": ([0.0], [np.inf]),
            "load": ([0.0], [10.0]),
            "is_visited": ([0.0, 0.0, 0.0, 0.0, 0.0], [1.0, 1.0, 1.0, 1.0, 1.0]),
        },
        "node_dependent": {
            "time": (
                [0.0, 5.0, 10.0, 0.0, 0.0],
                [100.0, 20.0, 25.0, 40.0, 100.0],
            )
        },
    },
    # ---- Graph structure ----
    "graph": {
        0: [1, 2, 3],
        1: [2, 3, 4],
        2: [3, 4],
        3: [4],
        4: [],
    },
    # ---- Arc costs ----
    "reduced_costs": {
        (0, 1): 3.0,
        (0, 2): 6.0,
        (0, 3): 2.0,  # SMALLER REDUCED COST
        (1, 2): 2.0,
        (1, 3): 5.0,
        (1, 4): 8.0,
        (2, 3): 1.0,
        (2, 4): 3.0,
        (3, 4): 2.0,
    },
    # ---- Travel times ----
    "travel_times": {
        (0, 1): 6.0,
        (0, 2): 10.0,
        (0, 3): 12.0,
        (1, 2): 8.0,
        (1, 3): 15.0,
        (1, 4): 5.0,
        (2, 3): 4.0,
        (2, 4): 6.0,
        (3, 4): 5.0,
    },
    # ---- Demands ----
    "demands": {
        1: 4.0,
        2: 7.0,
        3: 3.0,
        4: 0.0,
    },
}

# --- Problem instance objects (see @espprc_instance.py) ---

problem_instance_1 = ESPPTWCProblemData(
    num_customers=espptwc_test_1["num_customers"],
    resource_windows=BaseResourceWindows(
        constant=espptwc_test_1["resource_windows"]["constant"],
        node_dependent=espptwc_test_1["resource_windows"]["node_dependent"],
    ),
    graph=espptwc_test_1["graph"],
    reduced_costs=espptwc_test_1["reduced_costs"],
    travel_times=espptwc_test_1["travel_times"],
    demands=espptwc_test_1["demands"],
)

problem_instance_2 = ESPPTWCProblemData(
    num_customers=espptwc_test_2["num_customers"],
    resource_windows=BaseResourceWindows(
        constant=espptwc_test_2["resource_windows"]["constant"],
        node_dependent=espptwc_test_2["resource_windows"]["node_dependent"],
    ),
    graph=espptwc_test_2["graph"],
    reduced_costs=espptwc_test_2["reduced_costs"],
    travel_times=espptwc_test_2["travel_times"],
    demands=espptwc_test_2["demands"],
)

problem_instance_3 = ESPPTWCProblemData(
    num_customers=espptwc_test_3["num_customers"],
    resource_windows=BaseResourceWindows(
        constant=espptwc_test_3["resource_windows"]["constant"],
        node_dependent=espptwc_test_3["resource_windows"]["node_dependent"],
    ),
    graph=espptwc_test_3["graph"],
    reduced_costs=espptwc_test_3["reduced_costs"],
    travel_times=espptwc_test_3["travel_times"],
    demands=espptwc_test_3["demands"],
)


def espptwc_basic_example():
    """
    Example showcasing label extension, feasibility, and dominance checks for ESPPTWCProblemData/ESPPTWC instance.
    """
    from .espptwc import ESPPTWC

    espptwc = ESPPTWC(problem_instance_1)
    depot_label = espptwc.initialize_label()
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

    # Extend from depot to customer 3 (may be infeasible)
    label3 = espptwc.extend_label(depot_label, destination=3)
    if label3:
        print("\nExtended depot label from depot to customer 3:")
        for r, val in label3.resources.items():
            print(f"{r}: {val}")
        print("Path:", label3.path)
    else:
        print("\nDepot extension to customer 3 is infeasible")

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

    # check feasibility
    print("Feasibility (label1):", espptwc.check_feasibility(label1))
    print("Feasibility (label2):", espptwc.check_feasibility(label2))
    print("Feasibility (label13):", espptwc.check_feasibility(label13))
    print("Feasibility (label23):", espptwc.check_feasibility(label23))

    # check dominance
    print("label1 dominates label1:", label1.dominates(label1))
    print("label1 dominates label2:", label1.dominates(label2))
    print("label2 dominates label1:", label2.dominates(label1))


def labeling_algorithm_basic_example():
    """
    Example showing usage of the generic labeling_algorithm and printing the best labels/resources.
    """
    from .espptwc import ESPPTWC
    from .espprc_solver import make_min_resource_selector, labeling_algorithm

    pbdata = espptwc_test_1
    espptwc = ESPPTWC(pbdata)
    min_label_selector = make_min_resource_selector(resource_name="time")
    best_labels = labeling_algorithm(problem=espptwc, label_selector=min_label_selector)
    print(best_labels)
    print("Results:")
    for label in best_labels:
        resources = label.resources
        cost = resources["reduced_cost"][0]
        load = resources["load"][0]
        time = resources["time"][0]
        path = label.path
        print(f"  Cost: {cost}, Load: {load}, Time: {time}, Path: {path}")


if __name__ == "__main__":
    print("--------- espptwc_basic_example ---------")
    espptwc_basic_example()
    print("--------- labeling_algorithm_basic_example ---------")
    labeling_algorithm_basic_example()
