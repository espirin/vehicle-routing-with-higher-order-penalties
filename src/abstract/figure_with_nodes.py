from abc import ABC
from typing import List

from shapely.geometry import LineString
from utm import latlon_to_zone_number

from src.geo.geo import Node


class FigureWithNodes(ABC):
    """
    FigureWithNodes represents any geospatial figure that has nodes. E.g. segment.
    """

    def __init__(self, nodes: List[Node]):
        self.nodes = nodes
        self.original_nodes = nodes

    def get_length(self) -> float:
        # Convert lat, lon to UTM coordinates
        utm_zone_number = latlon_to_zone_number(self.original_nodes[0].position.latlon.lat,
                                                self.original_nodes[0].position.latlon.lon)
        nodes = []
        for node in self.original_nodes:
            utm = node.position.get_utm_with_forced_zone(utm_zone_number)
            nodes.append([utm.north, utm.east])

        line = LineString(nodes)
        return line.length

    def get_coordinates_list(self, reverse_lat_lon=False):
        if reverse_lat_lon:
            return [[node.position.latlon.lon, node.position.latlon.lat] for node in self.nodes]
        return [[node.position.latlon.lat, node.position.latlon.lon] for node in self.nodes]
