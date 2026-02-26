"""Injectable types for path pipe tasks.

None of these types should ever be initialized, rather they are defined to be used as type hints
and for injection via core.beacon.inject.

For example:

> from core.beacon.inject import inject
> update_heartbeat: UpdateHeartbeat = inject(UpdateHeartbeat)
> update_heartbeat(verbose=False)
"""

from pathlib import Path
from typing import Protocol

from model import JobRequestModel

CurrentJob = type('CurrentJob', (JobRequestModel,), {})


class UpdateHeartbeat(Protocol):
    """Protocol for a function that updates the heartbeat of a task."""

    def __call__(self, verbose: bool = True) -> None:
        """Update the heartbeat of a task."""


# TaskOutputDir is a type hint for the output directory of a task.
TaskOutputDir = type('TaskOutputDir', (Path,), {})

# TaskInputDir is a type hint for the input directory of a task.
TaskInputDir = type('TaskInputDir', (Path,), {})
