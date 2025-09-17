"""Task Module"""

# standard library
from abc import abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

from model import AdHocJobRequestModel
from model.settings_model import SettingModel
from sdk.sdk import SDK

# third-party
from tcex import TcEx

# first-party
from core.json_db import JsonDB

# from more import Metrics
from core.model.tie.job_request_base_model import JobRequestBaseModel
from core.service.metrics import Metrics
from core.service.writing_service import WritingModel, WritingService
from core.task.task_path_pipe_abc import TaskPathPipeABC
from core.task.tasks import Tasks

T = TypeVar('T', bound=JobRequestBaseModel)


class DownloadABC(TaskPathPipeABC):
    """Task Module"""

    def __init__(
        self,
        settings: SettingModel,
        tcex: TcEx,
        db: JsonDB,
        *,
        sdk=None,
        pipeline=None,
        request_schema: type[T] = JobRequestBaseModel,
    ):
        """Initialize class properties."""
        super().__init__(settings, tcex, db, request_schema=request_schema)

        self.log.info('action="initialize", message="Initializing Download class"')

        # properties
        self.sdk: SDK = sdk
        self.pipeline = pipeline
        self.metrics = None
        self.writing_service = WritingService(self.db, self.log)
        self.preflight_checks = [self._is_throttled_preflight_check]

    def process_group(self, item, chunk, writer: WritingModel):
        """Process item."""
        chunk.append(item)
        self.update_heartbeat(verbose=False)
        return self.writing_service.write_groups(chunk, writer)

    def process_indicator(self, item, chunk, writer: WritingModel):
        """Process item."""
        chunk.append(item)
        self.update_heartbeat(verbose=False)
        return self.writing_service.write_indicators(chunk, writer)

    def _is_throttled_preflight_check(self):
        if self._throttle_download():
            self.log.trace(
                f'task-event=launch-preflight-check-skip, action={self.task_settings.name}, '
                f'reason=throttle-limit-hit, throttle-limit={self.settings.job.throttle_limit}'
            )
            return True
        return False

    def register_preflight_check(self, check: Callable[[], bool]):
        """Register preflight check."""
        self.preflight_checks.append(check)

    def launch_preflight_checks(self):
        """Launch preflight checks."""
        try:
            if self.ns.unrecoverable_failure is True:
                return
            next_job = self.job_dao.get_next_for_task(self)
            if not next_job:
                return
            if next_job.pipeline != self.pipeline:
                return

            for check in self.preflight_checks:
                if check() is True:
                    return
        except Exception:
            self.log.exception('task-event=launch-preflight-check-error')
            return
        self.metrics = Metrics(self.db)
        self.launch(request_id=next_job.request_id)

    def run(self, request_id: str, input_dir: Path, output_dir: Path):  # noqa: ARG002
        """Run the task."""
        self.log.info(f'action="run-task", message="Running the task for request-id={request_id}"')
        request = self.job_dao.get(request_id)
        self.writing_service.request = request

        # reset the download counts
        request.count_download_group = 0
        request.count_download_indicator = 0
        self.job_dao.save(request)
        self.writing_service.request = request

        self.download(output_dir, request)
        self.metrics.process_metrics()
        self.log.info('action="task-complete", message="Task completed successfully"')

    @abstractmethod
    def download(self, output_dir: Path, request):
        """Download resources from provider."""

    def _throttle_download(self) -> bool:
        """Throttle download to prevent to much stale data on disk."""
        throttle_statutes = [
            self.settings.job.status_cancelled,
            self.settings.job.status_failed,
            self.settings.job.status_pending,
        ]
        throttle_statutes.extend(Tasks.status_final)
        # TODO fix this to account for different pipes
        running_tasks = [
            r for r in self.job_dao.get_all() if r.status.lower() not in throttle_statutes
        ]
        self.log.trace(
            f'task-event=throttle-download, count={len(running_tasks)}'
            f' final-status={Tasks.status_final}'
        )
        if len(running_tasks) >= self.settings.job.throttle_limit:
            return True
        return False

    def handle_run_error(self, request_id: str, request_dir: Path):  # noqa: ARG002
        """Handle errors during task run."""
        job = self.job_dao.get(request_id)
        if isinstance(job, AdHocJobRequestModel):
            self._task_set_status(
                request_id,
                self.settings.job.status_failed,
                ['date_failed'],
            )
            return
        # causes the app to fail.
        self.ns.unrecoverable_failure = True
        self._task_set_status(
            request_id,
            self.settings.job.status_pending,
            ['date_failed'],
        )
