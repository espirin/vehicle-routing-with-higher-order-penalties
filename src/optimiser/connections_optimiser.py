from typing import List, Dict, Tuple

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from src.config import OPTIMISER_INFINITY
from src.optimiser.monitor import RoutingMonitor
from src.routing_problem.connections.complete import CompleteConnection


class ConnectionsOptimiser:
    def __init__(self,
                 connections: List[CompleteConnection],
                 disjunctions: List[List[int]],
                 matrix: Dict[str, Dict[str, int]],
                 local_search_metaheuristic: routing_enums_pb2.LocalSearchMetaheuristic,
                 first_solution_strategy: routing_enums_pb2.FirstSolutionStrategy,
                 max_optimisation_duration: int,
                 straight_non_straight_maneuver_penalty=600,
                 non_straight_straight_maneuver_penalty=200):
        self.connections: List[CompleteConnection] = connections
        self.disjunctions: List[List[int]] = disjunctions
        self.matrix: Dict[str, Dict[str, int]] = matrix

        # Create routing model
        self.manager = pywrapcp.RoutingIndexManager(len(self.connections), 1, [0],
                                                    [len(self.connections) - 1])
        self.routing = pywrapcp.RoutingModel(self.manager)
        self.monitor = RoutingMonitor(self.routing)
        self.routing.AddAtSolutionCallback(self.monitor)

        # Create distance callback
        def distance_callback(from_index, to_index):
            from_element_index = self.manager.IndexToNode(from_index)
            to_element_index = self.manager.IndexToNode(to_index)

            from_connection = self.connections[from_element_index]
            to_connection = self.connections[to_element_index]
            return from_connection.get_cost_to(to_connection,
                                               self.matrix,
                                               straight_non_straight_maneuver_penalty,
                                               non_straight_straight_maneuver_penalty)

        transit_callback_index = self.routing.RegisterTransitCallback(distance_callback)
        self.routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add disjunctions
        for pack in self.disjunctions:
            self.routing.AddDisjunction([self.manager.NodeToIndex(i) for i in pack],
                                        OPTIMISER_INFINITY,
                                        1)

        # Set routing parameters
        self.search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        self.search_parameters.first_solution_strategy = first_solution_strategy
        self.search_parameters.local_search_metaheuristic = local_search_metaheuristic
        self.search_parameters.time_limit.seconds = max_optimisation_duration

    def optimise(self) -> Tuple[List[CompleteConnection], Dict]:
        assignment = self.routing.SolveWithParameters(self.search_parameters)
        if self.routing.status() != 1:
            raise Exception(f"Routing failed. Routing status {self.routing.status()}")
        optimal_order = self.format_solution(assignment)
        optimisation_history = self.monitor.optimization_history
        return optimal_order, optimisation_history

    def format_solution(self, assignment) -> List[CompleteConnection]:
        index = self.routing.Start(0)
        optimal_order = []
        route_objective = 0
        while not self.routing.IsEnd(index):
            optimal_order.append(self.manager.IndexToNode(index))
            previous_index = index
            index = assignment.Value(self.routing.NextVar(index))
            route_objective += self.routing.GetArcCostForVehicle(previous_index, index, 0)
        optimal_order.append(self.manager.IndexToNode(index))
        optimal_order = [self.connections[i] for i in optimal_order]
        if route_objective == 0:
            raise Exception("Optimiser error. Route objective 0. ")
        return optimal_order
