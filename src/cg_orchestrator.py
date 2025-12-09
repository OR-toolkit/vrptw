"""
Column Generation (CG) Orchestrator for Vehicle Routing Problems (VRP) and Variants.

- Builds a (restricted) master problem (RMP) as a relaxed set covering problem (SCP) (see models/set_covering.py).
- Solves the RMP to obtain dual variables.
- Passes duals to a pricing component (e.g., ESPPTWC, see espprc/espptwc.py) to generate a new column (route).
- Adds new column to RMP; repeat until optimality (no negative reduced cost column can be found).

"""

from typing import Dict, List, Optional, Any
import logging
from src.solvers.cplex_solver import CplexSolver
from src.restricted_master_problems.set_covering import build_set_covering_problem
from src.espprc.espprc_data import ESPPRCBaseProblemData
from src.espprc.espprc_model import EspprcModel
from src.espprc.espptwc_model import EspptwcModel
from src.espprc.espprc_solver import LabelingSolver
from src.config_loader import get_config


class ColumnGenerationOrchestrator:
    def __init__(
        self,
        problem_data: ESPPRCBaseProblemData,
        model: EspprcModel = None,
        initial_routes: Optional[List[List[int]]] = None,
    ) -> None:
        """
        Initializes the ColumnGenerationOrchestrator.

        Args:
            problem_data (ESPPRCBaseProblemData): The ESPPRC problem data instance.
            initial_routes (Optional[List[List[int]]]): Optional list of initial routes. Each route is a list of node indices.
        """
        self.logger = logging.getLogger(__name__)
        config = get_config()
        logging.basicConfig(
            filename=config['logging']['filename'],
            level=getattr(logging, config['logging']['level']),
            format=config['logging']['format'],
        )
        logging.getLogger("src.solvers.base_solver").setLevel(getattr(logging, config['logging']['loggers']['src.solvers.base_solver']))
        logging.getLogger("src.espprc.espprc_solver").setLevel(getattr(logging, config['logging']['loggers']['src.espprc.espprc_solver']))
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            self.logger.addHandler(ch)

        self.problem_data: ESPPRCBaseProblemData = problem_data

        if model is None:
            self.model = EspptwcModel(self.problem_data)
        else:
            self.model = model

        # Initialize routes: use provided initial_routes if any, otherwise generate trivial (dummy) variables.
        if initial_routes is not None and len(initial_routes) > 0:
            self.routes: List[List[int]] = initial_routes
        else:
            self.logger.debug(
                "No initial routes provided. Generating trivial variables for RMP initialization."
            )
            self.routes = self._generate_trivial_variables(
                self.problem_data.num_customers
            )
        # Map from variable name to path used to create it
        self.varname_to_path: Dict[str, list] = {}
        for j, route in enumerate(self.routes):
            self.varname_to_path[f"p_{j}"] = route

        # Map constraint names like "cover_element_5" to their corresponding integer (e.g., 5)
        self._map_constraint_name_to_int: Dict[str, int] = {}
        self.labeling_solver: LabelingSolver = LabelingSolver(
            self.model,
            label_selector=LabelingSolver.make_min_resource_selector("reduced_cost"),
        )
        self.restricted_master_model = self._initialize_restricred_master_problem()
        self.rmp_solver = CplexSolver(self.restricted_master_model)

        for constraint_name in self.restricted_master_model.constraints:
            num = int(constraint_name.split("_")[-1])
            self._map_constraint_name_to_int[constraint_name] = num
        self.logger.info(
            "ColumnGenerationOrchestrator initialized with problem data: %s",
            type(self.problem_data).__name__,
        )

    def _initialize_restricred_master_problem(self) -> Any:
        """
        Initializes the restricted master problem (RMP) as a relaxed set covering problem.

        Returns:
            Any: The initialized restricted master problem model.
        """
        costs = [self.model.path_cost(route) for route in self.routes]
        self.logger.debug(f"Initial routes: {self.routes}")
        self.logger.debug(f"Initial costs: {costs}")

        # Build the cover matrix: for each customer (row), does this route (column) visit it? 1 if yes, else 0.
        num_customers: int = self.problem_data.num_customers
        cover_matrix: List[List[int]] = []
        for customer in range(1, num_customers + 1):
            row: List[int] = []
            for route in self.routes:
                # route[1:-1] excludes depots (first and last node)
                row.append(1 if customer in route[1:-1] else 0)
            cover_matrix.append(row)
        self.logger.debug(f"Constructed cover matrix: {cover_matrix}")

        restricted_master_model = build_set_covering_problem(
            cover_matrix, costs, partitioned=False, relaxed=True
        )
        self.logger.debug("Restricted master problem initialized.")
        return restricted_master_model

    @staticmethod
    def _translate_path_to_col_coeffs(path: Any) -> Dict[str, float]:
        """
        Translate a path into a dictionary of coefficients per constraint,
        where each nonzero coefficient corresponds to a constraint "cover_element_{i}" with i being the node index
        (excluding the depot, assumed to be node 0).

        Args:
            path (Any): a sequence of node indices, from depot at start to depot at end.

        Returns:
            Dict[str, float]: Dictionary where the key is "cover_element_{i}" for every customer node i in the path (except depot).
        """

        internal_path = path[1:-1] if len(path) > 2 else []
        col_coeffs = {f"cover_element_{i}": 1.0 for i in internal_path if i != 0}
        return col_coeffs

    @staticmethod
    def _generate_trivial_variables(num_customers: int) -> List[List[int]]:
        """
        Generate trivial routes for the vehicle routing problem:
        A direct route from depot (0) to one customer x
        and then to the end depot (num_customers + 1). Each path is of the form [0, x, num_customers + 1].

        Args:
            num_customers (int): Number of customers (excluding depots).

        Returns:
            List[List[int]]: List of routes, each route is [0, x, num_customers + 1] for x in 1..num_customers.
        """
        routes: List[List[int]] = []
        for x in range(1, num_customers + 1):
            route = [0, x, num_customers + 1]
            routes.append(route)
        return routes

    def run(self, max_iterations: Optional[int] = None, tol: Optional[float] = None):
        """
        Main CG loop.

        Args:
            max_iterations (int, optional): Maximum number of CG iterations. Defaults to config value.
            tol (float, optional): Reduced cost tolerance for stopping. Defaults to config value.

        Returns:
            Tuple[Any, Any]: Final objective value, and a dictionary {var_name: (value, path)} for nonzero variables.
        """
        logger = self.logger
        config = get_config()
        if max_iterations is None:
            max_iterations = config['orchestrator']['max_iterations']
        if tol is None:
            tol = float(config['orchestrator']['tolerance'])

        for iter_no in range(max_iterations):
            # Solve current restricted master problem
            objective_value, variables, dual_values = self.rmp_solver.solve()
            logger.debug(
                "%s Column Generation Iteration %d %s", "=" * 20, iter_no, "=" * 20
            )
            logger.debug("Objective value: %s", objective_value)
            logger.debug("Number of variables: %d", len(variables))
            logger.debug("Dual values: %s", dual_values)

            # Solve pricing/subproblem to get (potential) new column

            # dual_values is dict[str,float]
            # dual_values_int (to use in adjut_costs) should be dict[int, float] using the _map
            dual_values_int: Dict[int, float] = {}
            for name, value in dual_values.items():
                if name in self._map_constraint_name_to_int:
                    idx = self._map_constraint_name_to_int[name]
                    dual_values_int[idx] = value
            logger.debug(
                "Converted dual_values (string) to (int) indices for pricing: %s",
                dual_values_int,
            )
            self.model.adjust_costs(dual_values_int)

            labeling_results = self.labeling_solver.solve()
            if not labeling_results:
                logger.info(
                    f"No improving column found at iteration {iter_no}. Terminating CG."
                )
                break
            labels, reduced_cost = labeling_results
            chosen_path = labels[0].path
            logger.debug(
                "Obtained new label: path=%s, reduced_cost=%.6f",
                chosen_path,
                reduced_cost,
            )
            col_coeffs = self._translate_path_to_col_coeffs(chosen_path)
            obj_coeff = self.model.path_cost(chosen_path)
            # Check reduced cost: stop if not negative enough
            if reduced_cost >= -tol:
                logger.info(
                    f"Reduced cost above tolerance at iteration {iter_no}: {reduced_cost} >= {-tol}. Stopping."
                )
                break
            logger.debug(f"Adding column with reduced_cost = {reduced_cost:.6f}")
            # Add new variable (column) to master
            num_variables = len(self.rmp_solver.model.variables)
            var_name = f"p_{num_variables}"
            logger.debug(
                "Introducing new variable %s for path %s (coeff = %.6f)",
                var_name,
                chosen_path,
                obj_coeff,
            )
            self.rmp_solver.add_variable(
                name=var_name, obj_coeff=obj_coeff, col_coeffs=col_coeffs
            )
            self.varname_to_path[var_name] = list(chosen_path)  # make a copy to be sure

        else:
            logger.info("Column Generation reached iteration limit!")
        # Return final master problem solution
        logger.debug("Final RMP objective: %s", objective_value)
        logger.debug("Final RMP variables: %s", variables)

        # Only return nonzero variables, along with their path
        nonzero_results = {
            var_name: (value, self.varname_to_path.get(var_name))
            for var_name, value in variables.items()
            if abs(value) > 1e-8  # consider "nonzero"
        }
        for var_name, (value, path) in nonzero_results.items():
            self.logger.info(
                "Variable: %s | Path: %s | Value: %.2f", var_name, path, value
            )
        self.logger.info(
            "Objective value: %.2f | Number of nonzero variables: %d",
            objective_value,
            len(nonzero_results),
        )
        return objective_value, nonzero_results


