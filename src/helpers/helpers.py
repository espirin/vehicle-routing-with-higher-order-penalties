from typing import List, Dict

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
