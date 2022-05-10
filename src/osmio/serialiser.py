from typing import Dict

from lxml import etree

from src.geometry.geometry import offset_nodes


def serialize_route_to_osm(route, visual_offset=False) -> str:
    if visual_offset:
        raise Exception("Not implemented")

    root = etree.Element("osm", version="0.6", generator="JOSM")  # Header of the main route file

    # Add nodes
    node_counter = -1
    visited_segments = dict()
    nodes_mapping = dict()
    for step in route.route_steps:
        if step.segment_id in visited_segments and visual_offset:
            nodes = offset_nodes([node for node in route.segments[step.segment_id].nodes],
                                 distance=visited_segments[step.segment_id] * 3)
            visited_segments[step.segment_id] += 1
        else:
            nodes = [node for node in route.segments[step.segment_id].nodes]
            visited_segments[step.segment_id] = 1
        nodes_mapping[step] = len(nodes)

        for node in nodes:
            node = etree.Element("node", id=str(node_counter),
                                 lon=str(node.position.latlon.lon),
                                 lat=str(node.position.latlon.lat))
            root.append(node)
            node_counter -= 1

    # Add ways
    node_counter = -1
    way_counter = -1
    for step in route.route_steps:
        way = etree.Element("way", id=str(way_counter), action='modify', visible='true')
        if node_counter < -1:
            nd = etree.Element("nd", ref=str(node_counter + 1))
            way.append(nd)
        for i in range(nodes_mapping[step]):
            nd = etree.Element("nd", ref=str(node_counter))
            way.append(nd)
            node_counter -= 1

        for attribute, value in step.to_json().items():
            way.append(etree.Element("tag", k=str(attribute), v=str(value)))
        if step.maneuver_id in route.maneuvers:
            for attribute, value in route.maneuvers[step.maneuver_id].to_json().items():
                way.append(etree.Element("tag", k=str(attribute), v=str(value)))

        root.append(way)
        way_counter -= 1

    # Create source
    source = "<?xml version='1.0' encoding='UTF-8'?>\n" + etree.tostring(root, pretty_print=True).decode('utf-8')
    return source


def serialize_nodes_and_ways_to_osm(nodes: Dict, ways: Dict) -> str:
    root = etree.Element("osm", version="0.6", generator="JOSM")  # Header of the main route file

    way_counter = -1
    node_counter = -1 - len(ways)
    for way in ways.values():
        new_way = etree.Element("way", id=str(way_counter), action='modify', visible='true')
        way_counter -= 1
        for node in way['nodes']:
            nd = etree.Element("nd", ref=str(node_counter))
            node_counter -= 1
            new_way.append(nd)

        for attribute, value in way['attributes'].items():
            new_way.append(etree.Element("tag", k=str(attribute), v=str(value)))

        root.append(new_way)

    node_counter = -1 - len(ways)
    for way in ways.values():
        for node_id in way['nodes']:
            node = nodes[node_id]
            nd = etree.Element("node", id=str(node_counter), lon=str(node.position.latlon.lon),
                               lat=str(node.position.latlon.lat))
            node_counter -= 1
            for attribute, value in node.attributes.items():
                nd.append(etree.Element("tag", k=str(attribute), v=str(value)))
            root.append(nd)

    # Create source
    source = "<?xml version='1.0' encoding='UTF-8'?>\n" + etree.tostring(root, pretty_print=True).decode('utf-8')

    return source
