import numpy as np

problem_data_test_1_depr = {
    "num_customers": 3,
    # Resource windows
    "resource_windows": {
        "constant": {
            "reduced_cost": ([0.0], [np.inf]),
            "load": ([0.0], [15.0]),
            "is_visited": ([0.0, 0.0, 0.0, 0.0], [1.0, 1.0, 1.0, 1.0]),
        },
        "node_dependent": {
            "time": (
                [0.0, 10.0, 0.0, 0.0],  # lower bounds for depot + 3 customers
                [100.0, 50.0, 40.0, 0.0],  # upper bounds
            ),
        },
    },
    # ---- Graph structure ----
    "graph": {
        0: [1, 2],  # depot can go to customer 1 or 2
        1: [3],  # customer 1 can go to 3
        2: [3],  # customer 2 can go to 3
        3: [],  # customer 3 is last (can be depot itself)
    },
    # Arc data
    "reduced_costs": {(0, 1): 2.0, (0, 2): 3.0, (1, 3): 4.0, (2, 3): 1.0},
    "travel_times": {(0, 1): 5.0, (0, 2): 4.0, (1, 3): 6.0, (2, 3): 3.0},
    # Node-specific data
    "demands": {1: 4.0, 2: 6.0, 3: 5.0},
}

problem_data_test_1 = {
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
problem_data_test_2 = {
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
problem_data_test_3 = {
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
