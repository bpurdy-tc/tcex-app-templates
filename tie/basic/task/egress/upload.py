"""Batch Submit"""

# standard library
import gzip
import json
from functools import cached_property

# first-party
from core.model.tie.task_setting_pipe_model import TaskSettingPipeModel
from core.task.upload_egress_abc import UploadEgressABC
from sdk.egress_sdk import EgressSDK


class Upload(UploadEgressABC):
    """Process to submit JSON files to TC batch API."""

    def process_file(self, file, request):  # noqa: ARG002
        """Process file."""
        self.sdk: EgressSDK

        with gzip.open(file) as f:
            indicators = json.load(f)

        for indicator in indicators:
            self.sdk.upload(json=indicator)

    @cached_property
    def task_settings(self) -> 'TaskSettingPipeModel':
        """Return the task settings."""
        name = 'Upload'
        if self.pipeline:
            name = f'{name} - {self.pipeline.title()}'

        return TaskSettingPipeModel(
            base_path=self.settings.base_path,
            date_field_start='date_upload_start',
            date_field_complete='date_upload_complete',
            description='Uploads TC Indicators to a mock API endpoint.',
            max_execution_minutes=30,
            name=name,
        )
