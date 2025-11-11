import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from ..model import Model


class BaseSolver(ABC):
    """Abstract base solver interface for LP/MIP solvers."""

    def __init__(self, model: Optional[Model] = None):
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

        self.model = model or Model()
        self.logger.debug(
            "Initialized BaseSolver with model: %s", type(self.model).__name__
        )

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
        self.logger.info(
            f"Adding variable '{name}', obj_coeff={obj_coeff}, lb={lb}, ub={ub}, is_integer={is_integer}"
        )
        self.model.add_variable(name, obj_coeff, col_coeffs, lb, ub, is_integer)

    def set_objective(self, name: str, coefficients: Dict[str, float], sense: str):
        """
        Set the objective of both the abstract and Docplex models.
        """
        self.logger.info(f"Setting objective '{name}', sense={sense}")
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
        self.logger.info("Calling solve() on base solver...")
        pass
