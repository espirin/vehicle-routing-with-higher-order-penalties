from typing import List

from src.entities.figure_with_nodes import FigureWithNodes
from src.geo.geo import Node
from src.routing_problem.segment import Segment


class Lanelet(FigureWithNodes):
    def __init__(self, nodes: List[Node], lane: int, segment: Segment):
        super().__init__(nodes)
        self.lane: int = lane
        self.segment: Segment = segment

    def __str__(self):
        return f"Lanelet {self.segment.id} {self.lane}/{self.segment.lanes}"

    def __repr__(self):
        return self.__str__()
