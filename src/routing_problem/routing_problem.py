from typing import List

from src.entities import Lanelet


class RoutingProblem:
    def __init__(self, lanelets: List[Lanelet]):
        self.lanelets: List[Lanelet] = lanelets
