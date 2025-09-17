"""ThreatConnect Preflight Check Service"""

# standard library
import logging
from pathlib import Path

# third-party
from tcex import TcEx
from tcex.logger.trace_logger import TraceLogger

# first-party
from core.app.enums import PREFLIGHT_CHECKS
from core.service.current_running_process import CurrentRunningProcess

logger = logging.getLogger('tcex')


class PreflightCheckService:
    """Service for performing preflight checks."""

    def __init__(self, tcex):
        """Initialize class properties."""
        self.tcex: TcEx = tcex
        self.log: TraceLogger = logger
        self.mapping = {
            PREFLIGHT_CHECKS.FILESYSTEM: self._check_filesystem,
            PREFLIGHT_CHECKS.TC_API: self._check_tc_api,
            PREFLIGHT_CHECKS.DUPLICATE_PROCESSES_RUNNING: self._check_duplicate_service,
        }
        self.preflight_checks = set()

    def register_preflight_check(self, check):
        """Register a preflight check."""
        self.preflight_checks.add(check)

    def perform_checks(self):
        """Perform all preflight checks."""
        for preflight_check in self.preflight_checks:
            preflight_check()

    def _check_filesystem(self):
        """Check the filesystem for required conditions."""
        preflight_check_file = self.tcex.inputs.model.tc_out_path / 'preflight'
        try:
            preflight_check_file.write_text('preflight check')
            self.log.info(
                'action=check_filesystem, '
                'message=Preflight check for filesystem passed, '
                f'file={preflight_check_file}'
            )
        except Exception as ex:
            self.log.exception(
                'action=check_filesystem, message=Preflight check for filesystem failed, '
            )
            ex_msg = 'Preflight check for filesystem failed.'
            raise RuntimeError(ex_msg) from ex

    def _check_tc_api(self):
        """Check the ThreatConnect API for required conditions."""
        try:
            owners = self.tcex.api.tc.v3.security.owners()
            owners = [o.model.name for o in owners]
            self.log.info(
                f'action=check_tc_api, message=Preflight check for TC API passed, owners={owners}'
            )
        except Exception as ex:
            self.log.exception('action=check_tc_api, message=Preflight check for TC API failed.')
            ex_msg = 'Preflight check for TC API failed.'
            raise RuntimeError(ex_msg) from ex

    def _check_attributes(self):
        """Check the attributes for required conditions."""
        attributes_path = Path('attributes.json')
        if not attributes_path.exists():
            self.log.error(f'attributes.json file not found at {attributes_path}')
            msg = 'attributes.json file is required for preflight checks.'
            raise RuntimeError(msg)

        try:
            list(self.tcex.api.tc.v3.ti.group_attributes())
        except Exception as ex:
            self.log.exception('Failed to fetch attributes from ThreatConnect API.')
            msg = 'Could not fetch attributes from ThreatConnect API.'
            raise RuntimeError(msg) from ex

    def _check_duplicate_service(self):
        """Check for duplicate services and shutdown all services if found."""
        current_running_processes = CurrentRunningProcess(self.tcex)
        current_running_processes.load()

        if current_running_processes.should_write():
            current_running_processes.write()
        else:
            current_running_processes.file.unlink()
            current_running_processes.shutdown_existing_service()
