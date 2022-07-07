import xml.etree.ElementTree as xml
from typing import Tuple, Dict

from src.geo.geo import Node, LatLon, Position


def find_osm_nodes_and_ways(source: str) -> Tuple[Dict[int, Node], Dict[int, Dict]]:
    # Parse xml file, find OSM nodes and ways

    tree = xml.fromstring(source)

    nodes = {}
    ways = {}
    for element in tree:
        # Nodes
        if element.tag == "node":
            nodes[int(element.attrib["id"])] = Node(Position(latlon=LatLon(lat=float(element.attrib["lat"]),
                                                                           lon=float(element.attrib["lon"]))))
            for child in element:
                if child.tag == "tag":
                    nodes[int(element.attrib["id"])].attributes[child.attrib['k']] = child.attrib['v']

        # Ways
        elif element.tag == "way":
            element_id = int(element.attrib["id"])
            ways[element_id] = {'nodes': [], 'attributes': {}}
            for child in element:
                if child.tag == "nd":
                    child_id = int(child.attrib["ref"])
                    ways[element_id]['nodes'].append(child_id)
                if child.tag == "tag":
                    ways[element_id]['attributes'][child.attrib["k"]] = child.attrib["v"]

    return nodes, ways
