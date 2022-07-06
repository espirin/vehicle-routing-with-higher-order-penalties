from typing import Optional, Dict

from src.routing_problem.lanelet import Lanelet
from src.routing_problem.maneuver.maneuver import Maneuver
from src.routing_problem.maneuver.modifier import ManeuverModifier


class XGraphNode:
    def __init__(self, lanelet_from: Lanelet, lanelet_to: Lanelet, maneuver: Optional[Maneuver]):
        self.lanelet_from: Lanelet = lanelet_from
        self.lanelet_to: Lanelet = lanelet_to

        self.maneuver: Optional[Maneuver] = maneuver

    def get_cost_to(self,
                    connection,
                    matrix: Dict[str, Dict[str, int]],
                    straight_non_straight_maneuver_penalty: int,
                    non_straight_straight_maneuver_penalty: int):
        if isinstance(connection, LastXGraphNode):
            return 0

        if self.lanelet_to.segment.id == connection.lanelet_from.segment.id and self.maneuver is not None:
            if self.maneuver.modifier == ManeuverModifier.Straight:
                if connection.maneuver.modifier == ManeuverModifier.Straight:
                    return 0
                else:
                    return straight_non_straight_maneuver_penalty
            else:
                if connection.maneuver.modifier == ManeuverModifier.Straight:
                    return non_straight_straight_maneuver_penalty
                else:
                    return 0
        else:
            return matrix[self.lanelet_to.segment.id][connection.lanelet_from.segment.id]


class SelfXGraphNode(XGraphNode):
    def __init__(self, lanelet: Lanelet):
        super().__init__(lanelet, lanelet, maneuver=None)


class LastXGraphNode(XGraphNode):
    def __init__(self):
        super().__init__(None, None, None)

    def get_cost_to(self,
                    connection,
                    matrix: Dict[str, Dict[str, int]],
                    straight_non_straight_maneuver_penalty: int,
                    non_straight_straight_maneuver_penalty: int):
        return 0


class FirstXGraphNode(XGraphNode):
    def __init__(self):
        super().__init__(None, None, None)

    def get_cost_to(self,
                    connection,
                    matrix: Dict[str, Dict[str, int]],
                    straight_non_straight_maneuver_penalty: int,
                    non_straight_straight_maneuver_penalty: int):
        return 0
