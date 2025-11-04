from ..model import Model
from .cplex_solver import CplexSolver
from ..models.set_covering import build_set_covering_problem


def create_simple_model():
    model = Model(name="simple_LP")
    model.add_variable("x", obj_coeff=3, lb=0)
    model.add_variable("y", obj_coeff=5, lb=0)
    model.add_constraint("c1", coefficients={"x": 2, "y": 1}, sense=">=", rhs=8)
    model.add_constraint("c2", coefficients={"x": 1, "y": 2}, sense=">=", rhs=6)
    return model


def test_cplex_solver(model: Model):
    """Test the CPLEX solver with a simple model."""
    solver = CplexSolver(model)
    result = solver.solve()
    print(f"Solution: {result}")


def test_cplex_solver_adding(model: Model):
    """Test the CPLEX solver with a simple model.
    then add a variable and solve again
    """
    solver = CplexSolver(model)
    result = solver.solve()
    print(f"Initial solution: {result}")
    solver.add_variable("z", obj=4, col_coeffs=None, lb=0)
    result = solver.solve()
    print(f"Solution after adding variable: {result}")


if __name__ == "__main__":
    model = create_simple_model()
    test_cplex_solver_adding(model)

    # Example cover matrix for set covering problem:
    # 4 elements (rows) to cover, 6 sets (columns)
    # At least 2 different exact covers exist, not all sets cover all elements.
    # Let the matrix be :
    #     S0 S1 S2 S3 S4 S5
    # E0  1  0  1  0  1  0
    # E1  1  0  0  1  0  1
    # E2  0  1  1  0  0  1
    # E3  0  1  0  1  1  0
    #
    # Two exact covers:
    #   [S0, S1]  -- S0 covers E0,E1; S1 covers E2,E3
    #   [S2, S3]  -- S2 covers E0,E2; S3 covers E1,E3
    cover_matrix = [
        [1, 0, 1, 0, 1, 0],  # E0
        [1, 0, 0, 1, 0, 1],  # E1
        [0, 1, 1, 0, 0, 1],  # E2
        [0, 1, 0, 1, 1, 0],  # E3
    ]
    #costs = [2, 3, 1, 2, 4, 1]
    costs = [2, 3, 4, 2, 4, 2]
    # test partitioned and relaxed models
    relaxed_model = build_set_covering_problem(
        cover_matrix, costs, partitioned=False, relaxed=True
    )
    print("try the set covering problem")
    test_cplex_solver(relaxed_model)
