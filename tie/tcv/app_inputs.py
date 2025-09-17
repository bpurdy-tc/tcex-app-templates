"""App Inputs"""

# third-party

# third-party
from pydantic import BaseModel, Extra, Field, validator
from tcex.input.model.app_feed_api_service_model import AppFeedApiServiceModel

# pylint: disable=no-self-argument

ALL_SAMPLE_TYPES: set[str] = {'File', 'URL', 'Host', 'Event'}


class AdvancedSettingsModel(BaseModel):
    """Advanced Settings model for the App."""

    class Config:
        """Config for the App."""

        extra = Extra.forbid

    backfill: int = 8  # How far back to backfill in hours
    backfill_frequency: int = 8  # How often a new backfill job is created in hours
    frequency: int = 1  # How often a new scheduled job is created in hours


class AppBaseModel(AppFeedApiServiceModel):
    """Base model for the App containing any common inputs."""

    # vv: ${OWNERS}
    # tc_owner: str
    sample_types: set[str] | None = Field(default_factory=set)
    # ${ORGANIZATION:TEXT:Advanced Settings}
    advanced_settings: AdvancedSettingsModel = AdvancedSettingsModel()

    @validator('sample_types', pre=True)
    def validate_sample_types(cls, entries: str | None) -> set[str]:  # noqa: N805
        """Validate and parse the supported types."""
        if not entries:
            return set()

        return {entry.strip().lower() for entry in entries}

    @validator('advanced_settings', pre=True)
    def validate_advanced_settings(cls, entries: str | None) -> dict:  # noqa: N805
        """Validate and parse the advanced settings."""
        if not entries:
            return {}

        advanced_settings = {}
        ignored_keys = {
            'backfill',
            'backfill_frequency',
            'frequency',
            'backfill_frequency_large',
        }

        for entry in entries.split(','):
            key_value = entry.split('=', maxsplit=1)
            if len(key_value) == 1:
                continue  # Skip if there's no value

            key, value = key_value
            key = key.strip().lower()

            if key in ignored_keys or not key:
                continue  # Skip ignored or empty keys

            if key in advanced_settings:
                msg = f'Duplicate key "{key}" defined in Advanced Settings input.'
                raise ValueError(msg)

            advanced_settings[key] = value

        return advanced_settings


class AppInputs:
    """App Inputs"""

    def __init__(self, inputs: BaseModel):
        """Initialize class properties."""
        self.inputs = inputs

    def update_inputs(self):
        """Add custom App models to inputs.

        Input will be validate when the model is added an any exceptions will
        cause the App to exit with a status code of 1.
        """
        self.inputs.add_model(AppBaseModel)
