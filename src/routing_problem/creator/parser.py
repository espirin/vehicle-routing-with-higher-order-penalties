import json
from typing import Dict, List, Tuple

from src.geo.geo import Node, Position, LatLon
from src.osmio.parser import find_osm_nodes_and_ways
from src.routing_problem.maneuver.maneuver import Maneuver
from src.routing_problem.maneuver.maneuver_type import ManeuverType
from src.routing_problem.maneuver.modifier import ManeuverModifier
from src.routing_problem.segment import Segment


class RoutingProblemParser:
    """
    RoutingProblemParser parses routing problems from .osm files.
    """
    
    def __init__(self, path: str):
        self.path: str = path

    def parse(self) -> List[Segment]:
        with open(self.path) as f:
            source = f.read()

        nodes, ways = find_osm_nodes_and_ways(source)
        segments = self.create_segments(ways)
        self.check_geometry(segments)
        self.add_references(segments)

        return segments

    @staticmethod
    def check_geometry(geometries: List[Segment]):
        to_remove = []

        for geometry in geometries:
            # Remove empty geometries
            if len(geometry.nodes) == 0:
                to_remove.append(geometry)

        for geometry in to_remove:
            geometries.remove(geometry)

    @staticmethod
    def add_references(segments: List[Segment]):
        segments_dict = {segment.id: segment for segment in segments}

        for segment in segments:
            for next_segment_id in segment.next_segment_ids:
                if next_segment_id in segments_dict:
                    segment.next_segments.append(segments_dict[next_segment_id])

            for previous_segment_id in segment.previous_segment_ids:
                if previous_segment_id in segments_dict:
                    segment.previous_segments.append(segments_dict[previous_segment_id])

    def create_segments(self, ways: Dict) -> List[Segment]:
        segments = []
        for way in ways.values():
            if "type" in way['attributes']:
                if way['attributes']['type'] == "segment":
                    if 'nodes' in way['attributes']:
                        nodes = [Node(Position(LatLon(lat=node[0], lon=node[1]))) for node in
                                 json.loads(way['attributes']['nodes'])]
                    else:
                        raise Exception(f"No nodes attribute for way: {way}")

                    segment_id, lanes, previous_segments, next_segments, parts, is_forward, connected_component, \
                    next_maneuvers = self.create_segment_attributes(way['attributes'])

                    segment = Segment(segment_id, nodes, lanes, previous_segments, next_segments, parts,
                                      is_forward, connected_component, next_maneuvers)
                    segments.append(segment)
            else:
                raise Exception(f"No type specified for way: {way}")
        return segments

    def create_segment_attributes(self, attributes: Dict):
        segment_id = attributes['segment_id']
        lanes = int(attributes['lanes'])
        previous_segments = attributes['previous_segments'].split(",")
        if '' in previous_segments:
            previous_segments.remove('')
        next_segments = attributes['next_segments'].split(",")
        if '' in next_segments:
            next_segments.remove('')
        parts = int(attributes['parts'])
        is_forward = attributes['is_forward'] == "true"
        connected_component = attributes['component_id']
        next_maneuvers = json.loads(attributes['next_maneuvers'])
        next_maneuvers = self.parse_next_maneuvers(next_maneuvers)

        return segment_id, lanes, previous_segments, next_segments, parts, is_forward, connected_component, \
               next_maneuvers

    @staticmethod
    def parse_next_maneuvers(next_maneuvers: Dict) -> Dict[Tuple[str, str], Maneuver]:
        parsed_maneuvers = dict()
        for maneuver in next_maneuvers:
            maneuver_type = ManeuverType(maneuver['type'])
            modifier = ManeuverModifier(maneuver['modifier'])

            parsed_maneuvers[(maneuver['from']), (maneuver['to'])] = Maneuver(from_id=maneuver['from'],
                                                                              to_id=maneuver['to'],
                                                                              in_angle=maneuver['in_angle'],
                                                                              turn_angle=maneuver['turn_angle'],
                                                                              duration=maneuver['duration'],
                                                                              weight=maneuver['weight'],
                                                                              maneuver_type=maneuver_type,
                                                                              modifier=modifier)

        return parsed_maneuvers
