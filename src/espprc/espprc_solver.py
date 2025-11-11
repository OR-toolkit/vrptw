from typing import List, Dict, Callable
from .label import Label
from .espprc_model import EspprcModel
import logging


class LabelingSolver:
    """
    Helper/driver for labeling algorithms over ESPPRC problems.

    Attributes:
        problem (ESPPRC): An instance of a subclass of ESPPRC (e.g., ESPPTWC).
        label_selector (callable): Function used to select next label to process.
    """

    def __init__(
        self,
        esspprc_problem: EspprcModel,
        label_selector: Callable[[Dict[int, List[Label]]], Label] = None,
    ):
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

        self.problem = esspprc_problem
        # If selector not given, use FIFO by default
        self.label_selector = (
            label_selector if label_selector is not None else self.fifo_selector
        )

    @staticmethod
    def fifo_selector(unprocessed_labels: Dict[int, List[Label]]) -> Label:
        """Select the first available unprocessed label (FIFO)."""
        for node_labels in unprocessed_labels.values():
            if node_labels:
                return node_labels[0]

    @staticmethod
    def lifo_selector(unprocessed_labels: Dict[int, List[Label]]) -> Label:
        """Select the most recently added unprocessed label (LIFO)."""
        for node_labels in unprocessed_labels.values():
            if node_labels:
                return node_labels[-1]
        return None

    @staticmethod
    def make_min_resource_selector(
        resource_name: str,
    ) -> Callable[[Dict[int, List[Label]]], Label]:
        """
        Return a selector function that picks the label with the smallest value for a given resource.
        Example: selector = LabelingSolver.make_min_resource_selector("reduced_cost")
        """

        def selector(unprocessed_labels: Dict[int, List[Label]]) -> Label:
            best_label = None
            best_value = float("inf")
            for node_labels in unprocessed_labels.values():
                for label in node_labels:
                    resource = label.resources[resource_name]
                    value = resource[0] if resource.size == 1 else resource.sum()
                    if value < best_value:
                        best_value = value
                        best_label = label
            return best_label

        return selector

    def set_label_selector(self, selector: Callable[[Dict[int, List[Label]]], Label]):
        """
        Set the label selector strategy for this solver.
        """
        self.label_selector = selector

    def solve(self) -> List[Label]:
        """
        Run the generic labeling algorithm, using this solver's label_selector.
        Returns:
            best_labels: List[Label] - least-cost feasible labels at the final node (e.g., depot).
        """
        label_selector = self.label_selector
        start_node = 0
        num_nodes = self.problem.problem_data.num_customers + 2

        labels_at_node = {i: [] for i in range(num_nodes)}
        unprocessed_labels = {i: [] for i in range(num_nodes)}

        start_label = self.problem.initialize_label()
        labels_at_node[start_node].append(start_label)
        unprocessed_labels[start_node].append(start_label)

        iteration = 0
        while any(unprocessed_labels[i] for i in range(num_nodes)):
            self.logger.debug("Labeling iteration %d started.", iteration)
            current_unprocessed = [
                label
                for label_list in unprocessed_labels.values()
                for label in label_list
            ]
            self.logger.debug(
                "Current unprocessed label paths: %s",
                [label.path for label in current_unprocessed],
            )
            current_label = label_selector(unprocessed_labels)
            current_node = current_label.node
            self.logger.debug(
                "Extending label at node %d with path %s.",
                current_node,
                current_label.path,
            )
            unprocessed_labels[current_node].remove(current_label)
            for dest in self.problem.problem_data.graph.get(current_node, []):
                new_label = self.problem.extend_label(current_label, dest)
                if new_label is None:
                    continue
                self.logger.debug(
                    "Generated label for destination node %d with path %s (reduced cost: %.2f).",
                    dest,
                    new_label.path,
                    new_label.resources["reduced_cost"][0],
                )
                if not self.problem.check_feasibility(new_label):
                    self.logger.debug(
                        "Label for path %s rejected by feasibility check.",
                        new_label.path,
                    )
                    continue
                # Dominance filtering
                dominated = []
                for label in labels_at_node[dest]:
                    if label.dominates(new_label):
                        continue
                    elif new_label.dominates(label):
                        dominated.append(label)
                else:
                    for label in dominated:
                        self.logger.debug(
                            "Removing dominated label at destination node %d with path %s.",
                            dest,
                            label.path,
                        )
                        labels_at_node[dest].remove(label)
                        if label in unprocessed_labels[dest]:
                            unprocessed_labels[dest].remove(label)
                    labels_at_node[dest].append(new_label)
                    unprocessed_labels[dest].append(new_label)
            iteration += 1

        end_node = num_nodes - 1
        final_labels = labels_at_node[end_node]
        if not final_labels:
            self.logger.debug(
                "No feasible labels found at the end node. Returning empty result."
            )
            return []
        min_reduced_cost = min(
            label.resources["reduced_cost"][0] for label in final_labels
        )
        self.logger.info(
            "Feasible paths at end node: %s", [label.path for label in final_labels]
        )
        best_labels = [
            label
            for label in final_labels
            if label.resources["reduced_cost"][0] == min_reduced_cost
        ]
        self.logger.info(
            "Number of least reduced cost labels: %d (minimum reduced cost: %.2f).",
            len(best_labels),
            min_reduced_cost,
        )
        return best_labels, min_reduced_cost
