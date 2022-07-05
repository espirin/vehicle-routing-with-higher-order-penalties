from enum import Enum


class ManeuverModifier(Enum):
    """
    ManeuverModifier is OSRM's internal Enum representing maneuver modifier.

    It is created with the help of Atlatec's proprietary OSRM fork.

    See: http://project-osrm.org/docs/v5.24.0/api/#stepmaneuver-object
    """

    UTurn = 0
    SharpRight = 1
    Right = 2
    SlightRight = 3
    Straight = 4
    SlightLeft = 5
    Left = 6
    SharpLeft = 7
    MaxDirectionModifier = 8
