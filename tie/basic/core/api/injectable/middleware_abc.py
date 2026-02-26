"""Declares an abstract base class for Middleware."""

from abc import ABC, abstractmethod

from core.api.falcon_request import FalconRequest
from core.api.falcon_response import FalconResponse


class MiddlewareABC(ABC):
    """Abstract base class for all middleware implementations."""

    @abstractmethod
    def process_request(self, req: FalconRequest, resp: FalconResponse):
        """Process the request before routing it."""

    @abstractmethod
    def process_resource(
        self, req: FalconRequest, resp: FalconResponse, resource: object, params: dict
    ):
        """Process the request after routing."""

    @abstractmethod
    def process_response(
        self,
        req: FalconRequest,
        resp: FalconResponse,
        resource: object,
        req_succeeded: bool,
    ):
        """Post-processing of the response (after routing)."""
