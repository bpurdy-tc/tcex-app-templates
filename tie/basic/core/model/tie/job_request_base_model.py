"""Model Definition"""

# standard library
from datetime import datetime
from typing import ClassVar

# third-party
import arrow
from pydantic import Extra, Field, validator

# first-party
from core.json_db import Index
from core.model.model_base import ModelBase


class JobRequestBaseModel(ModelBase):
    """Model Definition"""

    job_type: str = 'scheduled'
    date_completed: datetime | None = Field(None, description='')
    date_failed: datetime | None = Field(None, description='')
    date_queued: datetime = Field(..., description='')
    date_started: datetime | None = Field(None, description='')
    date_upload_failure: datetime | None = Field(None, description='')
    request_id: str = Index()
    status: str = Field(..., description='')
    status_icon: str | None = Field(None, description='The status icon to show in UI.')
    old_request_id: str | None = Field(None, description='Original request ID from a migrated job.')
    upload_failed_files: list[str] = Field(
        [], description='List of files that failed during batch upload.'
    )
    pipeline: str | None = Field(None, description='The name of the pipeline.')

    # metrics
    count_batch_error: int = Field(0, description='')
    count_upload_retries: int = Field(0, description='Number of retries for batch upload process.')
    count_batch_group_success: int = Field(0, description='')
    count_batch_indicator_success: int = Field(0, description='')
    count_download_group: int = Field(0, description='')
    count_download_indicator: int = Field(0, description='')
    date_convert_start: datetime | None = Field(None, description='')
    date_convert_complete: datetime | None = Field(None, description='')
    date_download_start: datetime | None = Field(None, description='')
    date_download_complete: datetime | None = Field(None, description='')
    date_upload_start: datetime | None = Field(None, description='')
    date_upload_complete: datetime | None = Field(None, description='')

    @property
    def convert_runtime(self):
        """Calculate convert runtime."""
        if self.date_convert_start and self.date_convert_complete:
            return self.date_convert_complete - self.date_convert_start
        return None

    @property
    def download_runtime(self):
        """Calculate download runtime."""
        if self.date_download_start and self.date_download_complete:
            return self.date_download_complete - self.date_download_start
        return None

    @property
    def upload_runtime(self):
        """Calculate upload runtime."""
        if self.date_upload_start and self.date_upload_complete:
            return self.date_upload_complete - self.date_upload_start
        return None

    @property
    def total_runtime(self):
        """Calculate total runtime."""
        if self.date_download_start and self.date_upload_complete:
            return self.date_upload_complete - self.date_download_start
        return None

    @validator('status')
    def _title_case(cls, v):  # noqa: N805
        return ' '.join([w.title() for w in v.split(' ')])

    @validator('status_icon', pre=True)
    def _status_icon(cls, _, values):  # noqa: N805
        status_icon_map = {
            'download in progress': 'file_download',
            'download complete': 'file_download',
            'convert in progress': 'change_circle',
            'convert complete': 'change_circle',
            'failed': 'error_outline',
            'pending': 'help_outline',
            'upload in progress': 'file_upload',
            'upload complete': 'check',
        }
        return status_icon_map.get(values.get('status').lower()) or 'help_outline'

    class Config:
        """Model Config"""

        arbitrary_types_allowed = True
        extra = Extra.allow
        json_encoders: ClassVar[dict] = {arrow.Arrow: lambda v: v.isoformat()}
        orm_mode = True
