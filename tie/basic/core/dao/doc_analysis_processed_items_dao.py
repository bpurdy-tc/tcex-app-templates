"""DAO for ReportPdfTrackerModel."""

from core.json_db import JsonDB, SortBy, SortOrder
from core.json_db.dao import JsonDBDAO
from core.model.tie import DocAnalysisProcessedItemsModel


class DocAnalysisProcessedItemsDAO(JsonDBDAO[DocAnalysisProcessedItemsModel]):
    """Data Access Object for ReportPdfTrackerModel"""

    def __init__(self, db: JsonDB) -> None:
        """Initialize class properties."""
        super().__init__(db, DocAnalysisProcessedItemsModel)

    @property
    def instance(self) -> DocAnalysisProcessedItemsModel:
        """Return the instance of the processed items tracker."""
        models = []
        for m in self.db.load_all(self.model, sort_by=SortBy.INDEX, sort_order=SortOrder.DESC):
            models.append(m)
        if len(models) > 1:
            ex_msg = 'Multiple processed items trackers items found, expected only one.'
            raise ValueError(ex_msg)
        if not models:
            model = DocAnalysisProcessedItemsModel()
            self.db.save(model)
        else:
            model = models[0]
        return model

    def save_newest_items(self, model: DocAnalysisProcessedItemsModel, n: int = 500_000):
        """Save the newest processed items, keeping only the most recent n items."""
        data = model.items
        for top_key in ['groups', 'indicators']:
            if top_key not in data:
                continue
            # Flatten all (type, key, epoch) triples
            flat = []
            for type_key, items in data[top_key].items():
                for k, v in items.items():
                    flat.append((type_key, k, v))
            # Sort by epoch (v), descending
            flat.sort(key=lambda x: x[2], reverse=True)
            # Keep only the newest n
            flat = flat[:n]
            # Rebuild the nested dict
            new_dict = {}
            for type_key, k, v in flat:
                new_dict.setdefault(type_key, {})[k] = v
            data[top_key] = new_dict
        self.db.save(model)
