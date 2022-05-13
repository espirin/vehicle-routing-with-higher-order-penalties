from typing import List, Optional

from geojson import LineString, Feature

from src.entities.figure_with_nodes import FigureWithNodes
from src.geo.geo import Node
from src.json.serialisable import Serialisable
from src.routing_problem.segment import Segment


class Lanelet(FigureWithNodes, Serialisable):
    def __init__(self, nodes: List[Node], lane: int, segment: Segment):
        super().__init__(nodes)
        self.lane: int = lane
        self.segment: Segment = segment

        self.next_lanelets: List[Lanelet] = []
        self.next_lanelet: Optional[Lanelet] = None

    def __str__(self):
        return f"Lanelet {self.segment.id} {self.lane}/{self.segment.lanes}"

    def __repr__(self):
        return self.__str__()

    def to_json(self):
        return Feature(geometry=LineString(coordinates=self.get_coordinates_list(reverse_lat_lon=True)),
                       properties={
                           "lane": self.lane,
                           "previous_segments": self.segment.previous_segment_ids,
                           "next_segments": self.segment.next_segment_ids,
                           "next_segments_sorted": [segment.id for segment in self.segment.next_segments],
                           "id": self.segment.id,
                           "heading head": round(self.segment.heading_head, 1),
                           "heading tail": round(self.segment.heading_tail, 1),
                       })

    def connect_with_next(self, next_lanelet):
        next_lanelet.nodes[0] = self.nodes[-1]
        self.next_lanelet = next_lanelet
