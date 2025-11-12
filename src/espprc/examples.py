from .espprc_data import ESPPTWCProblemData
from ..test_data_instances import espptwc_test_1
import logging

logging.getLogger("src.espprc.espprc_solver").setLevel(logging.DEBUG)

# Also construct the ESPPTWCProblemData directly
problem_instance_1 = ESPPTWCProblemData(
    num_customers=espptwc_test_1["num_customers"],
    capacity=espptwc_test_1["capacity"],
    graph=espptwc_test_1["graph"],
    costs=espptwc_test_1["costs"],
    travel_times=espptwc_test_1["travel_times"],
    demands=espptwc_test_1["demands"],
    time_windows=espptwc_test_1["time_windows"],
)


def espptwc_basic_example():
    """
    Example showcasing label extension, feasibility, and dominance checks for ESPPTWCProblemData/ESPPTWC instance.
    """
    from .espptwc_model import EspptwcModel

    espptwc = EspptwcModel(problem_instance_1)
    depot_label = espptwc.initialize_label()
    print("Initial depot label resources:")
    for r, val in depot_label.resources.items():
        print(f"{r}: {val}")
    print("Path:", depot_label.path)

    # Extend from depot to customer 1
    label1 = espptwc.extend_label(depot_label, destination=1)
    if label1:
        print("\nExtended label to customer 1:")
        for r, val in label1.resources.items():
            print(f"{r}: {val}")
        print("Path:", label1.path)
    else:
        print("\nExtension to customer 1 is infeasible")

    # Extend from depot to customer 2
    label2 = espptwc.extend_label(depot_label, destination=2)
    if label2:
        print("\nExtended label to customer 2:")
        for r, val in label2.resources.items():
            print(f"{r}: {val}")
        print("Path:", label2.path)
    else:
        print("\nExtension from depot to customer 2 is infeasible")

    # Extend from depot to customer 3 (may be infeasible)
    label3 = espptwc.extend_label(depot_label, destination=3)
    if label3:
        print("\nExtended depot label from depot to customer 3:")
        for r, val in label3.resources.items():
            print(f"{r}: {val}")
        print("Path:", label3.path)
    else:
        print("\nDepot extension to customer 3 is infeasible")

    # Extend from label1 to customer 3
    label13 = espptwc.extend_label(label1, destination=3)
    if label13:
        print("\nExtended label1 to customer 3:")
        for r, val in label13.resources.items():
            print(f"{r}: {val}")
        print("Path:", label13.path)
    else:
        print("\nExtension to customer 3 is infeasible from label1")

    # Extend from label2 to customer 3
    label23 = espptwc.extend_label(label2, destination=3)
    if label23:
        print("\nExtended label2 to customer 3:")
        for r, val in label23.resources.items():
            print(f"{r}: {val}")
        print("Path:", label23.path)
    else:
        print("\nExtension to customer 3 is infeasible from label2")

    # check feasibility
    print("Feasibility (label1):", espptwc.check_feasibility(label1))
    print("Feasibility (label2):", espptwc.check_feasibility(label2))
    print("Feasibility (label13):", espptwc.check_feasibility(label13))
    print("Feasibility (label23):", espptwc.check_feasibility(label23))

    # check dominance
    print("label1 dominates label1:", label1.dominates(label1))
    print("label1 dominates label2:", label1.dominates(label2))
    print("label2 dominates label1:", label2.dominates(label1))


def labeling_algorithm_basic_example():
    """
    Example showing usage of the LabelingSolver class and printing the best labels/resources.
    """
    from .espptwc_model import EspptwcModel
    from .espprc_solver import LabelingSolver

    espptwc = EspptwcModel(problem_instance_1)
    min_label_selector = LabelingSolver.make_min_resource_selector(resource_name="time")
    solver = LabelingSolver(espptwc, label_selector=min_label_selector)

    if not solver.logger.handlers:
        ch = logging.StreamHandler()
        formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        solver.logger.addHandler(ch)

    best_labels, _ = solver.solve()

    print("Results:")
    for label in best_labels:
        resources = label.resources
        print(f"resources {resources}")


if __name__ == "__main__":
    print("--------- espptwc_basic_example ---------")
    espptwc_basic_example()
    print("--------- labeling_algorithm_basic_example ---------")
    labeling_algorithm_basic_example()
