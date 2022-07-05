from abc import ABC, abstractmethod
from typing import Dict

from utm import to_latlon, from_latlon, latitude_to_zone_letter, latlon_to_zone_number

from src.abstract.serialisable import Serialisable


class Coordinates(Serialisable, ABC):
    """
    Coordinates is an abstract class for different types of coordinates.
    """

    @abstractmethod
    def check_validity(self):
        pass


class LatLon(Coordinates):
    """
    LatLon coordinates.
    """

    def __init__(self, lat: float = None, lon: float = None, utm=None, zone_latlon=None):
        self.lat = None
        self.lon = None

        if lat is not None and lon is not None and (utm is not None or zone_latlon is not None):
            raise Exception("Please provide either lat, lon or utm and zone_latlon")
        elif lat is not None and lon is not None:
            self.lat = lat
            self.lon = lon
        elif utm is not None and zone_latlon is not None:
            self.update(utm, zone_latlon)
        else:
            raise Exception("Bad constructor arguments")

        self.check_validity()

    def check_validity(self):
        if self.lat < -90 or self.lat > 90 or self.lon < -180 or self.lon > 180:
            raise Exception("LatLon not valid")

    def __str__(self):
        return f"lat: {self.lat}, lon: {self.lon}"

    def __repr__(self):
        return self.__str__()

    def to_json(self) -> dict:
        return {
            "lat": self.lat,
            "lon": self.lon
        }

    def update(self, utm, zone_latlon=None):
        if self.lat is not None and self.lon is not None:
            self.lat, self.lon = to_latlon(utm.east, utm.north, latlon_to_zone_number(self.lat, self.lon),
                                           latitude_to_zone_letter(self.lat))
        elif zone_latlon is not None:
            self.lat, self.lon = to_latlon(utm.east, utm.north, latlon_to_zone_number(zone_latlon.lat, zone_latlon.lon),
                                           latitude_to_zone_letter(zone_latlon.lat))
        else:
            raise Exception("lat and lon are not set, please provide zone_latlon")


class UTM(Coordinates):
    """
    UTM coordinates.

    See: https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system
    """

    def __init__(self, north: float = None, east: float = None, zone_latlon: LatLon = None):
        self.north = None
        self.east = None

        if north is not None and east is not None and zone_latlon is not None:
            raise Exception("Please provide north-east or latlon, not both")
        elif north is not None and east is not None:
            self.north = north
            self.east = east
        elif zone_latlon is not None:
            self.update(zone_latlon)
        else:
            raise Exception("Please provide north-east or latlon")
        self.check_validity()

    def check_validity(self):
        # Not implemented
        pass

    def to_json(self) -> dict:
        return {
            "north": self.north,
            "east": self.east
        }

    @staticmethod
    def from_json(json_message):
        return UTM(north=float(json_message['north']), east=float(json_message['east']))

    def update(self, latlon: LatLon):
        northeast = from_latlon(latlon.lat, latlon.lon)
        self.east = northeast[0]
        self.north = northeast[1]

    def __str__(self):
        return f"UTM: north {self.north}, east {self.east}"


class Position(Serialisable):
    """
    Position is a container for coordinates.

    Position has two coordinates representations:
    - lat, lon
    - UTM
    """

    def __init__(self, latlon: LatLon = None, utm: UTM = None, zone_latlon: LatLon = None):
        self.latlon = None
        self.utm = None

        if latlon is not None and utm is not None:
            raise Exception("Please provide only type of coordinates")
        elif latlon is None and utm is None:
            raise Exception("Please provide one type of coordinates")
        elif latlon is not None:
            self.latlon = latlon
            self.update_utm()
        elif utm is not None and zone_latlon is not None:
            self.utm = utm
            self.update_latlon(zone_latlon=zone_latlon)
        else:
            raise Exception("Bad constructor arguments")

    def __str__(self):
        return f"Position ({self.latlon}, {self.utm})"

    def __repr__(self):
        return self.__str__()

    def to_json(self) -> dict:
        if self.latlon is None:
            raise Exception("LatLon is not set")
        return {
            "latlon": self.latlon.to_json()
        }

    def update_utm(self):
        if self.latlon is None:
            raise Exception("LatLon is not set")
        if self.utm is None:
            self.utm = UTM(zone_latlon=self.latlon)
        else:
            self.utm.update(self.latlon)

    def update_latlon(self, zone_latlon=None):
        if self.utm is None:
            raise Exception("UTM is not set")
        if self.latlon is None:
            if zone_latlon is None:
                raise Exception("Please provide zone_latlon")
            self.latlon = LatLon(utm=self.utm, zone_latlon=zone_latlon)
        else:
            self.latlon.update(self.utm)

    def get_utm_with_forced_zone(self, zone_number: int) -> UTM:
        east, north, *rest = from_latlon(self.latlon.lat, self.latlon.lon, force_zone_number=zone_number)
        return UTM(north=north, east=east)


class Node(Serialisable):
    """
    Node is a point on map. E.g. a part of a segment.

    Each node has a position.
    """

    def __init__(self, position: Position, attributes: Dict = None):
        if attributes is None:
            attributes = dict()
        self.position = position
        self.attributes = attributes

    def __str__(self):
        return f"Node ({self.position.latlon.lat}, {self.position.latlon.lon})"

    def __repr__(self):
        return self.__str__()

    def to_json(self) -> dict:
        return {
            "position": self.position.to_json(),
            "attributes": self.attributes
        }

    def __eq__(self, other):
        return isinstance(other, Node) and self.position.latlon.lat == other.position.latlon.lat \
               and self.position.latlon.lon == other.position.latlon.lon

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.position.latlon.lat, self.position.latlon.lon))
