from typing import List, Dict, Tuple

from geojson import FeatureCollection
from mapboxgl import LinestringViz

from src.abstract.serialisable import Serialisable
from src.config.map import satellite_style
from src.geometry.geometry import shorten_line
from src.routing_problem.lanelet import Lanelet
from src.routing_problem.maneuver.maneuver import Maneuver
from src.routing_problem.segment import Segment


class RoutingProblem(Serialisable):
    """
    RoutingProblem is a road network that needs to be recorded.

    It is created with the help of Atlatec's proprietary OSRM fork.
    """

    def __init__(self, lanelets: List[Lanelet], segments: List[Segment]):
        self.lanelets: List[Lanelet] = lanelets
        self.segments: List[Segment] = segments

        # Generated attributes
        self.center: List[float] = self.calculate_center_coordinates(segments)
        self.maneuvers: Dict[Tuple[str, str], Maneuver] = self.create_maneuvers()
        self.average_branching_factor: float = self.calculate_average_branching_factor()
        self.nbg_nodes_number: int = self.calculate_nbg_nodes_number()

    def to_json(self):
        return [lanelet.to_json() for lanelet in self.lanelets]

    @staticmethod
    def calculate_center_coordinates(segments: List[Segment]) -> List[float]:
        nodes = [node for segment in segments for node in segment.nodes]
        east = max(nodes, key=lambda node: node.position.latlon.lon)
        west = min(nodes, key=lambda node: node.position.latlon.lon)
        north = max(nodes, key=lambda node: node.position.latlon.lat)
        south = min(nodes, key=lambda node: node.position.latlon.lat)

        return [(east.position.latlon.lon + west.position.latlon.lon) / 2,
                (north.position.latlon.lat + south.position.latlon.lat) / 2]

    def shorten_lanelets(self):
        for lanelet in self.lanelets:
            if lanelet.get_length() > 50:
                lanelet.nodes = shorten_line(lanelet.nodes, 12, cut_beginning=True)
                lanelet.nodes = shorten_line(lanelet.nodes, 20, cut_beginning=False)
            elif lanelet.get_length() > 30:
                lanelet.nodes = shorten_line(lanelet.nodes, 5, cut_beginning=True)
                lanelet.nodes = shorten_line(lanelet.nodes, 5, cut_beginning=False)
            elif lanelet.get_length() > 10:
                lanelet.nodes = shorten_line(lanelet.nodes, 3, cut_beginning=True)
                lanelet.nodes = shorten_line(lanelet.nodes, 3, cut_beginning=False)
            elif lanelet.get_length() > 5:
                lanelet.nodes = shorten_line(lanelet.nodes, 1, cut_beginning=True)
                lanelet.nodes = shorten_line(lanelet.nodes, 1, cut_beginning=False)

    def create_maneuvers(self) -> Dict[Tuple[str, str], Maneuver]:
        maneuvers = {}
        for segment in self.segments:
            maneuvers.update(segment.next_maneuvers)

        return maneuvers

    def visualize(self, zoom=14):
        geojson = FeatureCollection(features=self.to_json())

        viz = LinestringViz(data=geojson,
                            color_default="#3ad21b",
                            line_width_default='2',
                            center=self.center,
                            zoom=zoom,
                            style=satellite_style)

        return viz.show()

    def calculate_average_branching_factor(self) -> float:
        branches = 0
        for lanelet in self.lanelets:
            for next_segment in lanelet.segment.next_segments:
                branches += len(next_segment.lanelets)

        return branches / len(self.lanelets)

    def calculate_nbg_nodes_number(self) -> int:
        nodes_count = 0
        for lanelet in self.lanelets:
            for _ in lanelet.segment.nodes:
                nodes_count += 1

        return nodes_count
