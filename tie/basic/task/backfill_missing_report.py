"""Scheduled Task"""

# standard library
from typing import AnyStr

# first-party
from core.task.backfill_missing_report_abc import BackfillMissingReportABC

# from core.tcvf.task.backfill_missing_report_abc import CustomTag, DocumentRetrievalError


class BackfillMissingReport(BackfillMissingReportABC):
    """Scheduled Task"""

    # process_custom_tag is a method that takes a report_id and returns the document
    # custom_tag = CustomTag(name='custom_tag', processor=self.process_custom_tag)
    # self.register_custom_tag(custom_tag)

    def retrieve_document(self, report_id: str) -> AnyStr | None:
        """Retrieve document."""
        # Retrieve the document from disk or API. Return None if error.
        msg = 'retrieve_document method not implemented.'
        raise NotImplementedError(msg)

    def document_attached_cleanup(self, report_id: str):  # noqa: ARG002
        """Document Cleanup"""
        # Cleanup the attached document. This method is optional.
        return
