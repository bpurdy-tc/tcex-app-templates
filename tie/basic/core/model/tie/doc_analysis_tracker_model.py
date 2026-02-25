"""Model Definition"""

# standard library
import datetime
from typing import ClassVar

# third-party
from pydantic import Field

# first-party
from core.json_db import Index
from core.model.model_base import ModelBase
from core.model.response.paginated_response import PaginatedResponseModel


class DocAnalysisTrackerModel(ModelBase):
    """Model Definition"""

    id: str = Index()
    group_id: str
    attempt_count: int = Field(..., description='')
    attempt_result: str = Field('pending', description='')
    date_last_attempt: datetime.datetime = Field(
        datetime.datetime.now(datetime.UTC), description=''
    )

    class Config:
        """Model Config"""

        json_encoders: ClassVar[dict] = {
            datetime.datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')
        }


class DocAnalysisTrackerResponseModel(PaginatedResponseModel[DocAnalysisTrackerModel]):
    """Model Definition"""
