from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Variable:
    """Representation of a decision variable."""

    name: str
    lb: float = 0.0
    ub: Optional[float] = None
    is_integer: bool = False


@dataclass
class Constraint:
    """Representation of a linear constraint."""

    name: str
    coefficients: Dict[str, float]  # {var_name: coefficient}
    sense: str  # '=', '<=', '>='
    rhs: float


@dataclass
class Objective:
    sense: str = "min"  # or "max"
    coefficients: Dict[str, float] = field(default_factory=dict)


@dataclass
class Model:
    """Pure mathematical representation of an LP/MIP model."""

    name: str = "model"
    variables: Dict[str, Variable] = field(default_factory=dict)
    constraints: Dict[str, Constraint] = field(default_factory=dict)
    objective: Objective = field(default_factory=Objective)

    def add_variable(
        self,
        name: str,
        obj_coeff: float = 0.0,
        col_coeffs: dict[str, float] | None = None,
        lb: float = 0.0,
        ub: float | None = None,
        is_integer: bool = False,
    ):
        """
        Add a new decision variable and update the model (objective and constraints).

        Parameters:
            name (str): The name of the variable.
            obj_coeff (float, optional): Objective function coefficient for this variable. Defaults to 0.0.
            col_coeffs (dict[str, float] | None, optional): Coefficient per constraint name for the variable (maps constraint name -> coefficient).
                If not provided, all coefficients are assumed to be 0.0. Defaults to None.
            lb (float, optional): Lower bound of the variable. Defaults to 0.0.
            ub (float | None, optional): Upper bound of the variable. If None, variable is unbounded above. Defaults to None.
            is_integer (bool, optional): Whether the variable is integer-valued. Defaults to False.
        """
        if name in self.variables:
            raise ValueError(f"Variable '{name}' already exists in the model.")

        self.variables[name] = Variable(name, lb, ub, is_integer)
        self.objective.coefficients[name] = obj_coeff

        for constr in self.constraints.values():
            constr.coefficients[name] = (
                col_coeffs.get(constr.name, 0.0) if col_coeffs else 0.0
            )


    def add_constraint(
        self,
        name: str,
        coefficients: dict[str, float],
        sense: str,
        rhs: float,
    ):
        """
        Add a linear constraint to the model.
        coefficients: Dict[var_name, coef], only nonzero entries
        sense: '=', '<=', '>='
        rhs: right-hand side float
        """
        if name in self.constraints:
            raise ValueError(f"Constraint '{name}' already exists in the model.")
        # For variables missing in coefficients, assume 0.0; for missing variables, add them with coef 0.0 for this constraint
        coef_full = {v: coefficients.get(v, 0.0) for v in self.variables}
        self.constraints[name] = Constraint(
            name=name,
            coefficients=coef_full,
            sense=sense,
            rhs=rhs,
        )
