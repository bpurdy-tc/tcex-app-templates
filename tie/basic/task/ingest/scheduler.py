"""Batch Submit"""

# standard library
from datetime import UTC, datetime, timedelta
from functools import cached_property

# first-party
from core.model.tie.task_setting_model import TaskSettingModel
from core.task.task_abc import TaskABC
from model import JobRequestModel


class Scheduler(TaskABC):
    """Process to submit JSON files to TC batch API."""

    def __init__(self, settings, tcex, db, *, pipeline=None):
        """Initialize Class Properties."""
        super().__init__(settings, tcex, db)
        self.pipeline = pipeline

        self.backfill = timedelta(hours=settings.advanced_settings.backfill)
        self.backfill_frequency = timedelta(hours=settings.advanced_settings.backfill_frequency)
        self.frequency = timedelta(hours=settings.advanced_settings.frequency)

    def launch_preflight_checks(self):
        """Run pre-flight check before launching task."""
        self.launch()

    def launch(self):  # pylint: disable=arguments-differ
        """Launch the task."""
        self.run()

    def run(self):
        """Schedule next download."""
        self.log.info(f'event=schedule-download, action=running-task, pipeline={self.pipeline}')
        most_recent_scheduled_job = self.job_dao.get_most_recent_scheduled_job(
            pipeline=self.pipeline
        )
        now = datetime.now(UTC)

        if not most_recent_scheduled_job:
            self.tcex.log.info('task-event=schedule-download, action=schedule-backfill-downloads')
            self._add_backfill_jobs(now)
            return

        end_time = most_recent_scheduled_job.end_time
        self.tcex.log.info(
            'task-event=schedule-download, '
            f'end_time={end_time}, '
            f'now={now}, '
            f'frequency={self.frequency}'
        )

        if (now - end_time) < self.frequency:
            self.tcex.log.info('task-event=schedule-download, action=skip-schedule')

        while (now - end_time) > self.frequency:
            self.tcex.log.info('task-event=schedule-download, action=schedule-next-download')
            self._add_job(end_time, end_time + self.frequency)
            end_time += self.frequency

    def _add_backfill_jobs(self, end_date: datetime):
        """Add backfill jobs to the database."""
        start_time = end_date - self.backfill
        while start_time < end_date:
            end_time = min(start_time + self.backfill_frequency, end_date)
            self._add_job(start_time, end_time)
            start_time = end_time

    def _add_job(self, start_time: datetime, end_time: datetime):
        """Add the job to the database."""
        self.tcex.log.info(f'action=add-job, start_time={start_time}, end_time={end_time}')
        job = JobRequestModel(
            date_queued=datetime.now(UTC),
            status=self.settings.job.status_pending,
            # Add custom job request model fields here
            start_time=start_time,
            end_time=end_time,
            sample_types=list(self.settings.sample_types),
        )
        if self.pipeline:
            job.pipeline = self.pipeline
        self.job_dao.save(job)

        self.tcex.log.info(f'action=schedule-download, job={job.dict()}')

    @cached_property
    def task_settings(self) -> TaskSettingModel:
        """Return the task settings."""
        return TaskSettingModel(
            description='Schedules the next download.',
            max_execution_minutes=10,
            name='Schedule Downloads',
            schedule_period=5,
            schedule_unit='seconds',
        )
