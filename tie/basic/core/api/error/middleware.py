"""Middleware module"""

# standard library
from abc import ABC

# first-party
from core.api.error.util import error
from core.api.middleware_abc import MiddlewareABC


# pylint: disable=unused-argument
class ErrorMiddleware(MiddlewareABC, ABC):
    """Middleware module"""

    def process_resource(self, _req, _resp, resource, _params):
        """Process resource method."""
        resource.error = error
