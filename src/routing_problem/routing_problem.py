from typing import List

from src.abstract.serialisable import Serialisable
from src.routing_problem.lanelet import Lanelet
from src.routing_problem.segment import Segment


class RoutingProblem(Serialisable):
    """
    RoutingProblem is a road network that needs to be recorded.

    It is created with the help of Atlatec's proprietary OSRM fork.
    """

    def __init__(self, lanelets: List[Lanelet], segments: List[Segment]):
        self.lanelets: List[Lanelet] = lanelets
        self.segments: List[Segment] = segments

    def to_json(self):
        return [lanelet.to_json() for lanelet in self.lanelets]
