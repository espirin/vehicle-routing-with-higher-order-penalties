from typing import List, Optional, Dict, Set

from geojson import LineString, Feature

from src.config import OPTIMISER_INFINITY
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
        self.previous_lanelets: List[Lanelet] = []

        self.has_incoming_connection: bool = False
        self.has_outgoing_connection: bool = False

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
                           "next_maneuvers": [f"{maneuver.type.name} -> {to_id}" for (_, to_id), maneuver in
                                              self.segment.next_maneuvers.items()],
                           "id": self.segment.id,
                           "length": round(self.get_length()),
                           "type": 0
                       })

    def get_cost_to(self, lanelet, matrix: Dict[str, Dict[str, int]],
                    lanelet_connections: Set, check_topology: bool = True) -> int:
        if isinstance(lanelet, LastLanelet):
            return 0

        if check_topology:
            # If pair is connected, check lanelet connections
            if lanelet.segment.id in self.segment.next_segment_ids:
                if (self, lanelet) in lanelet_connections:
                    return 0
                else:
                    return OPTIMISER_INFINITY

            # If not, check if it's the same segment
            if self.segment.id == lanelet.segment.id:
                return OPTIMISER_INFINITY

            # Penalize for not choosing an existing connection
            if self.has_outgoing_connection:
                return matrix[self.segment.id][lanelet.segment.id] + 300

        return matrix[self.segment.id][lanelet.segment.id]


class FirstLanelet(Lanelet):
    def __init__(self):
        super().__init__([], 0, None)

    def get_cost_to(self, lanelet, matrix: Dict[str, Dict[str, int]],
                    lanelet_connections: Set, check_topology: bool = True) -> int:
        return 0


class LastLanelet(Lanelet):
    def __init__(self):
        super().__init__([], 0, None)
