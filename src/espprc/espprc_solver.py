from typing import List, Dict, Callable
from .label import Label
from .base_espprc import ESPPRC


def fifo_selector(unprocessed_labels: Dict[int, List[Label]]) -> Label:
    """Select the first available unprocessed label (FIFO)."""
    for node_labels in unprocessed_labels.values():
        if node_labels:
            return node_labels[0]


def lifo_selector(unprocessed_labels: Dict[int, list]) -> "Label":
    """Select the most recently added unprocessed label (LIFO)."""
    for node_labels in unprocessed_labels.values():
        if node_labels:
            return node_labels[-1]
    return None


def make_min_resource_selector(resource_name: str):
    """
    Return a selector function that picks the label
    with the smallest value for a given resource (higher order function).

    Example:
        selector = make_min_resource_selector("reduced_cost")
        label = selector(unprocessed_labels)
    """

    def selector(unprocessed_labels: Dict[int, list]) -> "Label":
        best_label = None
        best_value = float("inf")

        for node_labels in unprocessed_labels.values():
            for label in node_labels:
                # Handle both scalar and vector resources
                resource = label.resources[resource_name]
                value = resource[0] if resource.size == 1 else resource.sum()
                if value < best_value:
                    best_value = value
                    best_label = label

        return best_label

    return selector


def labeling_algorithm(
    problem: ESPPRC, label_selector: Callable[[Dict[int, List[Label]]], Label] = None
) -> Dict[int, List[Label]]:
    """
    Generic labeling algorithm for ESPPRC-type problems.

    Args:
        problem: an instance of a subclass of ESPPRC (e.g., ESPPTWC)
        start_node: node where labeling begins (default=0)
        label_selector: function that selects the next label to process.
                        It receives `unprocessed_labels` (dict of lists) and returns one Label.

    Returns:
        labels_at_node: dictionary {node: [non-dominated labels]}
    """

    start_node = 0
    num_nodes = problem.problem_data["num_customers"] + 2  # depot at start & at end

    # Initialize empty structures for all nodes
    labels_at_node = {i: [] for i in range(num_nodes)}
    unprocessed_labels = {i: [] for i in range(num_nodes)}

    start_label = problem.initialize_label()

    labels_at_node[start_node].append(start_label)
    unprocessed_labels[start_node].append(start_label)

    while any(unprocessed_labels[i] for i in range(num_nodes)):
        current_label = label_selector(unprocessed_labels)
        current_node = current_label.node

        unprocessed_labels[current_node].remove(current_label)

        for dest in problem.problem_data["graph"].get(current_node, []):
            new_label = problem.extend_label(current_label, dest)
            if new_label is None:
                continue

            if not problem.check_feasibility(new_label):
                continue

            # Dominance filtering
            dominated = []
            for label in labels_at_node[dest]:
                if label.dominates(new_label):
                    continue
                elif new_label.dominates(label):
                    dominated.append(label)

            # Remove dominated labels from both lists
            for label in dominated:
                labels_at_node[dest].remove(label)
                if label in unprocessed_labels[dest]:
                    unprocessed_labels[dest].remove(label)

            # Add the extended label to both structures
            labels_at_node[dest].append(new_label)
            unprocessed_labels[dest].append(new_label)

    # Return all labels with minimum cost in the end node/depot at end (in case of ties)
    end_node = num_nodes - 1
    final_labels = labels_at_node[end_node]
    if not final_labels:
        return []  # not feasible
    min_cost = min(label.resources["reduced_cost"][0] for label in final_labels)
    best_labels = [
        label
        for label in final_labels
        if label.resources["reduced_cost"][0] == min_cost
    ]

    return best_labels
