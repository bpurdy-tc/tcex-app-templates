"""Model Definition"""

# standard library
from datetime import UTC, datetime
from typing import ClassVar

# third-party
from pydantic import Field

# first-party
from core.json_db import Index
from core.model.model_base import ModelBase


class VersionManagerModel(ModelBase):
    """Model Definition"""

    id: str = Index()
    version: str = Field(..., description='')
    installation_date: datetime = Field(default_factory=lambda: datetime.now(UTC), description='')

    class Config:
        """Model Config"""

        json_encoders: ClassVar[dict] = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S'),
        }
