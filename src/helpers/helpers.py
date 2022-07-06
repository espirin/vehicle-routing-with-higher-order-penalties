from typing import List, Dict, Optional, Set, Tuple

from ortools.constraint_solver.routing_enums_pb2 import FirstSolutionStrategy, LocalSearchMetaheuristic

from src.optimizer.ebg_optimizer import EBGOptimizer
from src.optimizer.x_graph_optimizer import XGraphOptimizer
from src.routing_problem.lanelet import Lanelet
from src.routing_problem.maneuver.modifier import ManeuverModifier
from src.routing_problem.routing_problem import RoutingProblem


def list_difference(list1: List, list2: List) -> List:
    result = []
    for item in list1:
        if item not in list2:
            result.append(item)

    return result


def format_matrix(sources: List[int], destinations: List[int], matrix: List[float]) -> Dict[str, Dict[str, int]]:
    sources = [str(source) for source in sources]
    destinations = [str(destination) for destination in destinations]
    formatted_matrix = dict()
    len_sources = len(sources)
    len_destinations = len(destinations)
    for i in range(len_sources):
        formatted_matrix[sources[i]] = dict()
        for j in range(len_destinations):
            formatted_matrix[sources[i]][destinations[j]] = int(matrix[i * len_sources + j])

    return formatted_matrix


def create_straights(order: List[Lanelet], rp: RoutingProblem) -> List[float]:
    straights = []
    previous_lanelet = None
    current_straight = 0

    for lanelet in order:
        if previous_lanelet is None:
            previous_lanelet = lanelet
            continue

        if (previous_lanelet.segment.id, lanelet.segment.id) in rp.maneuvers:
            maneuver = rp.maneuvers[(previous_lanelet.segment.id, lanelet.segment.id)]

            if maneuver.modifier == ManeuverModifier.Straight:
                if current_straight == 0:
                    current_straight = previous_lanelet.segment.get_length() + lanelet.segment.get_length()
                else:
                    current_straight += lanelet.get_length()
            else:
                if current_straight > 0:
                    straights.append(current_straight)
                    current_straight = 0
        elif current_straight > 0:
            straights.append(current_straight)
            current_straight = 0

        previous_lanelet = lanelet

    if current_straight > 0:
        straights.append(current_straight)

    return straights


def format_x_graph_order(order) -> List[Lanelet]:
    cut_x_graph_order = order[1:-1]
    lanelets_order = []

    for maneuver in cut_x_graph_order:
        lanelets_order.append(maneuver.lanelet_from)
        lanelets_order.append(maneuver.lanelet_to)

    shortened_x_graph_order = []
    for lanelet in lanelets_order:
        if len(shortened_x_graph_order) > 0 and shortened_x_graph_order[-1].segment.id == lanelet.segment.id:
            continue
        shortened_x_graph_order.append(lanelet)

    return shortened_x_graph_order


def optimize_ebg(nodes: List,
                 matrix: Dict[str, Dict[str, int]],
                 local_search_metaheuristic: LocalSearchMetaheuristic,
                 first_solution_strategy: FirstSolutionStrategy,
                 max_optimisation_duration: int,
                 check_topology: bool,
                 connections: Optional[Set[Tuple[Lanelet]]],
                 return_dict: Dict = None,
                 proc_number: int = None):
    EBGOptimizer(nodes=nodes,
                 matrix=matrix,
                 local_search_metaheuristic=local_search_metaheuristic,
                 first_solution_strategy=first_solution_strategy,
                 max_optimisation_duration=max_optimisation_duration,
                 check_topology=check_topology,
                 connections=connections).optimize(return_dict, proc_number)


def optimize_x_graph(nodes: List,
                     matrix: Dict[str, Dict[str, int]],
                     disjunctions: List[List[int]],
                     local_search_metaheuristic: LocalSearchMetaheuristic,
                     first_solution_strategy: FirstSolutionStrategy,
                     max_optimisation_duration: int,
                     straight_non_straight_maneuver_penalty: int,
                     non_straight_straight_maneuver_penalty: int,
                     return_dict: Dict = None,
                     proc_number: int = None):
    XGraphOptimizer(nodes=nodes,
                    matrix=matrix,
                    disjunctions=disjunctions,
                    local_search_metaheuristic=local_search_metaheuristic,
                    first_solution_strategy=first_solution_strategy,
                    max_optimisation_duration=max_optimisation_duration,
                    straight_non_straight_maneuver_penalty=straight_non_straight_maneuver_penalty,
                    non_straight_straight_maneuver_penalty=non_straight_straight_maneuver_penalty).optimize(return_dict,
                                                                                                            proc_number)
