from typing import List

from src.entities.figure_with_nodes import FigureWithNodes
from src.geo.geo import Node
from src.geometry.geometry import get_heading


class Segment(FigureWithNodes):
    def __init__(self, segment_id: str, nodes: List[Node], lanes: int, previous_segments_ids: List[str],
                 next_segment_ids: List[str], parts: int, is_forward: bool, connected_component: str):
        super().__init__(nodes)
        self.id: str = segment_id
        self.lanes: int = lanes
        self.previous_segment_ids: List[str] = previous_segments_ids
        self.next_segment_ids: List[str] = next_segment_ids
        self.parts: int = parts
        self.is_forward: bool = is_forward
        self.connected_component: str = connected_component

        self.next_segments: List[Segment] = []
        self.previous_segments: List[Segment] = []

        self.heading_tail = get_heading(self.nodes[:2])
        self.heading_head = get_heading(self.nodes[-2:])

        self.lanelets: List = []

    def __str__(self):
        return f"Segment {self.id}"

    def __repr__(self):
        return self.__str__()

    def sort_next_segments(self):
        # Get next segments sorted by direction from left to right
        opposite_heading = self.heading_head - 180
        if opposite_heading < 0:
            opposite_heading = 360 + opposite_heading

        if self.heading_head <= 180:
            right_segments = list(filter(lambda segment: self.heading_head <= segment.heading_tail <= opposite_heading,
                                         self.next_segments))

            right_segments.sort(key=lambda segment: segment.heading_tail)
            left_segments = list(filter(lambda segment: 0 <= segment.heading_tail < self.heading_head or
                                                        opposite_heading < segment.heading_tail <= 360,
                                        self.next_segments))
            left_segments.sort(key=lambda segment: segment.heading_tail if segment.heading_tail > opposite_heading
            else segment.heading_tail + 360)
        else:
            left_segments = list(filter(lambda segment: opposite_heading <= segment.heading_tail <= self.heading_head,
                                        self.next_segments))
            left_segments.sort(key=lambda segment: segment.heading_tail)
            right_segments = list(filter(lambda segment: self.heading_head < segment.heading_tail <= 360 or
                                                         0 <= segment.heading_tail < opposite_heading,
                                         self.next_segments))
            right_segments.sort(key=lambda segment: segment.heading_tail if segment.heading_tail > self.heading_head
            else segment.heading_tail + 360)

        self.next_segments = left_segments + right_segments
