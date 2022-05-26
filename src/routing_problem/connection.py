from geojson import Feature, LineString

from src.entities.figure_with_nodes import FigureWithNodes
from src.json.serialisable import Serialisable
from src.routing_problem.lanelet import Lanelet
from src.routing_problem.maneuver.maneuver import Maneuver


class LaneletConnection(Serialisable, FigureWithNodes):
    def __init__(self, lanelet_from: Lanelet, lanelet_to: Lanelet, maneuver: Maneuver):
        super().__init__(nodes=[lanelet_from.nodes[-1], lanelet_to.nodes[0]])
        self.lanelet_from: Lanelet = lanelet_from
        self.lanelet_to: Lanelet = lanelet_to
        self.maneuver: Maneuver = maneuver

        lanelet_to.has_incoming_connection = True
        lanelet_from.has_outgoing_connection = True

    def to_json(self):
        return Feature(geometry=LineString(coordinates=self.get_coordinates_list(reverse_lat_lon=True)),
                       properties={
                           "modifier": self.maneuver.modifier.name,
                           "maneuver type": self.maneuver.type.name,
                           "segment_from": self.lanelet_from.segment.id,
                           "segment_to": self.lanelet_to.segment.id,
                           "type": 1
                       })

    def __str__(self):
        return f"LaneletConnection {self.lanelet_from.segment.id} -> {self.lanelet_to.segment.id}"

    def __repr__(self):
        return self.__str__()
