from src.routing_problem.maneuver.maneuver_type import ManeuverType
from src.routing_problem.maneuver.modifier import ManeuverModifier


class Maneuver:
    def __init__(self, from_id: str, to_id: str, in_angle: int, turn_angle: int, duration: int, weight: 0,
                 maneuver_type: ManeuverType, modifier: ManeuverModifier):
        self.from_id: str = from_id
        self.to_id: str = to_id
        self.in_angle: int = in_angle
        self.turn_angle: int = turn_angle
        self.duration: int = duration
        self.weight: int = weight
        self.type: ManeuverType = maneuver_type
        self.modifier: ManeuverModifier = modifier
