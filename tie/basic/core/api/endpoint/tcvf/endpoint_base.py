"""Endpoint Base Class"""

# first-party
from sdk.sdk import SDK

from core.api.endpoint.endpoint_base_abc import EndpointBaseABC
from core.task.tasks import Tasks


class EndpointBase(EndpointBaseABC):
    """Endpoint Base Class"""

    tasks: Tasks
    sdk: SDK
