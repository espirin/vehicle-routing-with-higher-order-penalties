import json
from multiprocessing import Process
from typing import List

from ortools.constraint_solver.routing_enums_pb2 import FirstSolutionStrategy, LocalSearchMetaheuristic

from src.optimiser.lane_topology_optimiser import ConnectionsOptimiser
from src.routing_problem.connections.complete import XGraphNode, LastXGraphNode, FirstXGraphNode
from src.routing_problem.creator.creator import create_routing_problem
from src.routing_problem.routing_problem import RoutingProblem

rp_path = "data/stuttgart_small.osm"


def optimize(solution_strategy, first_solution_strategy, duration):
    routing_problem: RoutingProblem = create_routing_problem(rp_path)

    with open("data/matrix.json") as f:
        matrix = json.load(f)

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

            # Remove or len(segment_to.previous_segments) == 0:
            if (segment_from.id, segment_to.id) in maneuvers or len(segment_to.previous_segments) == 0:
                maneuver = maneuvers[(segment_from.id, segment_to.id)] if (segment_from.id,
                                                                           segment_to.id) in maneuvers else None

                complete_connections.append(XGraphNode(lanelet_from=lanelet_from,
                                                       lanelet_to=lanelet_to,
                                                       maneuver=maneuver))
                disjunctions[-1].append(len(complete_connections) - 1)

    complete_connections.append(LastXGraphNode())

    optimiser = ConnectionsOptimiser(connections=complete_connections,
                                     disjunctions=disjunctions,
                                     matrix=matrix,
                                     local_search_metaheuristic=solution_strategy,
                                     first_solution_strategy=first_solution_strategy,
                                     max_optimisation_duration=duration)
    optimal_order, optimization_history = optimiser.optimize()
    print(f"{first_solution_strategy} - Optimisation history: {optimization_history}")
    # optimal_order = optimal_order[1:-1]


if __name__ == '__main__':
    procs = []
    p1 = Process(target=optimize, args=(LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH, FirstSolutionStrategy.AUTOMATIC,  20))
    p1.start()
    procs.append(p1)

    p2 = Process(target=optimize, args=(LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH, FirstSolutionStrategy.PATH_CHEAPEST_ARC,  20))
    p2.start()
    procs.append(p2)

    p3 = Process(target=optimize, args=(LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH, FirstSolutionStrategy.SAVINGS,  20))
    p3.start()
    procs.append(p3)

    p6 = Process(target=optimize, args=(LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH, FirstSolutionStrategy.CHRISTOFIDES,  20))
    p6.start()
    procs.append(p6)

    p7 = Process(target=optimize, args=(LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH, FirstSolutionStrategy.ALL_UNPERFORMED,  20))
    p7.start()
    procs.append(p7)

    p8 = Process(target=optimize, args=(LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH, FirstSolutionStrategy.BEST_INSERTION,  20))
    p8.start()
    procs.append(p8)

    p9 = Process(target=optimize, args=(LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH, FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION,  20))
    p9.start()
    procs.append(p9)

    p10 = Process(target=optimize, args=(LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH, FirstSolutionStrategy.LOCAL_CHEAPEST_INSERTION,  20))
    p10.start()
    procs.append(p10)

    p11 = Process(target=optimize, args=(LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH, FirstSolutionStrategy.GLOBAL_CHEAPEST_ARC,  20))
    p11.start()
    procs.append(p11)

    p12 = Process(target=optimize, args=(LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH, FirstSolutionStrategy.LOCAL_CHEAPEST_ARC,  20))
    p12.start()
    procs.append(p12)

    p13 = Process(target=optimize, args=(LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH, FirstSolutionStrategy.FIRST_UNBOUND_MIN_VALUE,  20))
    p13.start()
    procs.append(p13)

    print(f"AUTOMATIC - {FirstSolutionStrategy.AUTOMATIC}")
    print(f"PATH_CHEAPEST_ARC - {FirstSolutionStrategy.PATH_CHEAPEST_ARC}")
    print(f"SAVINGS - {FirstSolutionStrategy.SAVINGS}")
    print(f"CHRISTOFIDES - {FirstSolutionStrategy.CHRISTOFIDES}")
    print(f"ALL_UNPERFORMED - {FirstSolutionStrategy.ALL_UNPERFORMED}")
    print(f"BEST_INSERTION - {FirstSolutionStrategy.BEST_INSERTION}")
    print(f"PARALLEL_CHEAPEST_INSERTION - {FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION}")
    print(f"LOCAL_CHEAPEST_INSERTION - {FirstSolutionStrategy.LOCAL_CHEAPEST_INSERTION}")
    print(f"GLOBAL_CHEAPEST_ARC - {FirstSolutionStrategy.GLOBAL_CHEAPEST_ARC}")
    print(f"LOCAL_CHEAPEST_ARC - {FirstSolutionStrategy.LOCAL_CHEAPEST_ARC}")
    print(f"FIRST_UNBOUND_MIN_VALUE - {FirstSolutionStrategy.FIRST_UNBOUND_MIN_VALUE}")

    for p in procs:
        p.join()
