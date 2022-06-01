from typing import Optional, Dict

from src.config import STRAIGHT_NON_STRAIGHT_MANEUVER_PENALTY, NON_STRAIGHT_STRAIGHT_MANEUVER_PENALTY, \
    CONNECTIONS_COST_CUTOFF, OPTIMISER_INFINITY
from src.routing_problem.maneuver.maneuver import Maneuver
from src.routing_problem.maneuver.modifier import ManeuverModifier
from src.routing_problem.segment import Segment


class CompleteConnection:
    def __init__(self, segment_from: Segment, segment_to: Segment, maneuver: Optional[Maneuver]):
        self.segment_from: Segment = segment_from
        self.segment_to: Segment = segment_to

        self.maneuver: Optional[Maneuver] = maneuver

    def get_cost_to(self, connection, matrix: Dict[str, Dict[str, int]]):
        if self.segment_to.id == connection.segment_from.id:
            cost = 0
        else:
            cost = matrix[self.segment_to.id][connection.segment_from.id]

        if cost > CONNECTIONS_COST_CUTOFF:
            return OPTIMISER_INFINITY

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
