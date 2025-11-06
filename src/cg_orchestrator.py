"""
Column Generation (CG) Orchestrator for Vehicle Routing Problems (VRP) and Variants.

- Builds a (restricted) master problem (RMP) as a relaxed set covering problem (SCP) (see models/set_covering.py).
- Solves the RMP to obtain dual variables.
- Passes duals to a pricing component (e.g., ESPPTWC, see espprc/espptwc.py) to generate a new column (route).
- Adds new column to RMP; repeat until optimality (no negative reduced cost column can be found).

"""

from typing import Dict, List, Optional, Any
from src.restricted_master_problems.set_covering import build_set_covering_problem
from src.espprc.problem_data import ESPPRCBaseProblemData
from src.espprc.espptwc import ESPPTWC
from src.solvers.cplex_solver import CplexSolver
from src.espprc.espprc_solver import LabelingSolver


class ColumnGenerationOrchestrator:
    def __init__(
        self,
        problem_data: ESPPRCBaseProblemData,
        initial_routes: Optional[List[List[int]]] = None,
    ):
        """
        Args:
            problem_data: ESPPRCBaseProblemData instance.
            initial_routes: Optional list of ...
        """
        self.problem_data = problem_data
        self.problem = ESPPTWC(self.problem_data)
        self.routes = initial_routes if initial_routes is not None else []
        self.labeling_solver = None
        self.restricted_master_model = self.initialize_restricred_master_problem()
        self.rmp_solver = CplexSolver(self.restricted_master_model)

        print(self.restricted_master_model.constraints.values())
        self._map_constraint_name_to_int = {}
        for constraint_name in self.restricted_master_model.constraints:
            num = int(constraint_name.split("_")[-1])
            self._map_constraint_name_to_int[constraint_name] = num

    def initialize_restricred_master_problem(self):
        """
        Initializes the restricted master problem (RMP) as a relaxed set covering problem.
        """
        # solver of pricing problems
        self.labeling_solver = LabelingSolver(
            self.problem,
            label_selector=LabelingSolver.make_min_resource_selector("reduced_cost"),
        )

        if not self.routes:
            self.routes = self._generate_trivial_variables(
                self.problem_data.num_customers
            )
        costs = [self.problem.path_cost(route) for route in self.routes]

        # Build the cover matrix: for each customer (row), does this route (column) visit it? 1 if yes, else 0.
        num_customers = self.problem_data.num_customers
        cover_matrix = []
        for customer in range(1, num_customers + 1):
            row = []
            for route in self.routes:
                # route[1:-1] excludes depots (first and last node)
                row.append(1 if customer in route[1:-1] else 0)
            cover_matrix.append(row)

        restricted_master_model = build_set_covering_problem(
            cover_matrix, costs, partitioned=False, relaxed=True
        )
        return restricted_master_model

    @staticmethod
    def _translate_path_to_col_coeffs(path: Any) -> Dict[str, float]:
        """
        Translate a path into a dictionary of coefficients per constraint,
        where each nonzero coefficient corresponds to a constraint "cover_element_{i}" with i being the node index
        (excluding the depot, assumed to be node 0).

        Args:
            path: a sequence of node indices, from depot at start to depot at end.

        Returns:
            col_coeffs: Dict[str, float], where the key is "cover_element_{i}" for every customer node i in the path (except depot).
        """

        internal_path = path[1:-1] if len(path) > 2 else []
        col_coeffs = {f"cover_element_{i}": 1.0 for i in internal_path if i != 0}
        return col_coeffs

    @staticmethod
    def _generate_trivial_variables(num_customers):
        """
        Generate trivial routes for the vehicule routing problem:
        A direct route from depot (0) to one customer x
        and then to the end depot (num_customers + 1). Each path is of the form [0, x, num_customers + 1].

        Args:
            num_customers (int): Number of customers (excluding depots).

        Returns:
            routes (list of list): List of routes, each route is [0, x, num_customers + 1] for x in 1..num_customers.
        """
        routes = []
        for x in range(1, num_customers + 1):
            route = [0, x, num_customers + 1]
            routes.append(route)
        return routes

    def run(self, max_iterations: int = 50, tol: float = 1e-5):
        """
        Main CG loop.
        """
        for iter_no in range(max_iterations):
            # Solve current restricted master problem
            objective_value, variables, dual_values = self.rmp_solver.solve()
            print(20 * "=", f"iteration {iter_no}", 20 * "=")
            # print("Objective:", objective_value)
            # print("Variables:", variables)
            # print("Duals:", dual_values)

            # Solve pricing/subproblem to get (potential) new column

            # dual_values is dict[str,float]
            # dual_values should be dict[int, float] using the _map
            dual_values_int = {}
            for name, value in dual_values.items():
                if name in self._map_constraint_name_to_int:
                    idx = self._map_constraint_name_to_int[name]
                    dual_values_int[idx] = value

            self.problem.adjust_costs(dual_values_int)
            labeling_results = self.labeling_solver.solve()
            if not labeling_results:
                print(
                    f"No improving column found at iteration {iter_no}. Terminating CG."
                )
                break
            labels, reduced_cost = labeling_results
            chosen_path = labels[0].path
            col_coeffs = self._translate_path_to_col_coeffs(chosen_path)
            obj_coeff = self.problem.path_cost(chosen_path)
            # Check reduced cost: stop if not negative enough
            if reduced_cost >= -tol:
                print(
                    f"Reduced cost above tolerance at iteration {iter_no}: {reduced_cost} >= {-tol}. Stopping."
                )
                break
            print(f"reduced_cost: {reduced_cost}")
            # Add new variable (column) to master
            num_variables = len(self.rmp_solver.model.variables)
            var_name = f"p_{num_variables}"
            # print(f"all variables{self.rmp_solver.model.variables.keys()}")
            # print(f"introducing {var_name}: {chosen_label.path} ")
            self.rmp_solver.add_variable(
                name=var_name, obj_coeff=obj_coeff, col_coeffs=col_coeffs
            )
        else:
            print("Column Generation reached iteration limit!")
        # Return final master problem solution
        return objective_value, variables


if __name__ == "__main__":
    from .espprc.problem_data import BaseResourceWindows, ESPPTWCProblemData
    from .test_data_instances import espptwc_test_longest_path

    # Example: How to use ColumnGenerationOrchestrator, runs column generation with example problem data
    problem_data = ESPPTWCProblemData(
        num_customers=espptwc_test_longest_path["num_customers"],
        resource_windows=BaseResourceWindows(
            constant=espptwc_test_longest_path["resource_windows"]["constant"],
            node_dependent=espptwc_test_longest_path["resource_windows"][
                "node_dependent"
            ],
        ),
        graph=espptwc_test_longest_path["graph"],
        costs=espptwc_test_longest_path["costs"],
        travel_times=espptwc_test_longest_path["travel_times"],
        demands=espptwc_test_longest_path["demands"],
    )

    # Instantiate the CG orchestrator with sample problem data and run the column generation algorithm
    orchestrator = ColumnGenerationOrchestrator(problem_data)
    result = orchestrator.run(max_iterations=50)

    # Print the final master problem solution
    print("Final master problem solution:")
    print(result)
