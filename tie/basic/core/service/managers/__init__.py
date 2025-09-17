"""Define several 'managers' for handling data operations.

A manager is a way to manage incremental updates, suck as writing chunks of data to a file, or
updating metrics, or updating counts.  Critically, there's a "final" operation for managers: when
a manager is done, it should perform a final operation for any leftover items.
"""

from .operation_managers import (
    RequestCountField,
    batch_writer_manager,
    combine_managers,
    file_writer_manager,
    processing_metrics_manager,
    request_counts_manager,
)
