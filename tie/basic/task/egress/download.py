"""Task Module"""

# standard library
from functools import cached_property
from pathlib import Path

# first-party
from core.model.tie.task_setting_pipe_model import TaskSettingPipeModel
from core.service.tcvf.writing_service import WritingModel
from core.task.download_abc import DownloadABC
from model.job_request_model import JobRequestModel


class Download(DownloadABC):
    """Task Module for downloading data."""

    def download(self, output_dir: Path, request: JobRequestModel):  # noqa: ARG002
        """Download resources from provider."""
        writer = WritingModel(page_name='indicator', output_dir=output_dir, update_metrics=True)
        indicators = self.tcex.api.tc.v3.indicators(params={'resultLimit': 10})
        max_indicators = 10
        chunk = []
        for counter, indicator in enumerate(indicators):
            if counter >= max_indicators:
                break
            indicator = indicator.model.dict(by_alias=True, exclude_none=True, exclude_unset=True)
            chunk.append(indicator)
            chunk = self.writing_service.write_indicators(chunk, writer)
        writer.force = True
        self.writing_service.write_indicators(chunk, writer)

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
            description='Downloads indicators from ThreatConnect.',
            max_execution_minutes=20,
            name=name,
        )
