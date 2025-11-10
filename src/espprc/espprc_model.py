from abc import ABC
from typing import Dict
import numpy as np
from .label import Label
from .espprc_data import ESPPRCBaseProblemData
from .resource import ResourceDef

class EspprcModel(ABC):
    """
    Abstract base class for the Elementary Shortest Path Problem with Resource Constraints (ESPPRC).

    This class defines the generic structure and behavior common to all ESPPRC variants,
    including label initialization, extension, and dominance handling.

    Subclasses are expected to register resource definitions with register_resource(), 
    using ResourceDef objects as in espptwc_model.py. 
    Resource extension, window checking, and initialization are now driven by these 
    ResourceDef objects (not the older resource_windows/constant model).
    """

    def __init__(self, problem_data: ESPPRCBaseProblemData):
        self.problem_data = problem_data
        self.num_customers = problem_data.num_customers
        self._add_adjusted_costs()
        self.resources: Dict[str, ResourceDef] = {}

    def _add_adjusted_costs(self):
        """
        Initialize adjusted_costs as an identical copy of costs
        """
        self.problem_data.adjusted_costs = dict(self.problem_data.costs)

    def adjust_costs(self, dual_values: Dict[int, float]) -> None:
        """
        Adjust the adjusted costs of arcs (i, j) by subtracting the dual value
        associated with the source node i for each arc. The original costs remain unchanged.

        Args:
            dual_values (Dict[int, float]): A dictionary mapping node/customer indices (int)
                to the dual value corresponding to their covering constraint.

        Updates:
            adjusted_costs[(i, j)] := costs[(i, j)] - dual[i] (if dual[i] exists; if not, uses 0.0).
        """
        for (i, j), cost in self.problem_data.costs.items():
            dual_value = dual_values.get(i, 0.0)
            self.problem_data.adjusted_costs[(i, j)] = cost - dual_value

    def register_resource(self, resource: ResourceDef) -> None:
        """
        Register a ResourceDef object with this model.
        The resource's name is used as the key.
        """
        self.resources[resource.name] = resource

    def initialize_label(self) -> Label:
        """
        Initialize a label at the depot (`start_node` = 0) with the starting value for each resource. 
        If ResourceDef defines `resource_at_start_node`, use it. 
        Otherwise, use the lower bound at the start node or zero if undefined.
        """
        resources = {}
        start_node = 0
        for name, rdef in self.resources.items():
            if hasattr(rdef, "resource_at_start_node") and rdef.resource_at_start_node is not None:
                # Use provided initialization value for the resource
                val = rdef.resource_at_start_node
                # If it is already an array use as is, else wrap as 1-D array
                if isinstance(val, (np.ndarray, list)):
                    resources[name] = np.array(val, dtype=float)
                else:
                    resources[name] = np.array([val], dtype=float)
            elif rdef.windows:
                # windows present, use lower bound for start_node
                low = rdef.get_lower_bound(start_node)
                if isinstance(low, (np.ndarray, list)):
                    resources[name] = np.array(low, dtype=float)
                else:
                    resources[name] = np.array([low], dtype=float)
            else:
                # No windows, no start value: zero vector of length 1 (fallback)
                resources[name] = np.zeros(1, dtype=float)
        return Label(node=start_node, resources=resources)

    def extend_label(self, label: Label, destination: int) -> Label:
        """
        Create a new label by extending the given label using ResourceDefs' extension functions.
        Returns None if (label.node, destination) is not an allowed arc.
        """
        # Use the arc information from the graph (adjacency list)
        neighbors = self.problem_data.graph.get(label.node, [])
        if destination not in neighbors:
            return None
        new_resources = {}
        for name, resource_def in self.resources.items():
            new_resources[name] = resource_def.ref(
                label.resources, label.node, destination, self.problem_data
            )
        return Label(node=destination, resources=new_resources, path=label.path)

    def check_feasibility(self, label: Label) -> bool:
        """
        Check if all registered resources on the label are within their bounds at the current node.
        Returns True if feasible, False otherwise.
        """
        node = label.node
        for name, resource_def in self.resources.items():
            # If no windows, skip (e.g., reduced_cost unlimited)
            if not resource_def.windows:
                continue
            value = label.resources[name]
            # Use the ResourceDef's checking method
            if not resource_def.is_within_bounds(value, node):
                # print(f"[check_feasibility] {name}={value} not within [{resource_def.get_lower_bound(node)}, {resource_def.get_upper_bound(node)}] at node {node}")
                return False
        return True

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
