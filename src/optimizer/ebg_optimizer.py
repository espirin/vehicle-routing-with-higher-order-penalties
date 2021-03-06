from typing import List, Dict, Tuple, Set, Optional

from ortools.constraint_solver import routing_enums_pb2

from src.optimizer.optimizer import Optimizer
from src.routing_problem.lanelet import Lanelet


class EBGOptimizer(Optimizer):
    """
    EBGOptimizer (Edge-Based Graph Optimizer) is used in current AtlaRoute and lane topology approaches.

    check_topology parameter can used to switch between approaches.
    """

    def __init__(self,
                 nodes: List[Lanelet],
                 matrix: Dict[str, Dict[str, int]],
                 local_search_metaheuristic: routing_enums_pb2.LocalSearchMetaheuristic,
                 first_solution_strategy: routing_enums_pb2.FirstSolutionStrategy,
                 max_optimisation_duration: int,
                 check_topology: bool,
                 connections: Optional[Set[Tuple[Lanelet]]] = None):
        super().__init__(nodes, matrix, local_search_metaheuristic, first_solution_strategy, max_optimisation_duration)

        # EBG-specific attributes
        self.connections: Optional[Set[Tuple[Lanelet]]] = connections
        self.check_topology: bool = check_topology

    def distance_callback(self, from_index, to_index) -> int:
        from_element_index = self.manager.IndexToNode(from_index)
        to_element_index = self.manager.IndexToNode(to_index)

        from_maneuver = self.nodes[from_element_index]
        to_maneuver = self.nodes[to_element_index]

        return from_maneuver.get_cost_to(to_maneuver,
                                         self.matrix,
                                         self.connections,
                                         self.check_topology)
