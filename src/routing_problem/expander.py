from typing import List

from src.geometry.geometry import offset_nodes
from src.routing_problem.lanelet import Lanelet
from src.routing_problem.segment import Segment


def create_lanelets(rp_segments: List[Segment]) -> List[Lanelet]:
    lanelets = []

    for segment in rp_segments:
        for i in range(segment.lanes):
            lanelets.append(Lanelet(nodes=offset_nodes(nodes=segment.nodes,
                                                       distance=3 * (i + 1)),
                                    lane=i,
                                    segment=segment))

    return lanelets
