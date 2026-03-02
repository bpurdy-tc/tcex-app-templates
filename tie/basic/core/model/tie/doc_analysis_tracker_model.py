"""Model Definition"""

import datetime

from core.json_db import Index
from core.model.model_base import ModelBase
from core.model.response.paginated_response import PaginatedResponseModel
from pydantic import Field, field_serializer


class DocAnalysisTrackerModel(ModelBase):
    """Model Definition"""

    id: str = Index()
    group_id: str
    attempt_count: int = Field(..., description='')
    attempt_result: str = Field('pending', description='')
    date_last_attempt: datetime.datetime = Field(
        datetime.datetime.now(datetime.UTC), description=''
    )

    @field_serializer('date_last_attempt')
    def serialize_datetime(self, v: datetime.datetime, _info) -> str:
        """Serialize datetime to string."""
        return v.strftime('%Y-%m-%d %H:%M:%S')


class DocAnalysisTrackerResponseModel(PaginatedResponseModel[DocAnalysisTrackerModel]):
    """Model Definition"""
