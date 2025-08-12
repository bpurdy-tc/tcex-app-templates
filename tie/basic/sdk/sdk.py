"""SDK Module"""

# standard library
from functools import cached_property

# third-party
from tcex import TcEx

BASE_URL = 'BASE_URL'  # TODO: Update this with the correct base URL


class SDK:
    """SDK for interacting with the API."""

    def __init__(self, tcex: TcEx):
        """Initialize the SDK."""
        self.tcex = tcex

    @cached_property
    def session(self):
        """Return the session."""
        self.tcex.log.info('action=create_session')
        session = self.tcex.session.external
        session.retry(status_forcelist=[401, 500, 502, 504])
        session.base_url = BASE_URL
        return session

    def events(self, start_time, end_time):  # noqa: ARG002
        """Return the events API."""
        yield from [{'id': 1, 'name': 'Event 1'}, {'id': 2, 'name': 'Event 2'}]

    def test_connection(self, settings):  # noqa: ARG002
        """Test the connection to the API."""
        return
