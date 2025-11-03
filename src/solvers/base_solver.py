from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from ..model import Model


class BaseSolver(ABC):
    """Abstract base solver interface for LP/MIP solvers."""

    def __init__(self, model: Optional[Model] = None):
        self.model = model or Model()

    def add_variable(
        self,
        name: str,
        obj_coeff: float = 0.0,
        col_coeffs: Optional[Dict[str, float]] = None,
        lb: float = 0.0,
        ub: Optional[float] = None,
        is_integer: bool = False,
    ):
        """Add a variable to the internal model representation."""
        self.model.add_variable(name, obj_coeff, col_coeffs, lb, ub, is_integer)

    @abstractmethod
    def solve(self) -> Dict[str, Any]:
        """
        Solve the current model.
        Returns a dictionary containing:
          - "objective": optimal objective value
          - "variables": {var_name: value}
          - "duals": {constraint_name: dual_value}  (if available)
        """
        pass
