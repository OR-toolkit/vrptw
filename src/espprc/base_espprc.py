from abc import ABC
from typing import Dict, Callable, Any
import numpy as np
from .label import Label
from .espprc_instance import ESPPRCBaseProblemData


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
    - Resources under "constant" have fixed bounds across all nodes (e.g., load, reduced_cost).
    - Resources under "node_dependent" vary by node (e.g., time windows).
    - Subclasses should register resource extension functions via `add_ref()`.
    - Label feasibility and dominance are handled generically.
    """

    def __init__(self, problem_data: Any):
        # Support both ESPPRCBaseProblemData instances and raw dict
        if isinstance(problem_data, ESPPRCBaseProblemData):
            self.problem_data = problem_data.to_dict()
        else:
            self.problem_data = problem_data
        self.refs: Dict[
            str, Callable[[Dict[str, np.ndarray], int, int, Dict], np.ndarray]
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
        const = self.problem_data["resource_windows"]["constant"]
        node_dep = self.problem_data["resource_windows"]["node_dependent"]
        # Constant resources: same lower bound for all nodes
        for name, (low, _) in const.items():
            resources[name] = np.array(low, dtype=float)
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
        if "graph" in self.problem_data:
            neighbors = self.problem_data["graph"].get(label.node, [])
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
        const = self.problem_data["resource_windows"]["constant"]
        node_dep = self.problem_data["resource_windows"]["node_dependent"]
        # Constant resources: check against their uniform bounds
        for name, (low, high) in const.items():
            resource = label.resources[name]
            if np.any(resource < low) or np.any(resource > high):
                return False
        # Node-dependent resources: check against per-node window
        for name, (low, high) in node_dep.items():
            node = label.node
            lower, upper = low[node], high[node]
            resource = label.resources[name]
            if np.any(resource < lower) or np.any(resource > upper):
                return False
        return True
