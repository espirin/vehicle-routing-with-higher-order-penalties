from typing import Optional, Dict

from src.config import STRAIGHT_NON_STRAIGHT_MANEUVER_PENALTY, NON_STRAIGHT_STRAIGHT_MANEUVER_PENALTY
from src.routing_problem.lanelet import Lanelet
from src.routing_problem.maneuver.maneuver import Maneuver
from src.routing_problem.maneuver.modifier import ManeuverModifier


class CompleteConnection:
    def __init__(self, lanelet_from: Lanelet, lanelet_to: Lanelet, maneuver: Optional[Maneuver]):
        self.lanelet_from: Lanelet = lanelet_from
        self.lanelet_to: Lanelet = lanelet_to

        self.maneuver: Optional[Maneuver] = maneuver

    def get_cost_to(self, connection, matrix: Dict[str, Dict[str, int]]):
        if isinstance(connection, LastConnection) or isinstance(connection, FirstConnection):
            return 0

        if self.lanelet_to.segment.id == connection.lanelet_from.segment.id:
            cost = 0
        else:
            cost = matrix[self.lanelet_to.segment.id][connection.lanelet_from.segment.id]

        # if cost > CONNECTIONS_COST_CUTOFF:
        #     return OPTIMISER_INFINITY

        if self.maneuver is not None and connection.maneuver is not None:
            if self.maneuver.modifier == ManeuverModifier.Straight:
                if connection.maneuver.modifier == ManeuverModifier.Straight:
                    pass
                else:
                    cost += STRAIGHT_NON_STRAIGHT_MANEUVER_PENALTY
            else:
                if connection.maneuver.modifier == ManeuverModifier.Straight:
                    cost += NON_STRAIGHT_STRAIGHT_MANEUVER_PENALTY
                else:
                    pass

        return cost


class LastConnection(CompleteConnection):
    def __init__(self):
        super().__init__(None, None, None)

    def get_cost_to(self, connection, matrix: Dict[str, Dict[str, int]]):
        return 0


class FirstConnection(CompleteConnection):
    def __init__(self):
        super().__init__(None, None, None)

    def get_cost_to(self, connection, matrix: Dict[str, Dict[str, int]]):
        return 0
