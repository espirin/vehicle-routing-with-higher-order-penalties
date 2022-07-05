import time
from multiprocessing import Process

from optimizations import optimize_x_graph
from src.osrm.interface import OSRMInterface
from src.routing_problem.creator.creator import create_routing_problem
from src.routing_problem.maneuver.modifier import ManeuverModifier
from src.routing_problem.routing_problem import RoutingProblem


def calculate_asl(order):
    rp_path = "data/stuttgart_small.osm"
    routing_problem: RoutingProblem = create_routing_problem(rp_path)

    maneuvers = dict()
    for segment in routing_problem.segments:
        maneuvers.update(segment.next_maneuvers)

    straights = []
    previous_lanelet = None
    current_straight = 0

    for lanelet in order:
        if previous_lanelet is None:
            previous_lanelet = lanelet
            continue

        if (previous_lanelet.segment.id, lanelet.segment.id) in maneuvers:
            maneuver = maneuvers[(previous_lanelet.segment.id, lanelet.segment.id)]

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

    average_straight_length = sum(straights) / len(straights)
    print(f"Average straight length: {round(average_straight_length, 1)}")


def optimize_and_get_route(max_optimisation_duration: int,
                           straight_non_straight_maneuver_penalty: int,
                           non_straight_straight_maneuver_penalty: int):
    order = optimize_x_graph(max_optimisation_duration=max_optimisation_duration,
                             straight_non_straight_maneuver_penalty=straight_non_straight_maneuver_penalty,
                             non_straight_straight_maneuver_penalty=non_straight_straight_maneuver_penalty,
                             print_history=False)

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

    segments = [lanelet.segment for lanelet in shortened_x_graph_order]
    route = OSRMInterface.request_route(segments, "Stuttgart/stuttgart-regbez-latest.osrm")
    print(f"s->ns: {straight_non_straight_maneuver_penalty} ns->s: {non_straight_straight_maneuver_penalty}")
    print(f"Duration: {route['original_route']['routes'][0]['duration']} s")
    print(f"Distance: {route['original_route']['routes'][0]['distance']} m")
    calculate_asl(shortened_x_graph_order)
    print("*************************************")


if __name__ == '__main__':
    procs = []
    p1 = Process(target=optimize_and_get_route,
                 args=(400, 600, 300))
    p1.start()
    procs.append(p1)
    time.sleep(1.5)

    p2 = Process(target=optimize_and_get_route,
                 args=(400, 400, 200))
    p2.start()
    procs.append(p2)
    time.sleep(1.5)

    p3 = Process(target=optimize_and_get_route,
                 args=(400, 200, 200))
    p3.start()
    procs.append(p3)
    time.sleep(1.5)

    p4 = Process(target=optimize_and_get_route,
                 args=(400, 200, 100))
    p4.start()
    procs.append(p4)
    time.sleep(1.5)

    p5 = Process(target=optimize_and_get_route,
                 args=(400, 100, 50))
    p5.start()
    procs.append(p5)
    time.sleep(1.5)

    p6 = Process(target=optimize_and_get_route,
                 args=(400, 120, 40))
    p6.start()
    procs.append(p6)
    time.sleep(1.5)

    p7 = Process(target=optimize_and_get_route,
                 args=(400, 120, 0))
    p7.start()
    procs.append(p7)
    time.sleep(1.5)

    for p in procs:
        p.join()
