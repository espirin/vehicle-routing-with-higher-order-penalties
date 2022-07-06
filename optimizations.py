import json
from typing import List

from ortools.constraint_solver.routing_enums_pb2 import LocalSearchMetaheuristic, FirstSolutionStrategy

from src.optimiser.lane_topology_optimiser import ConnectionsOptimiser
from src.optimiser.lanelets_optimiser import LaneletsOptimiser
from src.routing_problem.connections.complete import XGraphNode, FirstXGraphNode, LastXGraphNode, SelfXGraphNode
from src.routing_problem.connections.lanelet import LaneletConnection
from src.routing_problem.creator.creator import create_routing_problem
from src.routing_problem.lanelet import FirstLanelet, LastLanelet
from src.routing_problem.maneuver.maneuver_type import ManeuverType
from src.routing_problem.maneuver.modifier import ManeuverModifier
from src.routing_problem.routing_problem import RoutingProblem


def optimize_lane_topology(max_optimisation_duration: int):
    rp_path = "data/stuttgart_small.osm"
    routing_problem: RoutingProblem = create_routing_problem(rp_path)

    maneuvers = dict()
    for segment in routing_problem.segments:
        maneuvers.update(segment.next_maneuvers)

    # Create connections. First for left and right turns, then for forward.
    connections = []
    for segment in routing_problem.segments:
        for previous_segment in segment.previous_segments:
            maneuver = maneuvers[(previous_segment.id, segment.id)]
            left = maneuver.modifier in [ManeuverModifier.Left, ManeuverModifier.SlightLeft,
                                         ManeuverModifier.SharpLeft, ManeuverModifier.UTurn]
            right = maneuver.modifier in [ManeuverModifier.Right, ManeuverModifier.SlightRight,
                                          ManeuverModifier.SharpRight]
            merge = maneuver.type == ManeuverType.Merge
            # Left
            if left and not merge or right and merge:
                for i, lanelet in enumerate(segment.lanelets):
                    if i < len(previous_segment.lanelets):
                        connections.append(LaneletConnection(previous_segment.lanelets[i],
                                                             lanelet,
                                                             maneuver))
            # Right
            elif right and not merge or left and merge:
                for i, lanelet in enumerate(reversed(segment.lanelets)):
                    if i < len(previous_segment.lanelets):
                        connections.append(LaneletConnection(previous_segment.lanelets[-(i + 1)],
                                                             lanelet,
                                                             maneuver))

    # Now connect straights
    for segment in routing_problem.segments:
        for previous_segment in segment.previous_segments:
            maneuver = maneuvers[(previous_segment.id, segment.id)]
            if maneuver.modifier != ManeuverModifier.Straight:
                continue

            lanelets_to = len(segment.lanelets)
            lanelets_from = len(previous_segment.lanelets)
            free_lanelets_to = list(filter(lambda x: not x.has_incoming_connection, segment.lanelets))
            free_lanelets_from = list(filter(lambda x: not x.has_outgoing_connection, previous_segment.lanelets))
            free_lanelets_to_count = len(free_lanelets_to)
            free_lanelets_from_count = len(free_lanelets_from)

            if lanelets_to == lanelets_from:
                for i in range(lanelets_to):
                    connections.append(LaneletConnection(previous_segment.lanelets[i],
                                                         segment.lanelets[i],
                                                         maneuver))
            elif free_lanelets_to_count == lanelets_from:
                for i in range(free_lanelets_to_count):
                    connections.append(LaneletConnection(previous_segment.lanelets[i],
                                                         free_lanelets_to[i],
                                                         maneuver))
            elif lanelets_to == free_lanelets_from_count:
                for i in range(lanelets_to):
                    connections.append(LaneletConnection(free_lanelets_from[i],
                                                         segment.lanelets[i],
                                                         maneuver))
            elif lanelets_to > free_lanelets_from_count:
                for i in range(lanelets_to):
                    connections.append(LaneletConnection(free_lanelets_from[min(i, free_lanelets_from_count - 1)],
                                                         segment.lanelets[i],
                                                         maneuver))
            elif lanelets_to < free_lanelets_from_count:
                for i in range(free_lanelets_from_count):
                    connections.append(LaneletConnection(free_lanelets_from[i],
                                                         segment.lanelets[min(i, lanelets_to - 1)],
                                                         maneuver))

    with open("data/matrix.json") as f:
        matrix = json.load(f)

    lanelet_connections = {(connection.lanelet_from, connection.lanelet_to) for connection in connections}
    optimiser = LaneletsOptimiser(lanelets=[FirstLanelet()] + routing_problem.lanelets + [LastLanelet()],
                                  matrix=matrix,
                                  local_search_metaheuristic=LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH,
                                  first_solution_strategy=FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION,
                                  max_optimisation_duration=max_optimisation_duration,
                                  connections=lanelet_connections,
                                  check_topology=True)
    optimal_order, optimization_history = optimiser.optimize()
    print("Lane topology:")
    print(f"Optimisation history: {optimization_history}")

    return optimal_order


