from typing import List, Dict

from ortools.constraint_solver import routing_enums_pb2

from src.config.config import OPTIMISER_INFINITY
from src.optimizer.optimizer import Optimizer
from src.routing_problem.connections.complete import XGraphNode


class XGraphOptimizer(Optimizer):
    def __init__(self,
                 nodes: List[XGraphNode],
                 disjunctions: List[List[int]],
                 matrix: Dict[str, Dict[str, int]],
                 local_search_metaheuristic: routing_enums_pb2.LocalSearchMetaheuristic,
                 first_solution_strategy: routing_enums_pb2.FirstSolutionStrategy,
                 max_optimisation_duration: int,
                 straight_non_straight_maneuver_penalty: int,
                 non_straight_straight_maneuver_penalty: int):
        super().__init__(nodes, matrix, local_search_metaheuristic, first_solution_strategy, max_optimisation_duration)

        # X-Graph specific attributes
        self.disjunctions: List[List[int]] = disjunctions
        self.straight_non_straight_maneuver_penalty: int = straight_non_straight_maneuver_penalty
        self.non_straight_straight_maneuver_penalty: int = non_straight_straight_maneuver_penalty

        # Register disjunctions
        for pack in self.disjunctions:
            self.routing.AddDisjunction([self.manager.NodeToIndex(i) for i in pack],
                                        OPTIMISER_INFINITY,
                                        1)

    def distance_callback(self, from_index, to_index) -> int:
        from_element_index = self.manager.IndexToNode(from_index)
        to_element_index = self.manager.IndexToNode(to_index)

        from_node = self.nodes[from_element_index]
        to_node = self.nodes[to_element_index]
        return from_node.get_cost_to(to_node,
                                     self.matrix,
                                     self.straight_non_straight_maneuver_penalty,
                                     self.non_straight_straight_maneuver_penalty)
