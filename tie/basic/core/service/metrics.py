"""Metrics Module"""

# third-party

# first-party
from core.json_db import JsonDB
from core.json_db.dao import JsonDBDAO
from core.model.tie import TiProcessingMetricModel


class Metrics:
    """Metrics Module"""

    def __init__(self, db: JsonDB):
        """Initialize class properties."""
        # properties
        self.db = db
        self.staged_metrics = {}
        self.dao = JsonDBDAO(db, TiProcessingMetricModel)

    #  pylint: disable=no-member
    def get_metrics(self, metric_name: str) -> TiProcessingMetricModel | None:
        """Return metrics."""
        try:
            return self.dao.get(metric_name)
        except FileNotFoundError:
            return TiProcessingMetricModel(ti_type=metric_name, ti_count=0)

    def stage_metrics(self, metric_name: str, metric_value: int):
        """Stage metrics."""
        self.staged_metrics.setdefault(metric_name, 0)
        self.staged_metrics[metric_name] += metric_value

    def process_metrics(self):
        """Process metrics."""
        for metric_name, metric_value in self.staged_metrics.items():
            self._process_metric(metric_name, metric_value)
        self.staged_metrics = {}

    def _process_metric(self, metric_name: str, metric_value: int):
        """Add or update metrics."""
        metric = self.get_metrics(metric_name)
        metric.ti_count += metric_value
        self.dao.save(metric)
