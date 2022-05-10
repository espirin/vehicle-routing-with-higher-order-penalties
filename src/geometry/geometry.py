from typing import List

from shapely.geometry import LineString, Point
from utm import latlon_to_zone_number

from src.geo.geo import Node, Position, UTM, LatLon


class BadGeometryException(Exception):
    pass


def offset_nodes(nodes: List[Node], distance=3, side='left', resolution=16, join_style=1) -> List[Node]:
    utm_zone_number = latlon_to_zone_number(nodes[0].position.latlon.lat, nodes[0].position.latlon.lon)

    utm_nodes = []
    for node in nodes:
        utm = node.position.get_utm_with_forced_zone(utm_zone_number)
        utm_nodes.append([utm.north, utm.east])
    line_string = LineString(utm_nodes)

    offsetted_utm_string = line_string.parallel_offset(distance=distance, side=side, resolution=resolution,
                                                       join_style=join_style)
    try:
        offsetted_coordinates = list(offsetted_utm_string.coords)
    except NotImplementedError:
        raise BadGeometryException()
    offsetted_nodes = []
    for north, east in offsetted_coordinates:
        node = Node(Position(utm=UTM(north=north, east=east), zone_latlon=nodes[0].position.latlon))
        offsetted_nodes.append(node)

    # Right hand offsets are returned in the reverse direction of the original LineString or LineRing,
    # while left side offsets flow in the same direction.
    if side == 'right':
        offsetted_nodes.reverse()

    return offsetted_nodes


def get_part(from_percent: float, to_percent: float, line: LineString, zone_latlon: LatLon) -> List[Node]:
    # Cut figure into two at a given percent of its length
    distance_from = line.length * from_percent
    before_from, after_from = cut_line(line, distance_from)

    distance_to = line.length * to_percent - before_from.length if before_from else line.length * to_percent
    before_to, after_to = cut_line(after_from, distance_to)

    part = [Node(Position(utm=UTM(north=node[0], east=node[1]), zone_latlon=zone_latlon))
            for node in before_to.coords] if before_to else []
    return part


def cut_line(line: LineString, distance: float):
    # Cut a line in two at a given distance from its starting point
    if distance <= 0.0:
        return None, line
    elif distance >= line.length:
        return line, None

    coords = list(line.coords)
    for i, p in enumerate(coords):
        pd = line.project(Point(p))
        if pd == distance:
            return LineString(coords[:i + 1]), LineString(coords[i:])
        if pd > distance:
            cp = line.interpolate(distance)
            return LineString(coords[:i] + [(cp.x, cp.y)]), LineString([(cp.x, cp.y)] + coords[i:])
