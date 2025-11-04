import numpy as np
from .base_espprc import ESPPRC
from .espprc_instance import ESPPTWCProblemData, ESPPRCBaseProblemData


class ESPPTWC(ESPPRC):
    """Elementary Shortest Path Problem with Time Windows and Capacity (ESPPTWC).

    Accepts problem_data as either a dictionary or an ESPPTWCProblemData object.
    See espprc_instance.py for full data structure.
    """

    def __init__(self, problem_data):
        # Allow direct passing of ESPPTWCProblemData or ESPPRCBaseProblemData
        if isinstance(problem_data, (ESPPTWCProblemData, ESPPRCBaseProblemData)):
            problem_data = problem_data.to_dict()
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
