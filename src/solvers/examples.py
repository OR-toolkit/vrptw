from ..model import Model
from .cplex_solver import CplexSolver
from ..restricted_master_problems.set_covering import build_set_covering_problem
import logging

logging.getLogger("src.solvers.base_solver").setLevel(logging.DEBUG)



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
    if not solver.logger.handlers:
        ch = logging.StreamHandler()
        formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        solver.logger.addHandler(ch)

    result = solver.solve()
    print(f"Solution: {result}")


def test_cplex_solver_adding(model: Model):
    """Test the CPLEX solver with a simple model.
    then add a variable and solve again
    """
    solver = CplexSolver(model)
    result = solver.solve()
    print(f"Initial solution: {result}")
    solver.add_variable("z", obj_coeff=4, col_coeffs=None, lb=0)
    result = solver.solve()
    print(f"Solution after adding variable: {result}")


def test_solving_set_covering():
    # Example cover matrix for set covering problem:
    # 4 elements (rows) to cover, 6 sets (columns)
    cover_matrix = [
        #    S0 S1 S2 S3 S4 S5
        [1, 0, 1, 0, 1, 0],  # E0
        [1, 0, 0, 1, 0, 1],  # E1
        [0, 1, 1, 0, 0, 1],  # E2
        [0, 1, 0, 1, 1, 0],  # E3
    ]
    # not all sets cover all elements.
    # exact covers:
    #   [S0, S1]  -- S0 covers E0,E1; S1 covers E2,E3
    #   [S2, S3]  -- S2 covers E0,E2; S3 covers E1,E3
    #   [S4, S5]  -- S4 covers E0,E3; S5 covers E1,E2
    costs = [2, 3, 4, 2, 4, 2]
    # test partitioned and relaxed models
    relaxed_model = build_set_covering_problem(
        cover_matrix, costs, partitioned=False, relaxed=True
    )
    test_cplex_solver(relaxed_model)


def test_set_covering_with_paths_cplex():
    """
    Test the CPLEX solver for set covering where columns are the given paths.
    The cost and cover matrix are built from these explicit paths for espptwc_test_1 / problem_instance_1.
    """
    from src.espprc.examples import problem_instance_1
    from src.espprc.espptwc_model import EspptwcModel

    # Paths (columns)
    paths = [
        [0, 1, 4],
        [0, 2, 4],
        [0, 3, 4],
        [0, 1, 2, 3, 4],
    ]

    # Build cover matrix: each row for a customer (1..3), value 1 if path visits that customer (exclude depots 0,4)
    num_customers = problem_instance_1.num_customers
    cover_matrix = []
    for customer in range(1, num_customers + 1):
        row = []
        for path in paths:
            # Internal path excludes depot nodes
            row.append(1 if customer in path[1:-1] else 0)
        cover_matrix.append(row)

    # Compute costs for each path using ESPPTWC.path_cost
    espptwc_model = EspptwcModel(problem_instance_1)
    costs = [espptwc_model.path_cost(path) for path in paths]

    # Build and solve the set covering problem (relaxed, not partitioned)
    model = build_set_covering_problem(
        cover_matrix, costs, partitioned=False, relaxed=True
    )
    print("Solving set covering for explicit paths (columns)...")
    test_cplex_solver(model)


if __name__ == "__main__":
    print("\n", 10 * "-", "creating a simple model", 10 * "-")
    model = create_simple_model()
    print(
        "\n", 10 * "-", "test the cplex solver updating model functionality", 10 * "-"
    )
    test_cplex_solver_adding(model)
    print("\n", 10 * "-", "test solving set covering", 10 * "-")
    test_solving_set_covering()
    print("\n", 10 * "-", "test on a VRPTW context", 10 * "-")
    test_set_covering_with_paths_cplex()
