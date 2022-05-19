import json
import traceback
from typing import Dict, List

from src.geo.geo import Node, Position, LatLon
from src.osmio.parser import find_osm_nodes_and_ways
from src.routing_problem.segment import Segment


class RoutingProblemParser:
    def __init__(self, path: str):
        self.path: str = path

    def parse(self) -> List[Segment]:
        with open(self.path) as f:
            source = f.read()

        nodes, ways = find_osm_nodes_and_ways(source)
        segments = self.create_segments(ways)
        self.check_geometry(segments)
        self.add_references(segments)
        self.sort_next_segments(segments)

        return segments

    @staticmethod
    def sort_next_segments(segments: List[Segment]):
        for segment in segments:
            segment.next_segments_left, segment.next_segments_forward, segment.next_segments_right = segment.sort_next_segments()

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
                    try:
                        segment_id, lanes, previous_segments, next_segments, parts, is_forward, connected_component = \
                            self.create_segment_attributes(way['attributes'])
                    except Exception:
                        tb = traceback.format_exc()
                        raise Exception(f"{tb} Either segment_id or lanes attribute is missing for segment "
                                        f"{way['attributes']['segment_id'] if 'segment_id' in way['attributes'] else way['attributes']}")

                    segment = Segment(segment_id, nodes, lanes, previous_segments, next_segments, parts,
                                      is_forward, connected_component)
                    segments.append(segment)
            else:
                raise Exception(f"No type specified for way: {way}")
        return segments

    @staticmethod
    def create_segment_attributes(attributes: Dict):
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

        return segment_id, lanes, previous_segments, next_segments, parts, is_forward, connected_component
