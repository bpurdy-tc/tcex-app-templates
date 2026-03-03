"""Settings Module"""

from pydantic import BaseModel


class AdvancedSettingsModelBase(BaseModel):
    """Advanced Settings model for the App."""

    backfill: int = 48  # How far back to backfill in hours
    backfill_frequency: int = 8  # How often a new backfill job is created in hours
    frequency: int = 1  # How often a new scheduled job is created in hours
