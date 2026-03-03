"""Middleware module"""

from abc import ABC

from core.api.error.util import error
from core.api.middleware_abc import MiddlewareABC


class ErrorMiddleware(MiddlewareABC, ABC):
    """Middleware module"""

    def process_resource(self, _req, _resp, resource, _params):
        """Process resource method."""
        resource.error = error
