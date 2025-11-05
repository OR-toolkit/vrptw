"""
Examples and tests for the set covering problem builder.
"""

from .set_covering import build_set_covering_problem
from ..solvers.cplex_solver import CplexSolver


def example_simple_set_covering():
    """
    Simple set covering example with 4 elements and 6 sets.

    Two exact covers exist:
    - [S0, S1] -- S0 covers E0,E1; S1 covers E2,E3
    - [S2, S3] -- S2 covers E0,E2; S3 covers E1,E3
    """
    #   S0 S1 S2 S3 S4 S5
    cover_matrix = [
        [1, 0, 1, 0, 1, 0],  # E0
        [1, 0, 0, 1, 0, 1],  # E1
        [0, 1, 1, 0, 0, 1],  # E2
        [0, 1, 0, 1, 1, 0],  # E3
    ]
    costs = [2, 3, 4, 2, 4, 2]

    print("=" * 60)
    print("Example 1: Simple Set Covering (Relaxed, Non-partitioned)")
    print("=" * 60)

    model = build_set_covering_problem(
        cover_matrix, costs, partitioned=False, relaxed=True
    )

    print(f"Model name: {model.name}")
    print(f"Number of variables: {len(model.variables)}")
    print(f"Number of constraints: {len(model.constraints)}")
    print(f"Objective sense: {model.objective.sense}")
    print("\nVariables:")
    for var_name, var in model.variables.items():
        print(
            f"  {var_name}: lb={var.lb}, ub={var.ub}, integer={var.is_integer}, obj_coeff={model.objective.coefficients[var_name]}"
        )

    print("\nConstraints:")
    for constr_name, constr in model.constraints.items():
        non_zero_coeffs = {k: v for k, v in constr.coefficients.items() if v != 0}
        print(f"  {constr_name}: {non_zero_coeffs} {constr.sense} {constr.rhs}")

    return model


if __name__ == "__main__":
    print("Testing Set Covering Problem Builder\n")
    example_simple_set_covering()
