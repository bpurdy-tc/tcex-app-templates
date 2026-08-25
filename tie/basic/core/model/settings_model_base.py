"""Settings Module"""

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import ClassVar

from arrow import arrow
from pydantic import BaseModel, Extra, Field, validator

from core.service.notification_service import DIGEST_INTERVAL_MAP

# Default failure threshold for jobs and pipeline staleness
DEFAULT_FAILURE_THRESHOLD = timedelta(hours=48)

# Default cap on total stored batch errors before the oldest are pruned
DEFAULT_MAX_BATCH_ERRORS = 20_000


class FileSettings(BaseModel):
    """Settings for file handling."""

    extension_csv: str = '.csv'
    extension_gzip: str = '.gz'
    extension_bzip: str = '.bz'
    extension_json: str = '.json'
    extension_pending: str = '.temp'
    extension_processed: str = '.processed'
    extension_unknown: str = '.unknown'
    extension_zip: str = '.zip'
    separator: str = '#'  # separator used when building file names


# TODO: Would like to move status to its own thing too. Maybe a Enum?
class JobSettings(BaseModel):
    """Settings for job management."""

    status_cancelled: str = 'cancelled'
    status_failed: str = 'failed'
    status_pending: str = 'pending'
    status_retry_pending: str = 'retry pending'
    throttle_limit: int = 3


class AppSettingsBase(BaseModel):
    """The admin-editable settings, and the only thing written to the JSON DB.

    Being a separate model IS the boundary: credentials and runtime state live on
    `SettingModelBase` and so cannot be persisted or reached by a settings payload. An
    app subclasses this to add its own settings and to build the record from the app
    inputs on first boot — see `AppSettings.load`.
    """

    #: Singleton record id. Also satisfies `JsonDB.get_index_field()`, which needs either
    #: an `Index()`-marked field or a field literally named `id`.
    id: str = 'app_settings'

    notification_digest_interval: timedelta | None = None
    notification_types: list[str] | None = None

    # Scheduling and retry. FLAT, and named exactly as the settings form posts them, so an
    # update is `type(record)(**{**record.dict(), **payload})` and nothing has to map one
    # shape onto another. `rate_limit_constraints` is deliberately absent — it is not
    # admin-editable, so it stays on the app inputs rather than in this record.
    frequency: int = 1
    failure_threshold: timedelta = DEFAULT_FAILURE_THRESHOLD
    max_retries: int = 10

    # Not on the settings form (api/ui_config_builder.py::advanced_settings_inputs is an
    # explicit whitelist that omits this) — internal tuning, changeable via PUT /api/settings
    # without a redeploy for support/engineering, not meant for the admin-facing UI.
    max_batch_errors: int = DEFAULT_MAX_BATCH_ERRORS

    @validator('failure_threshold', pre=True)
    def parse_failure_threshold(cls, value: str | float | timedelta) -> timedelta:
        """Accept whole hours from the form, seconds from the JSON DB, or a timedelta."""
        if isinstance(value, timedelta):
            return value
        if isinstance(value, float):
            return timedelta(seconds=value)
        return timedelta(hours=int(value))

    @validator('notification_digest_interval', pre=True)
    def parse_digest_interval(cls, value):
        """Accept the label the form offers, seconds from the JSON DB, or a timedelta.

        The select is built from `DIGEST_INTERVAL_MAP` and posts back the label it
        displayed, so this is the inverse of how `notification_inputs` renders the
        default. Empty means notifications are disabled — see `core/task/tasks.py`.

        An unrecognised non-empty value raises rather than resolving to `None`: silently
        turning notifications off because a label did not match is exactly the kind of
        failure nobody notices until an incident goes unreported.
        """
        if value is None or value == '':
            return None
        if isinstance(value, timedelta):
            return value
        if isinstance(value, int | float):
            return timedelta(seconds=value)

        interval = DIGEST_INTERVAL_MAP.get(str(value))
        if interval is None:
            msg = f'Unknown notification digest interval: {value!r}'
            raise ValueError(msg)
        return interval


class SettingModelBase(BaseModel):
    """Base model for settings."""

    base_path: Path
    name: str
    description: str
    tc_owner: str
    date_started: datetime = Field(default_factory=lambda: datetime.now(UTC))

    #: The persisted settings. Loaded from the JSON DB at startup and mutated in place by
    #: the settings API, so every holder of this object sees an edit without a restart.
    app_settings: AppSettingsBase = AppSettingsBase()
    notification_display_name: str | None = None

    file: FileSettings = FileSettings()
    job: JobSettings = JobSettings()

    class Config:
        """Pydantic Config"""

        arbitrary_types_allowed = True
        json_encoders: ClassVar[dict] = {arrow.Arrow: lambda v: v.isoformat()}
        extra = Extra.allow
