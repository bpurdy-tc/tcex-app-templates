"""DAO for ReportPdfTrackerModel."""

from core.json_db import JsonDB, SortBy, SortOrder
from core.json_db.dao import JsonDBDAO
from core.model.tie import ReportPdfTrackerModel


class ReportPdfTrackerDAO(JsonDBDAO[ReportPdfTrackerModel]):
    """Data Access Object for ReportPdfTrackerModel"""

    def __init__(self, db: JsonDB) -> None:
        """Initialize class properties."""
        super().__init__(db, ReportPdfTrackerModel)

    def find_next_for_group(self, group_id: str) -> ReportPdfTrackerModel | None:
        """Find next tracker for group."""
        for m in self.db.load_all(self.model, sort_by=SortBy.INDEX, sort_order=SortOrder.DESC):
            if m.group_id == group_id:
                return m
        return None
