"""Job DAO."""

# standard library
from collections.abc import Iterable
from typing import TYPE_CHECKING, Generic, TypeVar

# third-party
import arrow
from model.job_request_model import AdHocJobRequestModel, JobRequestModel

# first-party
from core.json_db import JsonDB, SortOrder, where
from core.json_db.dao import JsonDBDAO
from core.model.settings_model_base import SettingModelBase
from core.model.tie.job_request_base_model import JobRequestBaseModel

if TYPE_CHECKING:
    from core.task.task_path_pipe_abc import TaskPathPipeABC

M = TypeVar('M', bound=JobRequestBaseModel)


class JobRequestDAO(JsonDBDAO[M], Generic[M]):
    """Job Request DAO"""

    def __init__(
        self, db: JsonDB, settings: SettingModelBase, model: type[M] = JobRequestModel
    ) -> None:
        """."""
        super().__init__(db, model)
        self.settings = settings

    def get_all_job_ids(self) -> list[str]:
        """Get all job IDs."""
        #  pylint: disable=protected-access
        return [self.db.get_index_from_path(path) for path in self.db.get_paths(self.model)]

    def get_jobs_over_limit(self, max_jobs: int) -> Iterable[M]:
        """Get jobs over the limit."""
        paths = self.db.get_paths(self.model, sort_by='index', sort_order='desc')
        paths = paths[max_jobs:]
        for path in paths:
            yield self.db.load_from_path(self.model, path)

    def get_jobs_to_clean(self, max_jobs: int) -> Iterable[M]:
        """Get jobs over the limit."""
        hits = 0
        first_found = False
        # this iterates over the jobs with the most recent job first
        for job in self.db.load_all(self.model, sort_by='index', sort_order='desc'):
            # if the job is not completed or failed do NOT clean it
            if not job.date_completed and not job.date_failed:
                continue
            # We do not want to clean the most recent scheduled job
            if job.job_type == 'scheduled' and first_found is False:
                first_found = True
                continue
            hits += 1
            # if we have hit the limit, yield the job
            if hits > max_jobs:
                yield job

    def get_completed_before(self, before: arrow.Arrow) -> Iterable[M]:
        """Get completed jobs before a date."""
        for job in self.db.load_all(M):
            done_date = job.date_completed or job.date_failed
            if done_date is not None and done_date < before:
                yield job

    def get_next_for_task(self, task: 'TaskPathPipeABC') -> M | None:
        """Get the next job for the pipeline."""
        scheduled = self.db.get_paths(self.model, sort_by='index', sort_order='asc') or []

        ad_hoc_job = None
        for job in scheduled:
            job = self.db.load_from_path(self.model, job)
            if (
                job.status.casefold() == self.settings.job.status_pending.casefold()
                or job.status.casefold() == task.task_settings.status_active.casefold()
            ):
                if task.pipeline and job.pipeline != task.pipeline:
                    continue
                if not isinstance(job, AdHocJobRequestModel):
                    return job
                if ad_hoc_job is None:
                    ad_hoc_job = job

        return ad_hoc_job

    def get_last_run_job(self, request_id, pipeline: str | None = None) -> M | None:
        """Get the last run job."""
        for j in self.db.load_all(
            self.model,
            where=where.where({'job_type': where.eq('scheduled')}),
            sort_order=SortOrder.DESC,
        ):
            if pipeline and j.pipeline != pipeline:
                continue
            if j.request_id == request_id:
                continue
            return j

        return None

    def get_most_recent_scheduled_job(self, pipeline: str | None = None) -> M | None:
        """Get the most recent scheduled job."""
        for j in self.db.load_all(
            self.model,
            where=where.where({'job_type': where.eq('scheduled')}),
            sort_order=SortOrder.DESC,
        ):
            if pipeline and j.pipeline != pipeline:
                continue
            return j

        return None
