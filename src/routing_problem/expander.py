from typing import List

from src.geometry.geometry import offset_nodes
from src.routing_problem.lanelet import Lanelet
from src.routing_problem.segment import Segment


def create_lanelets(rp_segments: List[Segment]) -> List[Lanelet]:
    lanelets = []

    for segment in rp_segments:
        for i in range(segment.lanes):
            lanelet = Lanelet(nodes=offset_nodes(nodes=segment.nodes,
                                                 distance=1.5 * (i + 1)),
                              lane=i,
                              segment=segment)
            lanelets.append(lanelet)
            segment.lanelets.append(lanelet)

    for lanelet in lanelets:
        next_lanelets = []
        for next_segment in lanelet.segment.next_segments:
            next_lanelets += next_segment.lanelets

        lanelet.next_lanelets = next_lanelets

    return lanelets
