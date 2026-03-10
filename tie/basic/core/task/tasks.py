"""Tasks Container"""

import logging
import os
import signal
import time
import traceback
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, ClassVar

import arrow
import schedule
from core.beacon import inject
from core.dao.job_dao import JobRequestDAO
from core.json_db import JsonDB
from core.model.settings_model_base import SettingModelBase
from core.model.tie.notification_model import NotificationModel
from core.service.notification_service import NotificationService
from core.supervisor import Supervisor
from model.job_request_model import JobRequestModel
from tcex import TcEx
from tcex.exit import ExitCode

if TYPE_CHECKING:
    from task import TaskABC

logger = logging.getLogger('tcex')


class Tasks:
    """Tasks Container"""

    status_final: ClassVar[list[str]] = []

    def __init__(
        self,
        tcex: TcEx,
        db: JsonDB = inject(JsonDB),  # noqa: B008
        settings: SettingModelBase = inject(SettingModelBase),  # noqa: B008
    ):
        """Initialize class properties.

        Args:
            tcex: TcEx instance.
            db: JsonDB instance for persisting Supervisor state.
            settings: Application settings.
        """
        # properties
        self._tasks = set()
        self.log = logger
        self.tcex = tcex
        self.exit_service = tcex.exit
        self.settings = settings
        self.db = db

        # Create JobRequestDAO for Supervisor
        self.job_dao = JobRequestDAO(db, settings)

        # Initialize Supervisor with JsonDB, job_dao, settings, and exit service
        self.supervisor = Supervisor(
            db=db,
            job_dao=self.job_dao,
            settings=settings,
            exit_service=self.exit_service,
        )

        # Notification state tracking (disabled when notification_digest_interval is None)
        self.notifications_enabled = settings.notification_digest_interval is not None
        self.notification_service = (
            NotificationService(tcex) if self.notifications_enabled else None
        )
        self.last_digest_time = datetime.now(UTC)
        self.reported_retrying: set[str] = set()  # job IDs already reported as retrying
        self.reported_resolved: set[str] = set()  # job IDs already reported as perm_fail/recovered

        # Check for stale pipelines and enter probation mode if needed
        # Stale pipelines: first job must succeed or app shuts down
        # Healthy pipelines: baseline is reset normally
        self.supervisor.check_and_enter_probation()

        # schedule watchdog for tasks
        schedule.every(1).minute.do(self.watchdog)

    def add_task(self, task: 'TaskABC'):
        """Add a task to the container."""
        self._tasks.add(task)
        task.schedule()

    def add_task_path_pipe(self, tasks: 'list[TaskABC]'):
        """Add a task to the container."""
        for index, task in enumerate(tasks):  # reverse list
            # set the task index
            task.task_settings.index = index

            # first task in pipe
            if index == 0:
                task.task_settings.pipe_task_start = True
            else:
                # set previous task name for pipe, unless first task in pipe
                task.task_settings.previous_task_name = tasks[index - 1].task_settings.name

            # last task in pipe
            if index == len(tasks) - 1:
                task.task_settings.pipe_task_complete = True

                # for last task in pipe, set the pipe task complete to True
                task.task_settings.working_dir_out = (
                    task.task_settings.base_path / 'done_working_dir'
                )
                task.task_settings.working_dir_out.mkdir(parents=True, exist_ok=True)

                # add final status
                Tasks.status_final.append(task.task_settings.status_complete)
            else:
                # out directory for the current task is the "in" directory for
                # the next task, except when on the last task in the pipe
                task.task_settings.working_dir_out = tasks[index + 1].task_settings.working_dir_in

            self.log.debug(
                f'pipe-event=add-task-pipe, task-name={task.task_settings.name}, '
                f'pipe-task-start={task.task_settings.pipe_task_start}, '
                f'pipe-task-complete={task.task_settings.pipe_task_complete}, '
                f'previous-task-name={task.task_settings.previous_task_name}, '
                f'working-dir-out={task.task_settings.working_dir_out}'
            )
            self.add_task(task)

    def all(self) -> 'list[TaskABC]':
        """Return all processes that are alive."""
        return list(self._tasks)

    def alive(self) -> 'list[TaskABC]':
        """Return all processes that are alive."""
        return [t for t in self._tasks if t.process is not None and t.process.is_alive()]

    def kill(self, task: 'TaskABC'):
        """Kill multi-processes to cleanly exit app."""
        self.log.warning(f'event=kill-task, task-name={task.task_settings.name}')
        if task.process is not None:
            if task.process.is_alive():
                try:
                    self._send_signal_to_task(signal.SIGALRM, task)
                    time.sleep(2)
                    self._send_signal_to_task(signal.SIGKILL, task)
                except Exception:
                    self.log.warning(f'event=kill-task-failed, pid={task.process.pid}')
                    self.log.warning(traceback.format_exc())

            task.process.join(10)

    def kill_all(self):
        """Kill all multi-process."""
        max_wait = 30
        deadline = time.time() + max_wait

        # wait for up to "max_wait"
        self.log.trace(f'action=kill_all-wait-for-task-completion, max-seconds={max_wait}')
        while True:
            # allow processes to wrap up current work before exiting App
            if time.time() > deadline or len(self.alive()) == 0:
                break
            time.sleep(1)
        for task in self.all():
            self.kill(task)

    def watchdog(self) -> None:  # noqa: C901
        """Monitor tasks and perform health checks.

        Per-job backoff is handled directly on JobRequestModel fields.
        Pipeline staleness is checked by Supervisor.tick() using job completion times.
        """
        self.log.debug(f'task-event=run-watchdog, task-count={len(self._tasks)}')
        api_limit: None | dict = None

        # Run Supervisor tick for pipeline health monitoring
        # This checks if any pipeline has no completed jobs for threshold (default 48h)
        self.supervisor.tick()

        # Check for shutdown request from Supervisor (staleness detected in main process)
        if self.supervisor.shutdown_requested:
            self.log.warning(
                f'task-event=supervisor-shutdown-requested, '
                f'reason={self.supervisor.shutdown_reason}'
            )
            self._graceful_shutdown(self.supervisor.shutdown_reason)
            return

        # Check for unrecoverable failure from forked tasks (cross-process via Redis)
        for task in self.all():
            if task.ns.unrecoverable_failure is True:
                self.log.warning(
                    f'task-event=unrecoverable-failure, task-name={task.task_settings.name}'
                )
                self._graceful_shutdown('Task reported unrecoverable failure')
                return

        for task in self.all():
            # see if we should kill the task as its over its time limit
            if task.process is not None and task.process.is_alive():
                # update date expires based on heartbeat
                self.log.trace(
                    f'task-event=watchdog, '
                    f'heartbeat-value={task.ns.heartbeat}, task={task.task_settings.name}'
                )

                if arrow.now(UTC) - task.ns.heartbeat > timedelta(
                    minutes=task.task_settings.max_execution_minutes
                ):
                    self.log.warning(
                        f'task-event=kill-task, task-name={task.task_settings.name}, '
                        f'process-id={task.process.pid}, metadata={task.process.metadata.dict()}, '
                    )
                    self.kill(task)

                # Handle setting our api limit hit metric since its forked
                # We only care about the value for the DownloadPathPipe task
                if type(task).__name__ in ['Download']:
                    self.log.debug(f'Task: {type(task).__name__} has: {task.ns.api_limit_details}')
                    # Set to latest value
                    if api_limit is None or task.ns.api_limit_details.get(
                        'date_set'
                    ) > api_limit.get('date_set'):
                        api_limit = task.ns.api_limit_details

            if api_limit is not None:
                # self.tcex.app.service.add_metric(
                #     'Vulnerability API Limit Hit', api_limit.get('reached')
                # )
                self.log.debug(f'API Limit Hit: {api_limit.get("reached")}')

        # Check if digest interval has elapsed and send digest if needed
        if self.notifications_enabled:
            now = datetime.now(UTC)
            digest_interval = self.settings.notification_digest_interval
            if now - self.last_digest_time >= digest_interval:
                self._send_digest(now)

    def pause_all(self):
        """Pause all tasks.

        Sets pause flag in Tasks' settings so that it will not persist across restart.
        """
        for task in self.all():
            task.task_settings.paused = True

    def _graceful_shutdown(self, reason: str) -> None:
        """Perform graceful shutdown: pause tasks, kill running, then exit.

        Tier 1 notification: always sent, never filtered.

        Args:
            reason: Human-readable reason for shutdown.
        """
        self.log.error(f'task-event=graceful-shutdown-initiated, reason={reason}')

        # Tier 1: Send shutdown notification (always, never filtered)
        if self.notifications_enabled:
            message = f'App is shutting down: {reason}'
            self._store_and_maybe_send('shutdown', 'High', message, should_send=True)

        self.pause_all()
        self.kill_all()
        if self.exit_service:
            self.exit_service.exit(ExitCode.FAILURE, f'Shutting down: {reason}')

    def _send_digest(self, now: datetime) -> None:  # noqa: C901
        """Sweep job state and send a digest notification if anything noteworthy happened.

        Tier 2: periodic digest batched into fixed windows. Each job appears in at most
        2 digests (retrying + resolution). Self-healed jobs are omitted.
        """
        retrying = []
        perm_failed = []
        recovered = []

        status_failed = self.settings.job.status_failed

        for job in self.db.load_all(JobRequestModel):
            job_id = job.request_id

            # Retrying: has failures, still pending (not permanently failed), not yet reported
            if (
                job.failure_count > 0
                and job.status.casefold() != status_failed
                and job_id not in self.reported_retrying
            ):
                # Only report if first failure occurred since last digest
                if job.date_failed is not None and job.date_failed >= self.last_digest_time:
                    retrying.append(job)

            # Permanently failed: status is 'failed', not yet reported as resolved
            elif job.status.casefold() == status_failed and job_id not in self.reported_resolved:
                perm_failed.append(job)

            # Recovered: completed, was previously reported as retrying, not yet resolved
            elif (
                job.date_completed is not None
                and job_id in self.reported_retrying
                and job_id not in self.reported_resolved
            ):
                # Self-heal omission: if first failure and completion both in this window, skip
                if job.date_failed is not None and job.date_failed >= self.last_digest_time:
                    continue
                recovered.append(job)

        if not retrying and not perm_failed and not recovered:
            self.last_digest_time = now
            return

        notification_types = getattr(
            self.settings,
            'notification_types',
            ['retrying', 'permanently_failed', 'recovered'],
        )

        if retrying:
            job_ids = ', '.join(j.request_id for j in retrying)
            msg = f'{len(retrying)} job(s) ({job_ids}) failing and retrying'
            should_send = 'retrying' in notification_types
            self._store_and_maybe_send('retrying', 'Medium', msg, should_send)
            self.reported_retrying.update(j.request_id for j in retrying)

        if perm_failed:
            job_ids = ', '.join(j.request_id for j in perm_failed)
            msg = f'{len(perm_failed)} job(s) ({job_ids}) permanently failed'
            should_send = 'permanently_failed' in notification_types
            self._store_and_maybe_send('permanently_failed', 'High', msg, should_send)
            self.reported_resolved.update(j.request_id for j in perm_failed)

        if recovered:
            job_ids = ', '.join(j.request_id for j in recovered)
            msg = f'{len(recovered)} job(s) ({job_ids}) recovered'
            should_send = 'recovered' in notification_types
            self._store_and_maybe_send('recovered', 'Low', msg, should_send)
            self.reported_resolved.update(j.request_id for j in recovered)

        self.last_digest_time = now

    def _store_and_maybe_send(
        self, category: str, priority: str, message: str, should_send: bool
    ) -> None:
        """Store notification in json_db and optionally send via TC Notification API."""
        api_request = None
        api_response = None
        send_status = None
        status_code = None
        status_text = None

        if should_send:
            result = self.notification_service.send(message, priority)
            send_status = result['send_status']
            status_code = result['status_code']
            status_text = result['status_text']
            api_request = result['api_request']
            api_response = result['api_response']

        notification = NotificationModel(
            category=category,
            priority=priority,
            message=message,
            send_status=send_status,
            send_status_code=status_code,
            send_status_text=status_text,
            api_request=api_request,
            api_response=api_response,
        )
        self.db.save(notification)

    def _send_signal_to_task(self, send_signal: signal.Signals, to_task: 'TaskABC'):
        """Send signal to task."""
        if to_task.process is None or not to_task.process.is_alive():
            self.log.warning(
                f'event=send-signal-to-task-failed, task-name={to_task.task_settings.name}, '
                f'reason=task-not-running'
            )
            return
        self.log.trace(
            f'event=send-signal-to-task, signal={send_signal}, '
            f'task-name={to_task.task_settings.name}, pid={to_task.process.pid}'
        )
        os.kill(to_task.process.pid, send_signal)
