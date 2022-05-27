import math
from datetime import datetime


class RoutingMonitor:
    def __init__(self, model):
        self.model = model
        self.best_objective = float("inf")
        self.start_time = datetime.now()
        self.last_reading_time = None
        self.optimization_history = dict()

    def __call__(self):
        current_objective = self.model.CostVar().Max()
        if current_objective < self.best_objective:
            self.best_objective = current_objective

        if self.last_reading_time is None or (datetime.now() - self.last_reading_time).total_seconds() > 1:
            self.last_reading_time = datetime.now()
            time_from_start = datetime.now() - self.start_time
            time_from_start = math.floor(time_from_start.total_seconds())
            self.optimization_history[str(time_from_start)] = self.best_objective