def optimize_x_graph(max_optimisation_duration: int,
                     straight_non_straight_maneuver_penalty: int = 600,
                     non_straight_straight_maneuver_penalty: int = 200,
                     print_history: bool = True):
    rp_path = "data/stuttgart_small.osm"
    routing_problem: RoutingProblem = create_routing_problem(rp_path)

    maneuvers = dict()
    for segment in routing_problem.segments:
        maneuvers.update(segment.next_maneuvers)

    complete_connections: List[XGraphNode] = [FirstXGraphNode()]
    disjunctions: List[List[int]] = []

    for lanelet_to in routing_problem.lanelets:
        disjunctions.append([])
        segment_to = lanelet_to.segment

        for lanelet_from in routing_problem.lanelets:
            segment_from = lanelet_from.segment

            if (segment_from.id, segment_to.id) in maneuvers:
                maneuver = maneuvers[(segment_from.id, segment_to.id)]

                complete_connections.append(XGraphNode(lanelet_from=lanelet_from,
                                                       lanelet_to=lanelet_to,
                                                       maneuver=maneuver))
                disjunctions[-1].append(len(complete_connections) - 1)

        if len(disjunctions[-1]) == 0:
            disjunctions = disjunctions[:-1]
            complete_connections.append(SelfXGraphNode(lanelet_to))

    complete_connections.append(LastXGraphNode())

    with open("data/matrix.json") as f:
        matrix = json.load(f)

    optimiser = ConnectionsOptimiser(connections=complete_connections,
                                     disjunctions=[],
                                     matrix=matrix,
                                     local_search_metaheuristic=LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH,
                                     first_solution_strategy=FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION,
                                     max_optimisation_duration=max_optimisation_duration,
                                     straight_non_straight_maneuver_penalty=straight_non_straight_maneuver_penalty,
                                     non_straight_straight_maneuver_penalty=non_straight_straight_maneuver_penalty)
    optimal_order, optimization_history = optimiser.optimize()

    print("X-Graph")
    if print_history:
        print(f"Optimisation history: {optimization_history}")

    return optimal_order


def optimize_normal(max_optimisation_duration):
    rp_path = "data/stuttgart_small.osm"
    routing_problem: RoutingProblem = create_routing_problem(rp_path)

    with open("data/matrix.json") as f:
        matrix = json.load(f)

    optimiser = LaneletsOptimiser(lanelets=[FirstLanelet()] + routing_problem.lanelets + [LastLanelet()],
                                  matrix=matrix,
                                  local_search_metaheuristic=LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH,
                                  first_solution_strategy=FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION,
                                  max_optimisation_duration=max_optimisation_duration,
                                  connections=set(),
                                  check_topology=False)
    optimal_order, optimization_history = optimiser.optimize()

    print("Normal")
    print(f"Optimisation history: {optimization_history}")

    return optimal_order
