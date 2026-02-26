"""Task Module"""

from functools import cached_property
from pathlib import Path

from core.model.tie.task_setting_pipe_model import TaskSettingPipeModel
from core.service.writing_service import WritingModel
from core.task.download_abc import DownloadABC
from model.job_request_model import JobRequestModel


class Download(DownloadABC):
    """Task Module for downloading data."""

    def download(self, output_dir: Path, request: JobRequestModel):
        """Download resources from provider."""
        chunk = []
        writer = WritingModel(page_name='event', output_dir=output_dir, update_metrics=True)

        for item in self.sdk.events(request.start_time, request.end_time):
            chunk.append(item)
            chunk = self.writing_service.write_groups(chunk, writer)

        writer.force = True
        self.writing_service.write_groups(chunk, writer)

    @cached_property
    def task_settings(self) -> TaskSettingPipeModel:
        """Return the task settings."""
        name = 'Download'
        if self.pipeline:
            name = f'{name} - {self.pipeline.title()}'
        return TaskSettingPipeModel(
            base_path=self.settings.base_path,
            date_field_start='date_download_start',
            date_field_complete='date_download_complete',
            description='Downloads Threat Intelligence.',
            max_execution_minutes=120,
            name=name,
            schedule_period=10,
            schedule_unit='seconds',
        )