if __name__ == "__main__":
    from .espprc.espprc_data import ESPPTWCProblemData
    from .test_data_instances import espptwc_test_1 as espptwc_test_longest_path

    # Example: How to use ColumnGenerationOrchestrator, runs column generation with example problem data

    # Also construct the ESPPTWCProblemData directly
    problem_data = ESPPTWCProblemData(
        num_customers=espptwc_test_longest_path["num_customers"],
        capacity=espptwc_test_longest_path["capacity"],
        graph=espptwc_test_longest_path["graph"],
        costs=espptwc_test_longest_path["costs"],
        travel_times=espptwc_test_longest_path["travel_times"],
        demands=espptwc_test_longest_path["demands"],
        time_windows=espptwc_test_longest_path["time_windows"],
    )

    # Instantiate the CG orchestrator with sample problem data and run the column generation algorithm
    orchestrator = ColumnGenerationOrchestrator(problem_data)
    objective_value, nonzero_results = orchestrator.run()

    # Print the final master problem solution
    print(40 * "=")
    print("Final master problem solution:")
    print(40 * "=")

    for var_name, (value, path) in nonzero_results.items():
        print(f"Variable: {var_name} | Path: {path} | Value: {value:.2f}")
    print(
        f"Objective value: {objective_value:.2f} | Num of Needed Vehicules: {len(nonzero_results)}"
    )
