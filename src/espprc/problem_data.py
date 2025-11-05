from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, List


@dataclass
class BaseResourceWindows:
    """
    Defines the resource window format for the generic/base ESPPRC problem.
    """

    constant: Dict[str, Tuple[List[float], List[float]]] = field(default_factory=dict)
    node_dependent: Dict[str, Tuple[List[float], List[float]]] = field(
        default_factory=dict
    )


@dataclass
class ESPPRCBaseProblemData:
    """
    The minimal/generic problem data structure for the base ESPPRC class.
    """

    num_customers: int
    resource_windows: BaseResourceWindows
    graph: Dict[int, List[int]]
    costs: Dict[Tuple[int, int], float]
    adjusted_costs: Dict[Tuple[int, int], float] = field(default_factory=dict)

    def __post_init__(self):
        # Initialize adjusted_costs as an identical copy of costs, unless already provided
        if not self.adjusted_costs:
            self.adjusted_costs = dict(self.costs)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "num_customers": self.num_customers,
            "resource_windows": {
                "constant": self.resource_windows.constant,
                "node_dependent": self.resource_windows.node_dependent,
            },
            "graph": self.graph,
            "costs": self.costs,
            "adjusted_costs": self.adjusted_costs,
        }


@dataclass
class ESPPTWCProblemData(ESPPRCBaseProblemData):
    """
    Problem data structure for ESPPTWC (Elementary Shortest Path Problem with Time Windows and Capacity).
    Extends the base ESPPRC problem data with ESPPTWC-specific fields.
    """

    travel_times: Dict[Tuple[int, int], float] = field(default_factory=dict)
    demands: Dict[int, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        if self.travel_times:
            base["travel_times"] = self.travel_times
        if self.demands:
            base["demands"] = self.demands
        return base


# Example usage:
# resource_windows = BaseResourceWindows(
#     constant={
#         "load": ([0.0], [50.0]),
#         "is_visited": ([0.0, 0.0, 0.0], [1.0, 1.0, 1.0]),
#         "reduced_cost": ([0.0], [float('inf')])
#     },
#     node_dependent={
#         "time": ([0.0, 10.0, 20.0], [100.0, 120.0, 130.0])
#     }
# )
# problem_data = ESPPTWCProblemData(
#     num_customers=3,
#     resource_windows=resource_windows,
#     graph={0: [1,2], 1: [2,0], 2: [0]},
#     costs={(0,1): 5.0, (1,2): 3.0, (0,2): 7.0, (2,0): 2.0, (1,0): 1.0},
#     travel_times = {(0,1): 8.0, (1,2): 9.0, (0,2): 25.0, (2,0): 7.0},
#     demands = {1: 10.0, 2: 20.0}
# )
# problem_data_dict = problem_data.to_dict()
