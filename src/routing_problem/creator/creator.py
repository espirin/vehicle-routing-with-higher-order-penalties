from typing import List

from src.geometry.geometry import offset_nodes
from src.routing_problem.creator.parser import RoutingProblemParser
from src.routing_problem.lanelet import Lanelet
from src.routing_problem.routing_problem import RoutingProblem
from src.routing_problem.segment import Segment


def create_routing_problem(path: str) -> RoutingProblem:
    # Parse routing problem
    parser = RoutingProblemParser(path)
    segments = parser.parse()

    # Create lanelets by expanding segments
    lanelets = create_lanelets(segments)

    return RoutingProblem(lanelets, segments)


def create_lanelets(rp_segments: List[Segment]) -> List[Lanelet]:
    lanelets = []

    # Expand RP segments into lanelets
    for segment in rp_segments:
        for i in range(segment.lanes):
            lanelet = Lanelet(nodes=offset_nodes(nodes=segment.nodes,
                                                 distance=1.5 * (i + 1)),
                              lane=i,
                              segment=segment)
            lanelets.append(lanelet)
            segment.lanelets.append(lanelet)

    return lanelets
