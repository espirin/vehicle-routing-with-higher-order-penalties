from typing import List, Optional

from shapely.geometry import LineString, Point
from utm import latlon_to_zone_number

from src.geo.geo import Node, Position, UTM, LatLon


def create_linestring(nodes: List[Node]) -> LineString:
    utm_zone_number = latlon_to_zone_number(nodes[0].position.latlon.lat, nodes[0].position.latlon.lon)

    utm_nodes = []
    for node in nodes:
        utm = node.position.get_utm_with_forced_zone(utm_zone_number)
        utm_nodes.append([utm.north, utm.east])
    line_string = LineString(utm_nodes)

    return line_string


def create_nodes(line_string: LineString, zone_latlon: LatLon) -> Optional[List[Node]]:
    try:
        utm_coordinates = list(line_string.coords)
    except NotImplementedError:
        return None

    nodes = []
    for north, east in utm_coordinates:
        node = Node(Position(utm=UTM(north=north, east=east), zone_latlon=zone_latlon))
        nodes.append(node)

    return nodes


def offset_nodes(nodes: List[Node], distance=3, side='left', resolution=16, join_style=1) -> List[Node]:
    line_string = create_linestring(nodes)

    offsetted_utm_string = line_string.parallel_offset(distance=distance, side=side, resolution=resolution,
                                                       join_style=join_style)

    offsetted_nodes = create_nodes(offsetted_utm_string, nodes[0].position.latlon)
    # Right hand offsets are returned in the reverse direction of the original LineString or LineRing,
    # while left side offsets flow in the same direction.
    if side == 'right':
        offsetted_nodes.reverse()

    return offsetted_nodes


def cut_line(line: LineString, distance: float):
    # Cut a line in two at a given distance from its starting point
    if distance <= 0.0:
        return None, line

    if distance >= line.length:
        return line, None

    coords = list(line.coords)
    for i, p in enumerate(coords):
        pd = line.project(Point(p))
        if pd == distance:
            return LineString(coords[:i + 1]), LineString(coords[i:])
        if pd > distance:
            cp = line.interpolate(distance)
            return LineString(coords[:i] + [(cp.x, cp.y)]), LineString([(cp.x, cp.y)] + coords[i:])

    return None


def shorten_line(nodes: List[Node], distance: float, cut_beginning: bool) -> List[Node]:
    line_string = create_linestring(nodes)

    if cut_beginning:
        new_line = cut_line(line_string, distance)[1]
    else:
        new_line = cut_line(line_string, line_string.length - distance)[0]
    new_nodes = create_nodes(new_line, nodes[0].position.latlon)

    return new_nodes
