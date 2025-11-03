from abc import ABC
from typing import Dict, Callable, Any
import numpy as np
from espprc.label import Label


class ESPPRC(ABC):
    """
    Abstract base class for the Elementary Shortest Path Problem with Resource Constraints (ESPPRC).

    This class defines the generic structure and behavior common to all ESPPRC variants,
    including label initialization, extension, and dominance handling.

    Expected `problem_data` structure:
    {
        "num_customers": int,
        "resource_windows": {
            "constant": {
                <resource_name>: ([lower_bounds], [upper_bounds]),
                ...
            },
            "node_dependent": {
                <resource_name>: ([lower_i, ..., lower_n], [upper_i, ..., upper_n]),
                ...
            }
        },
        "graph": {i: [neighbors], ...},             # adjacency list
        "reduced_costs": {(i, j): float, ...},      # arc cost or reduced cost
        # Optional problem-specific fields (defined by subclasses)
    }

    Notes:
    - Resources under "constant" have fixed bounds across all nodes (e.g., load, reduced_cost).
    - Resources under "node_dependent" vary by node (e.g., time windows).
    - Subclasses should register resource extension functions via `add_ref()`.
    - Label feasibility and dominance are handled generically.
    """

    def __init__(self, problem_data: Dict[str, Any]):
        self.problem_data = problem_data
        self.refs: Dict[
            str, Callable[[Dict[str, np.ndarray], int, int, Dict], np.ndarray]
        ] = {}

    def add_ref(self, name: str, ref: Callable):
        """Register a resource extension function (REF) for a resource name."""
        self.refs[name] = ref

    def initialize_label(self) -> Label:
        """Initialize a label at `start_node` with the lower bounds of each resource window."""
        resources = {}
        start_node = 0
        # Constant resources: same for all nodes
        for name, (low, _) in self.problem_data["resource_windows"]["constant"].items():
            resources[name] = np.array(low, dtype=float)
        # Node-dependent resources: initialize with the lower bound at start_node
        for name, (low, _) in self.problem_data["resource_windows"][
            "node_dependent"
        ].items():
            resources[name] = np.array([low[start_node]], dtype=float)
        return Label(node=start_node, resources=resources)

    def extend_label(self, label: Label, destination: int) -> Label:
        """Create a new label by extending the given label using REFs.
        The new label will have an updated path including the destination node.
        """
        # Check if arc exists in the graph
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
        """Check if all resources are within their bounds."""
        # Constant resources
        for name, (low, high) in self.problem_data["resource_windows"][
            "constant"
        ].items():
            resource = label.resources[name]
            if np.any(resource < low) or np.any(resource > high):
                return False

        # Node-dependent resources
        for name, (low, high) in self.problem_data["resource_windows"][
            "node_dependent"
        ].items():
            node = label.node
            lower, upper = low[node], high[node]
            resource = label.resources[name]
            if np.any(resource < lower) or np.any(resource > upper):
                return False
        return True
