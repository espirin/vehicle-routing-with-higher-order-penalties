from typing import List, Dict, Tuple

from src.entities.figure_with_nodes import FigureWithNodes
from src.geo.geo import Node
from src.routing_problem.maneuver.maneuver import Maneuver


class Segment(FigureWithNodes):
    def __init__(self, segment_id: str, nodes: List[Node], lanes: int, previous_segments_ids: List[str],
                 next_segment_ids: List[str], parts: int, is_forward: bool, connected_component: str,
                 next_maneuvers: Dict[Tuple[str, str], Maneuver]):
        super().__init__(nodes)
        self.id: str = segment_id
        self.lanes: int = lanes
        self.previous_segment_ids: List[str] = previous_segments_ids
        self.next_segment_ids: List[str] = next_segment_ids
        self.parts: int = parts
        self.is_forward: bool = is_forward
        self.connected_component: str = connected_component
        self.next_maneuvers: Dict[Tuple[str, str], Maneuver] = next_maneuvers

        self.next_segments: List[Segment] = []
        self.previous_segments: List[Segment] = []

        self.lanelets: List = []

    def __str__(self):
        return f"Segment {self.id}"

    def __repr__(self):
        return self.__str__()
