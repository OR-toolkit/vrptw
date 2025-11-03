from ..model import Model, Constraint
from .cplex_solver import CplexSolver

def create_simple_model():
    model = Model(name="simple_LP")
    model.add_variable("x", obj_coeff=3, lb=0)
    model.add_variable("y", obj_coeff=5, lb=0)
    model.constraints["c1"] = Constraint(
        name="c1", coefficients={"x": 2, "y": 1}, sense=">=", rhs=8
    )
    model.constraints["c2"] = Constraint(
        name="c2", coefficients={"x": 1, "y": 2}, sense=">=", rhs=6
    )
    return model

def test_cplex_solver(model: Model):
    """Test the CPLEX solver with a simple model.
    then add a variable and solve again
    """
    solver = CplexSolver(model)
    result = solver.solve()
    print(f"Initial solution: {result}")

    model.add_variable("z", obj_coeff=4, lb=0)
    solver = CplexSolver(model)
    result = solver.solve()
    print(f"Solution after adding variable: {result}")


if __name__ == "__main__":
    model = create_simple_model()
    test_cplex_solver(model)
