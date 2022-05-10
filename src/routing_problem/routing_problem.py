from typing import List

from geojson import FeatureCollection

from src.json.serialisable import Serialisable
from src.routing_problem.lanelet import Lanelet


class RoutingProblem(Serialisable):
    def __init__(self, lanelets: List[Lanelet]):
        self.lanelets: List[Lanelet] = lanelets

    def to_json(self):
        return FeatureCollection(features=[lanelet.to_json() for lanelet in self.lanelets])
