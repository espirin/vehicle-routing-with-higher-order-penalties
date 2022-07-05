from datetime import datetime
from typing import Dict, Optional

from src.config.config import OPTIMIZATION_HISTORY_DELTA


class RoutingMonitor:
    def __init__(self, model):
        self.model = model
        self.best_objective: float = float("inf")
        self.start_time: datetime = datetime.now()
        self.last_reading_time: Optional[datetime] = None
        self.optimization_history: Dict[str, int] = dict()

    def __call__(self):
        # Update best result
        current_objective = self.model.CostVar().Max()
        if current_objective < self.best_objective:
            self.best_objective = current_objective

        # Save current best result to optimization history
        if self.last_reading_time is None or \
                (datetime.now() - self.last_reading_time).total_seconds() > OPTIMIZATION_HISTORY_DELTA:
            self.last_reading_time = datetime.now()
            time_from_start = (datetime.now() - self.start_time).total_seconds()
            self.optimization_history[str(round(time_from_start, 1))] = self.best_objective
