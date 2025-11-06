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
        """
        Add a variable to the internal model representation.

        Parameters:
            name (str): The name of the variable.
            obj_coeff (float, optional): Objective function coefficient for this variable. Defaults to 0.0.
            col_coeffs (Optional[Dict[str, float]], optional): Coefficient per constraint name {constraint_name: coefficient}. 
                If a constraint name isn't mentioned, its coefficient is assumed to be 0.0. Defaults to None.
            lb (float, optional): Lower bound of the variable. Defaults to 0.0.
            ub (Optional[float], optional): Upper bound of the variable. If None, variable is unbounded above. Defaults to None.
            is_integer (bool, optional): Whether the variable is integer-valued. Defaults to False.
        """
        self.model.add_variable(name, obj_coeff, col_coeffs, lb, ub, is_integer)

    def set_objective(self, name: str, coefficients: Dict[str, float], sense: str):
        """
        Set the objective of both the abstract and Docplex models.
        """
        self.model.set_objective(name, coefficients, sense)
    
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
