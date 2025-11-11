import numpy as np

espptwc_test_1 = {
    "num_customers": 3,  # customers 1, 2, 3
    "capacity": 10.0,
    "time_windows": (
        [0.0, 0.0, 0.0, 0.0, 0.0],  # lower bounds
        [100.0, 20.0, 25.0, 40.0, 100.0],  # upper bounds
    ),
    "graph": {
        0: [1, 2, 3],  # start depot can go to any customer
        1: [2, 3, 4],  # customer 1 can go to 2, 3, or end depot
        2: [3, 4],  # customer 2 can go to 3 or end depot
        3: [4],  # customer 3 can only go to depot (end)
        4: [],  # end depot
    },
    "costs": {
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
    "capacity": 10.0,
    "time_windows": (
        [0.0, 5.0, 10.0, 0.0, 0.0],  # lower bounds (used as in original test_2)
        [100.0, 20.0, 25.0, 40.0, 100.0],  # upper bounds
    ),
    "graph": {
        0: [1, 2, 3],
        1: [2, 3, 4],
        2: [3, 4],
        3: [4],
        4: [],
    },
    "costs": {
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
    "capacity": 10.0,
    "time_windows": (
        [0.0, 5.0, 10.0, 0.0, 0.0],  # lower bounds (used as in original test_3)
        [100.0, 20.0, 25.0, 40.0, 100.0],  # upper bounds
    ),
    "graph": {
        0: [1, 2, 3],
        1: [2, 3, 4],
        2: [3, 4],
        3: [4],
        4: [],
    },
    "costs": {
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
    "demands": {
        1: 4.0,
        2: 7.0,
        3: 3.0,
        4: 0.0,
    },
}

# espptwc_test_longest_path: test instance crafted so that the optimal solution is the longest (maximum arc count) feasible path.
espptwc_test_longest_path = {
    "num_customers": 3,  # customers 1, 2, 3
    "capacity": 40.0,
    "time_windows": (
        [0.0, 0.0, 0.0, 0.0, 0.0],  # lower bounds
        [100.0, 20.0, 25.0, 40.0, 100.0],  # upper bounds
    ),
    "graph": {
        0: [1, 2, 3],  # start depot can go to any customer
        1: [2, 3, 4],  # customer 1 can go to 2, 3, or end depot
        2: [3, 4],  # customer 2 can go to 3 or end depot
        3: [4],  # customer 3 can only go to depot (end)
        4: [],  # end depot
    },
    "costs": {
        (0, 1): 3.0,
        (0, 2): 106.0,
        (0, 3): 107.0,
        (1, 2): 2.0,
        (1, 3): 105.0,
        (1, 4): 108.0,
        (2, 3): 1.0,
        (2, 4): 103.0,
        (3, 4): 2.0,
    },
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
    "demands": {
        1: 4.0,
        2: 7.0,
        3: 3.0,
        4: 0.0,  # depot
    },
}
