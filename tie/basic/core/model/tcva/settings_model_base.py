"""Settings Module"""

from pathlib import Path

from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(arbitrary_types_allowed=True, extra='allow')
