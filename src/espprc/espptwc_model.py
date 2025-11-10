import numpy as np
from typing import Dict
from .espprc_model import EspprcModel
from .resource import ResourceDef
from .espprc_data import ESPPTWCProblemData


class EspptwcModel(EspprcModel):
    """
    ESPPTWC model: sets up standard time, load, is_visited, and reduced_cost resources
    for the Elementary Shortest Path Problem with Time Windows and Capacity.

    Only accepts problem_data as an ESPPTWCProblemData object.

    Resources:
        - reduced_cost: The reduced cost accumulated along the path (no bounds).
        - time: Arrival time at each node, obeying per-node lower/upper bounds from `problem_data.time_windows`.
        - load: Total cumulative load (vehicle capacity), fixed bounds.
        - is_visited: Indicator array for elementary constraint (0/1 per node).
    """

    def __init__(self, problem_data: ESPPTWCProblemData) -> None:
        super().__init__(problem_data)

        self.num_nodes = self.num_customers + 2

        # Reduced cost: no bounds.
        reduced_cost_resource = ResourceDef(
            name="reduced_cost",
            ref=self.ref_reduced_cost,
            initial_resource_at_start=np.array([0]),
            windows=None,
        )

        # Time: per-node bounds provided by problem_data.time_windows (tuple of (lower_bounds, upper_bounds))
        lower_bounds_time, upper_bounds_time = problem_data.time_windows
        time_resource = ResourceDef.from_array_bounds(
            name="time",
            ref=self.ref_time,
            lower_bounds=lower_bounds_time,
            upper_bounds=upper_bounds_time,
        )

        # Load resource: bounds [0, capacity] for all nodes.
        capacity = problem_data.capacity
        load_resource = ResourceDef.from_constant_bounds(
            name="load",
            ref=self.ref_load,
            num_nodes=self.num_nodes,
            lower=[0.0],
            upper=[capacity],
        )

        # is_visited: constant bounds [0, 1] for each node (enforce elementary path).
        visited_resource = ResourceDef.from_constant_bounds(
            name="is_visited",
            ref=self.ref_visited,
            num_nodes=self.num_nodes,
            lower=[0.0] * self.num_nodes,
            upper=[1.0] * self.num_nodes,
        )

        self.register_resource(reduced_cost_resource)
        self.register_resource(time_resource)
        self.register_resource(load_resource)
        self.register_resource(visited_resource)

    def ref_reduced_cost(
        self,
        current_resources: Dict[str, np.ndarray],
        current_node: int,
        dest: int,
        problem_data: ESPPTWCProblemData,
    ) -> np.ndarray:
        """
        Resource extension for reduced cost: accumulate arc cost.

        Args:
            current_resources: Current resource dictionary.
            current_node: Index of the node being extended from.
            dest: Index of the node being extended to.
            problem_data: The ESPPTWCProblemData instance.

        Returns:
            np.ndarray: Updated reduced cost as np.array([value]).
        """
        new_reduced_cost = (
            current_resources["reduced_cost"]
            + problem_data.adjusted_costs[(current_node, dest)]
        )

        return new_reduced_cost

    def ref_time(
        self,
        current_resources: Dict[str, np.ndarray],
        current_node: int,
        dest: int,
        problem_data: ESPPTWCProblemData,
    ) -> np.ndarray:
        """
        Resource extension for time: adds travel time, waits for earliest time window if arriving early.

        Args:
            current_resources: Current resource dictionary.
            current_node: Index of the node being extended from.
            dest: Index of the node being extended to.
            problem_data: The ESPPTWCProblemData instance.

        Returns:
            np.ndarray: Updated time as np.array([value]).
        """
        travel_time = problem_data.travel_times[(current_node, dest)]
        arrival = current_resources["time"][0] + travel_time
        lower_bounds, _ = problem_data.time_windows
        arrival = max(arrival, lower_bounds[dest])
        return np.array([arrival], dtype=float)

    def ref_load(
        self,
        current_resources: Dict[str, np.ndarray],
        current_node: int,
        dest: int,
        problem_data: ESPPTWCProblemData,
    ) -> np.ndarray:
        """
        Resource extension for load: adds demand at destination node.

        Args:
            current_resources: Current resource dictionary.
            current_node: Index of the node being extended from.
            dest: Index of the node being extended to.
            problem_data: The ESPPTWCProblemData instance.

        Returns:
            np.ndarray: Updated load as np.array([value]).
        """
        return current_resources["load"] + problem_data.demands[dest]

    def ref_visited(
        self,
        current_resources: Dict[str, np.ndarray],
        current_node: int,
        dest: int,
        problem_data: ESPPTWCProblemData,
    ) -> np.ndarray:
        """
        Resource extension for the elementary constraint: marks 'dest' as visited.

        Args:
            current_resources: Current resource dictionary.
            current_node: Index of the node being extended from.
            dest: Index of the node being extended to.
            problem_data: The ESPPTWCProblemData instance.

        Returns:
            np.ndarray: Updated is_visited vector.
        """
        is_visited = current_resources["is_visited"].copy()
        print(is_visited)
        is_visited[dest] = 1.0
        return is_visited
