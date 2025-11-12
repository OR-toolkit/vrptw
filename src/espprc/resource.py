from typing import Callable, Any, List, Tuple, Dict, Optional
import numpy as np
from .espprc_data import ESPPRCBaseProblemData


class ResourceDef:
    """
    Represents a resource definition for ESPPRC models.

    Attributes:
        name (str): Resource name, e.g., 'time', 'load'.
        ref (Callable): Resource extension function:
            (resources: Dict[str, np.ndarray], current_node: int, dest: int, problem_data: Any) -> np.ndarray
        windows (Tuple[np.ndarray, np.ndarray]): Tuple of (lower_bounds, upper_bounds), both are np.ndarray of shape [num_nodes, resource_dim]
        initial_resource_at_start (np.ndarray): Initial value for the resource at start node as np.ndarray.
    """

    def __init__(
        self,
        name: str,
        ref: Callable[
            [Dict[str, np.ndarray], int, int, ESPPRCBaseProblemData], np.ndarray
        ],
        windows: Optional[Tuple[np.ndarray, np.ndarray]] = None,
        initial_resource_at_start: Optional[np.ndarray] = None,
    ) -> None:
        self.name = name
        self.ref = ref
        self.windows = (
            windows  # (lower, upper), each shape [num_nodes, resource_dim] or None
        )
        self.resource_dim: int

        if initial_resource_at_start is not None:
            self.initial_resource_at_start = initial_resource_at_start
        elif self.windows is not None:
            # Use lower bound at node 0 by default
            self.initial_resource_at_start = self.get_lower_bound(0)
        else:
            self.initial_resource_at_start = np.zeros(1, dtype=float)

    @classmethod
    def from_constant_bounds(
        cls,
        name: str,
        ref: Callable[[Dict[str, np.ndarray], int, int, Any], np.ndarray],
        num_nodes: int,
        lower: List,
        upper: List,
        initial_resource_at_start: Optional[np.ndarray] = None,
    ) -> "ResourceDef":
        """
        Creates a ResourceDef with constant time/load windows across all nodes.
        All bounds are  (shape [num_nodes][resource_dim]).
        """
        lower_bounds = np.tile(lower, (num_nodes, 1))
        lower_bounds = np.array(lower_bounds, dtype=float)
        upper_bounds = np.tile(upper, (num_nodes, 1))
        upper_bounds = np.array(upper_bounds, dtype=float)

        if initial_resource_at_start is not None:
            init_value = np.array(initial_resource_at_start, dtype=float)
        else:
            init_value = lower_bounds[0, :]
        return cls(
            name,
            ref,
            (lower_bounds, upper_bounds),
            initial_resource_at_start=init_value,
        )

    @classmethod
    def from_array_bounds(
        cls,
        name: str,
        ref: Callable[[Dict[str, np.ndarray], int, int, Any], np.ndarray],
        lower_bounds: List,  # each element MUST be a list (vector) even if length 1
        upper_bounds: List,
        initial_resource_at_start: Optional[np.ndarray] = None,
    ) -> "ResourceDef":
        """
        Creates a ResourceDef from explicit lower/upper bound lists.
        Each bounds[i] must be a list representing resource vector for node i (even when it is of length 1).
        Resulting arrays have shape [num_nodes, resource_dim].
        """
        lower_bounds_np = np.array(lower_bounds, dtype=float)
        upper_bounds_np = np.array(upper_bounds, dtype=float)
        if initial_resource_at_start is not None:
            init_value = np.array(initial_resource_at_start, dtype=float)
        else:
            init_value = lower_bounds_np[0]
        return cls(
            name,
            ref,
            (lower_bounds_np, upper_bounds_np),
            initial_resource_at_start=init_value,
        )

    def is_within_bounds(self, value: np.ndarray, node_idx: int) -> bool:
        """
        Checks if 'value' is within lower/upper bounds for the specified node index.
        """
        if self.windows is None:
            return True
        lower = self.get_lower_bound(node_idx)
        upper = self.get_upper_bound(node_idx)
        # value = np.array(value, dtype=float)
        return np.all(value >= lower) and np.all(value <= upper)

    def get_lower_bound(self, node_idx: int) -> np.ndarray:
        return self.windows[0][node_idx]

    def get_upper_bound(self, node_idx: int) -> np.ndarray:
        return self.windows[1][node_idx]
