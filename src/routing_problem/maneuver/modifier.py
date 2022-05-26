from enum import Enum


class ManeuverModifier(Enum):
    UTurn = 0
    SharpRight = 1
    Right = 2
    SlightRight = 3
    Straight = 4
    SlightLeft = 5
    Left = 6
    SharpLeft = 7
    MaxDirectionModifier = 8
