from typing import List

from src.entities.figure_with_nodes import FigureWithNodes
from src.geo.geo import Node


class Segment(FigureWithNodes):
    def __init__(self, segment_id: str, nodes: List[Node], lanes: int, previous_segments: List[str],
                 next_segments: List[str], parts: int, is_forward: bool, connected_component: str):
        super().__init__(nodes)
        self.id: str = segment_id
        self.lanes: int = lanes
        self.previous_segments: List[str] = previous_segments
        self.next_segments: List[str] = next_segments
        self.parts: int = parts
        self.is_forward: bool = is_forward
        self.connected_component: str = connected_component

    def __str__(self):
        return f"Segment {self.id}"

    def __repr__(self):
        return self.__str__()
