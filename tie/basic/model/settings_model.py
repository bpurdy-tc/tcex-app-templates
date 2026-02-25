"""Define custom settings for app.

The parent SettingsModel class should never be edited.
"""

# first-party
from app_inputs import AdvancedSettingsModel
from core.json_db import Embedded
from core.model.settings_model_base import SettingModelBase


class SettingModel(SettingModelBase):
    """Custom Setting Model"""

    advanced_settings: AdvancedSettingsModel = Embedded()

    # Define custom settings for the App
    sample_types: set[str]
