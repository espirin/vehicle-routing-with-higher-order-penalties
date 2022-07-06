from abc import ABC, abstractmethod
from typing import List, Dict, Tuple

from ortools.constraint_solver import routing_enums_pb2, pywrapcp

from src.optimizer.monitor import RoutingMonitor


class Optimizer(ABC):
    """
    Optimizer solves Vehicle Routing Problem.

    See: https://developers.google.com/optimization/routing/vrp
    """

    def __init__(self,
                 nodes: List,
                 matrix: Dict[str, Dict[str, int]],
                 local_search_metaheuristic: routing_enums_pb2.LocalSearchMetaheuristic,
                 first_solution_strategy: routing_enums_pb2.FirstSolutionStrategy,
                 max_optimisation_duration: int):
        # Shared attributes
        self.nodes: List = nodes
        self.matrix: Dict[str, Dict[str, int]] = matrix
        self.local_search_metaheuristic: routing_enums_pb2.LocalSearchMetaheuristic = local_search_metaheuristic
        self.first_solution_strategy: routing_enums_pb2.FirstSolutionStrategy = first_solution_strategy
        self.max_optimisation_duration: int = max_optimisation_duration

        # Create routing model
        self.manager = pywrapcp.RoutingIndexManager(len(self.nodes), 1, [0], [len(self.nodes) - 1])
        self.routing = pywrapcp.RoutingModel(self.manager)
        self.monitor = RoutingMonitor(self.routing)
        self.routing.AddAtSolutionCallback(self.monitor)

        # Register transit callback
        transit_callback_index = self.routing.RegisterTransitCallback(self.distance_callback)
        self.routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Set routing parameters
        self.search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        self.search_parameters.first_solution_strategy = first_solution_strategy
        self.search_parameters.local_search_metaheuristic = local_search_metaheuristic
        self.search_parameters.time_limit.seconds = max_optimisation_duration

    @abstractmethod
    def distance_callback(self, from_index, to_index) -> int:
        pass

    def optimize(self, return_dict: Dict = None, proc_number: int = None) -> Tuple[List, Dict[str, int]]:
        assignment = self.routing.SolveWithParameters(self.search_parameters)
        if self.routing.status() != 1:
            raise Exception(f"Routing failed. Routing status {self.routing.status()}")
        optimal_order = self.format_solution(assignment)
        optimisation_history = self.monitor.optimization_history

        if return_dict is not None:
            return_dict[proc_number] = {
                "order": optimal_order,
                "history": optimisation_history
            }

        return optimal_order, optimisation_history

    def format_solution(self, assignment) -> List:
        index = self.routing.Start(0)
        optimal_order = []
        route_objective = 0
        while not self.routing.IsEnd(index):
            optimal_order.append(self.manager.IndexToNode(index))
            previous_index = index
            index = assignment.Value(self.routing.NextVar(index))
            route_objective += self.routing.GetArcCostForVehicle(previous_index, index, 0)
        optimal_order.append(self.manager.IndexToNode(index))
        optimal_order = [self.nodes[i] for i in optimal_order]

        # Check if the route is empty
        if route_objective == 0:
            raise Exception("Optimiser error. Route objective 0. ")

        return optimal_order
