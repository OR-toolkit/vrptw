from src.model import Model


def build_set_covering_problem(cover_matrix, costs, partitioned=False, relaxed=False):
    """
    Build the relaxed linear set covering problem.
    cover_matrix: 2D list or numpy array, where cover_matrix[i][j]=1 if set j covers element i
    costs: list of costs per set (path/extreme point)
    partitioned: if True, add partitioned constraints: for each element i, sum_j a_ij * x_j = 1
    relaxed: if True, add relaxed variables: x_j ∈ [0, 1]

    Note:
        When naming constraints, indexing starts from 1 (i.e., names are 'cover_element_1', 'cover_element_2', ...).
        This is important because 0 is reserved for the depot at the start.

    Returns:
     An instance of Model with constraints and objective set up for SCP.
    """
    m, n = len(cover_matrix), len(cover_matrix[0])
    model = Model(name="set_covering_problem")

    # Add variables: x_j ∈ [0, 1] if relaxed is False, otherwise x_j ∈ [0, 1]
    if relaxed:
        for j in range(n):
            model.add_variable(name=f"p_{j}", obj_coeff=costs[j], ub=1.0)
    else:
        for j in range(n):
            model.add_variable(
                name=f"p_{j}", obj_coeff=costs[j], ub=1.0, is_integer=True
            )

    if partitioned:
        for i in range(m):
            model.add_constraint(
                name=f"cover_element_{i + 1}",  # start constraint names from 1
                coefficients={f"p_{j}": cover_matrix[i][j] for j in range(n)},
                sense="=",
                rhs=1.0,
            )
    else:
        for i in range(m):
            model.add_constraint(
                name=f"cover_element_{i + 1}",  # start constraint names from 1
                coefficients={f"p_{j}": cover_matrix[i][j] for j in range(n)},
                sense=">=",
                rhs=1.0,
            )
    return model
