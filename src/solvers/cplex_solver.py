from docplex.mp.model import Model as CplexModel
from typing import Dict, Optional
from .base_solver import BaseSolver


class CplexSolver(BaseSolver):
    def __init__(self, model):
        super().__init__(model)
        self._model = CplexModel(name=model.name)
        self._build_from_model()

    def _build_from_model(self):
        """
        Populate the Docplex model from the abstract model.
        Will only be called once, when the solver is initialized.
        """
        self.logger.debug("Building Docplex model from abstract model ...")
        # Create variables from the abstract model to the internal docplex model
        for vname, var in self.model.variables.items():
            self.logger.debug("Adding variable to Docplex: %s (Integer: %s, lb=%s, ub=%s)", vname, var.is_integer, var.lb, var.ub)
            if var.is_integer:
                self._model.integer_var(lb=var.lb, ub=var.ub, name=vname)
            else:
                self._model.continuous_var(lb=var.lb, ub=var.ub, name=vname)

        # Add constraints
        for constr in self.model.constraints.values():
            self.logger.debug("Adding constraint: %s (Sense: %s, RHS: %s)", constr.name, constr.sense, constr.rhs)
            expr = 0
            for vname, coef in constr.coefficients.items():
                var = self._model.get_var_by_name(vname)
                if var is None:
                    self.logger.error("Unknown variable '%s' in constraint '%s'", vname, constr.name)
                    raise KeyError(
                        f"Unknown variable '{vname}' in constraint '{constr.name}'"
                    )
                expr += coef * var

            if constr.sense == "=":
                self._model.add_constraint(expr == constr.rhs, ctname=constr.name)
            elif constr.sense == "<=":
                self._model.add_constraint(expr <= constr.rhs, ctname=constr.name)
            elif constr.sense == ">=":
                self._model.add_constraint(expr >= constr.rhs, ctname=constr.name)
            else:
                self.logger.error("Unsupported constraint sense '%s'", constr.sense)
                raise ValueError(f"Unsupported constraint sense '{constr.sense}'")

        # Set the objective
        obj_expr = 0
        for vname, coef in self.model.objective.coefficients.items():
            var = self._model.get_var_by_name(vname)
            if var is None:
                self.logger.error("Unknown variable '%s' in objective", vname)
                raise KeyError(f"Unknown variable '{vname}' in objective")
            obj_expr += coef * var

        sense = self.model.objective.sense.lower()
        self.logger.info("Setting objective: sense=%s, coefficients=%s", sense, self.model.objective.coefficients)
        if sense == "min":
            self._model.minimize(obj_expr)
        elif sense == "max":
            self._model.maximize(obj_expr)
        else:
            self.logger.error("Unknown objective sense '%s'", self.model.objective.sense)
            raise ValueError(f"Unknown objective sense '{self.model.objective.sense}'")

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
        Add a variable to both the abstract and Docplex models using the internal docplex model.

        Parameters:
            name (str): The name of the variable.
            obj_coeff (float, optional): Objective function coefficient for this variable. Defaults to 0.0.
            col_coeffs (dict, optional): Coefficient per constraint name for the variable.
                If not provided, all coefficients are assumed to be 0.0. Defaults to None.
            lb (float, optional): Lower bound of the variable. Defaults to 0.0.
            ub (float or None, optional): Upper bound of the variable. Defaults to None.
            is_integer (bool, optional): Whether the variable is integer. Defaults to False.
        """
        super().add_variable(name, obj_coeff, col_coeffs, lb, ub, is_integer)
        self.logger.info(
            f"Adding variable '{name}' to both Docplex model, obj_coeff={obj_coeff}, lb={lb}, ub={ub}, is_integer={is_integer}"
        )
        if is_integer:
            var = self._model.integer_var(lb=lb, ub=ub, name=name)
        else:
            var = self._model.continuous_var(lb=lb, ub=ub, name=name)

        if obj_coeff != 0:
            self.logger.debug("Updating objective function in Docplex with added variable '%s', obj_coeff=%s", name, obj_coeff)
            new_expression = self._model.get_objective_expr() + obj_coeff * var
            sense = self.model.objective.sense
            self._model.set_objective(sense=sense, expr=new_expression)

        for constr in self.model.constraints.values():
            coef = constr.coefficients.get(name, 0.0)
            if coef != 0:
                self.logger.debug(
                    "Updating constraint '%s' in Docplex with new variable '%s', coef=%s", constr.name, name, coef
                )
                self._model.get_constraint_by_name(constr.name).lhs += coef * var

    def solve(self) -> tuple[float, dict[str, float], dict[int, float]]:
        """
        Solves the optimization model using the internal docplex model and returns the results.

        Returns:
            tuple: A tuple containing:
                - objective (float): The objective function value of the solved model.
                - variables (dict[str, float]): A dictionary mapping variable names to their solution values.
                - dual_values (dict[str, float]): The dual values for all constraints.
        """
        self.logger.info("Solving Docplex model ...")
        solution = self._model.solve()
        if solution is None:
            self.logger.error("No solution found by CPLEX.")
            raise RuntimeError("CPLEX could not find a solution.")
        else:
            self.logger.info("Docplex model solved. Objective value: %s", self._model.objective_value)

        variables: dict[str, float] = {
            v.name: v.solution_value for v in self._model.iter_variables()
        }

        dual_values = {}
        for c in self._model.iter_constraints():
            dual_values[c.name] = c.dual_value

        self.logger.debug("Returning solution: variables=%s, duals=%s", variables, dual_values)
        return (
            self._model.objective_value,
            variables,
            dual_values,
        )
