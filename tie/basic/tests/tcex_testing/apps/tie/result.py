"""Result dataclasses returned by TIE pipeline stage runners."""

# standard library
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DownloadResult:
    """Result of a Download task run."""

    output_dir: Path
    job_request: object  # JobRequestModel — typed loosely to avoid import coupling

    @property
    def files(self) -> list[Path]:
        """All .json.gz files written by the Download task."""
        return sorted(self.output_dir.rglob('*.json.gz'))


@dataclass
class ConvertResult:
    """Result of a Convert task run."""

    output_dir: Path
    job_request: object

    @property
    def batch_files(self) -> list[Path]:
        """All batch .json.gz files written by the Convert task."""
        return sorted(self.output_dir.rglob('*.json.gz'))


@dataclass
class UploadResult:
    """Result of an Upload task run."""

    tcex: object  # TcEx instance — typed loosely to avoid import coupling
    errors: list[str] = field(default_factory=list)

    @property
    def exit_code(self) -> int:
        return getattr(getattr(self.tcex, 'exit', None), 'code', 0) or 0

    def assert_no_errors(self) -> None:
        """Assert the upload completed without hard failures."""
        hard_failure = 4  # ExitCode.HARD_FAILURE
        assert self.exit_code != hard_failure, (
            f'Upload exited with hard failure (code {self.exit_code}). See logs for details.'
        )
