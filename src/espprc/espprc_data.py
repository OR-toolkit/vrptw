from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, List


@dataclass
class ESPPRCBaseProblemData:
    """
    The minimal/generic problem data structure for the base ESPPRC class.
    """

    num_customers: int
    capacity: float
    graph: Dict[int, List[int]]
    costs: Dict[Tuple[int, int], float]
    adjusted_costs: Dict[Tuple[int, int], float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "num_customers": self.num_customers,
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
    time_windows: Tuple[List[float], List[float]] = field(
        default_factory=lambda: ([], [])
    )

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        if self.travel_times:
            base["travel_times"] = self.travel_times
        if self.demands:
            base["demands"] = self.demands
        return base
