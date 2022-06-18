from geojson import Feature, LineString

from src.entities.figure_with_nodes import FigureWithNodes
from src.json.serialisable import Serialisable
from src.routing_problem.lanelet import Lanelet


class RouteConnection(Serialisable, FigureWithNodes):
    def __init__(self, lanelet_from: Lanelet, lanelet_to: Lanelet, cost: int, type_: int):
        super().__init__(nodes=[lanelet_from.nodes[-1], lanelet_to.nodes[0]])
        self.lanelet_from: Lanelet = lanelet_from
        self.lanelet_to: Lanelet = lanelet_to

        self.cost: int = cost
        self.type = type_

    def to_json(self):
        return Feature(geometry=LineString(coordinates=self.get_coordinates_list(reverse_lat_lon=True)),
                       properties={
                           "weight": self.cost,
                           "segment_from": self.lanelet_from.segment.id,
                           "segment_to": self.lanelet_to.segment.id,
                           "type": self.type
                       })

    def __str__(self):
        return f"RouteConnection {self.lanelet_from.segment.id} -> {self.lanelet_to.segment.id}"

    def __repr__(self):
        return self.__str__()
