"""Settings Module"""

# standard library
from pathlib import Path
from typing import ClassVar

# third-party
from arrow import arrow
from pydantic import BaseModel, Extra


class SettingModelBase(BaseModel):
    """Setting Model"""

    use_message_broker: bool = True
    base_path: Path
    name: str
    description: str
    schema_version: str
    active: bool = True
    provider_id: str
    topic: str
    features: dict = {}

    def add_message_handler(self, type_: str, handler):
        """."""
        self.features[type_.lower()] = handler

    def get_message_handler(self, type_: str):
        """."""
        return self.features.get(type_.lower())

    class Config:
        """Pydantic Config"""

        arbitrary_types_allowed = True
        json_encoders: ClassVar[dict] = {arrow.Arrow: lambda v: v.isoformat()}
        extra = Extra.allow
