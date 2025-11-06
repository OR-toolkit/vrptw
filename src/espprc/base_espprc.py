from abc import ABC
from typing import Dict, Callable
import numpy as np
from .label import Label
from .problem_data import ESPPRCBaseProblemData


class ESPPRC(ABC):
    """
    Abstract base class for the Elementary Shortest Path Problem with Resource Constraints (ESPPRC).

    This class defines the generic structure and behavior common to all ESPPRC variants,
    including label initialization, extension, and dominance handling.

    A strongly-typed version of the problem data is provided via ESPPRCBaseProblemData (see espprc_instance.py).

    Expected `problem_data` structure:
      - Use ESPPRCBaseProblemData, or ESPPTWCProblemData for ESPPTWC instances.
      - See espprc_instance.py for definitions.
      - If a dict is passed, it must match those data fields.

    Notes:
    - Resources under "constant" have fixed bounds across all nodes (e.g., load, cost).
    - Resources under "node_dependent" vary by node (e.g., time windows).
    - Subclasses should register resource extension functions via `add_ref()`.
    - Label feasibility and dominance are handled generically.
    """

    def __init__(self, problem_data: ESPPRCBaseProblemData):
        # Only dataclass-based problem_data is supported, no conversion to dict
        self.problem_data = problem_data
        self.refs: Dict[
            str, Callable[[Dict[str, np.ndarray], int, int, object], np.ndarray]
        ] = {}

    def add_ref(self, name: str, ref: Callable):
        """Register a resource extension function (REF) for a resource name."""
        self.refs[name] = ref

    def initialize_label(self) -> Label:
        """
        Initialize a label at the depot (`start_node` = 0) with the lower bounds of each resource window.
        The resource window/type structure should follow `BaseResourceWindows` as in espprc_instance.py.
        """
        resources = {}
        start_node = 0
        const = self.problem_data.resource_windows.constant
        node_dep = self.problem_data.resource_windows.node_dependent
        # Constant resources: same lower bound for all nodes
        for name, (low, _) in const.items():
            resources[name] = np.array(low, dtype=float)
            # print(resources[name], name)
        resources["reduced_cost"] = np.array([0], dtype=float)
        # Node-dependent: initialize with lower bound of start node
        for name, (low, _) in node_dep.items():
            resources[name] = np.array([low[start_node]], dtype=float)
        return Label(node=start_node, resources=resources)

    def extend_label(self, label: Label, destination: int) -> Label:
        """
        Create a new label by extending the given label using REFs.
        The new label will have an updated path including the destination node.
        Returns None if (label.node, destination) is not an allowed arc.
        """
        # Use the arc information from the graph (adjacency list)
        neighbors = self.problem_data.graph.get(label.node, [])
        if destination not in neighbors:
            return None
        new_resources = {}
        for name in label.resources:
            new_resources[name] = self.refs[name](
                label.resources, label.node, destination, self.problem_data
            )
        return Label(node=destination, resources=new_resources, path=label.path)

    def check_feasibility(self, label: Label) -> bool:
        """
        Check if all resources on the label are within their bounds
        as specified in the BaseResourceWindows/ESPPRCBaseProblemData.
        Returns True if feasible, False otherwise.
        """
        const = self.problem_data.resource_windows.constant
        node_dep = self.problem_data.resource_windows.node_dependent
        # Constant resources: check against their uniform bounds
        for name, (low, high) in const.items():
            resource = label.resources[name]
            if np.any(resource < low) or np.any(resource > high):
                # DEBUG
                print(f"{name} is {resource} is not between [{low}, {high}]")
                return False
        # Node-dependent resources: check against per-node window
        for name, (low, high) in node_dep.items():
            node = label.node
            lower, upper = low[node], high[node]
            resource = label.resources[name]
            if np.any(resource < lower) or np.any(resource > upper):
                # DEBUG
                print(f"{name} is {resource} is not between [{low}, {high}]")
                return False
        return True

    def adjust_costs(self, dual_values: Dict[int, float]) -> None:
        """
        Adjust the adjusted costs of arcs (i, j) by subtracting the dual value
        associated with the source node i for each arc. The original costs remain unchanged.

        Args:
            dual (Dict[int, float]): A dictionary mapping node/customer indices (int)
                to the dual value corresponding to their covering constraint.

        Updates:
            adjusted_costs[(i, j)] := costs[(i, j)] - dual[i] (if dual[i] exists; if not, uses 0.0).
        """
        for (i, j), cost in self.problem_data.costs.items():
            dual_value = dual_values.get(i, 0.0)
            self.problem_data.adjusted_costs[(i, j)] = cost - dual_value

    def path_cost(self, path):
        """
        Compute the total cost of a route as the sum of arc costs along the label's path.

        Args:
            path:

        Returns:
            float: The total cost of the route corresponding to the label's path.
        """
        if not path or len(path) < 2:
            return 0.0
        return sum(
            self.problem_data.costs[(path[i], path[i + 1])]
            for i in range(len(path) - 1)
        )
