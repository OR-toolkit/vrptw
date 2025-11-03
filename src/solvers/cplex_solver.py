from docplex.mp.model import Model as CplexModel
from .base_solver import BaseSolver


class CplexSolver(BaseSolver):
    def __init__(self, model):
        super().__init__(model)
        self._model = CplexModel(name=model.name)
        self._build_from_model()

    def _build_from_model(self):
        """Populate the Docplex model from the abstract model.
        will only be called once, when the solver is initialized
        """

        # Create variables from the abstract model to the internal docplex model
        for vname, var in self.model.variables.items():
            if var.is_integer:
                self._model.integer_var(lb=var.lb, ub=var.ub, name=vname)
            else:
                self._model.continuous_var(lb=var.lb, ub=var.ub, name=vname)

        # Add constraints
        for constr in self.model.constraints.values():
            expr = 0
            for vname, coef in constr.coefficients.items():
                var = self._model.get_var_by_name(vname)
                if var is None:
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
                raise ValueError(f"Unsupported constraint sense '{constr.sense}'")

        # Set the objective
        obj_expr = 0
        for vname, coef in self.model.objective.coefficients.items():
            var = self._model.get_var_by_name(vname)
            if var is None:
                raise KeyError(f"Unknown variable '{vname}' in objective")
            obj_expr += coef * var

        sense = self.model.objective.sense.lower()
        if sense == "min":
            self._model.minimize(obj_expr)
        elif sense == "max":
            self._model.maximize(obj_expr)
        else:
            raise ValueError(f"Unknown objective sense '{self.model.objective.sense}'")


    def add_variable(self, name, obj, col_coeffs, lb=0.0, ub=None, is_integer=False):
        """Add a variable to both the abstract and Docplex models.
        use internal docplex model to add the variable
        """
        super().add_variable(name, obj, col_coeffs, lb, ub, is_integer)
        if is_integer:
            var = self._model.integer_var(lb=lb, ub=ub, name=name)
        else:
            var = self._model.continuous_var(lb=lb, ub=ub, name=name)

        self._var_map[name] = var
        if obj != 0:
            new_expression = self._model.objective_expr()
            self._model.objective_expr(new_expr=new_expression)
            self._model.set_objective(self._model.objective_expr + obj * var)
        for constr in self.model.constraints:
            coef = constr.coefficients.get(name, 0.0)
            if coef != 0:
                self._model.get_constraint_by_name(constr.name).lhs += coef * var

    def _get_dual_values(self):
        """"
        Get the dual values of the constraints from the internal docplex model
        """
        cts = self._model.iter_constraints()
        duals = self._model.dual_values(cts)
        return duals

    def solve(self):
        """
        Solve the model using the internal docplex model
        """
        self._model.solve()
        variables = {v.name: v.solution_value for v in self._model.iter_variables()}
        dual_values = self._get_dual_values()
        return {
            "objective": self._model.objective_value,
            "variables": variables,
            "dual_values": dual_values,
        }
