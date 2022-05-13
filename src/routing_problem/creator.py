from src.routing_problem.expander import create_lanelets
from src.routing_problem.parser import RoutingProblemParser
from src.routing_problem.routing_problem import RoutingProblem


def create_routing_problem(path: str) -> RoutingProblem:
    # Parse routing problem
    parser = RoutingProblemParser(path)
    segments = parser.parse()

    # Create lanelets by expanding segments
    lanelets = create_lanelets(segments)

    return RoutingProblem(lanelets, segments)
