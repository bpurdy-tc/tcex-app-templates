"""Scheduled action model."""

# standard library
from collections.abc import Callable
from datetime import timedelta
from typing import Any

# third-party
from pydantic import BaseModel, Field


class ScheduledActionModel(BaseModel):
    """Defines a scheduled job with a function, interval, and arguments."""

    name: str = Field(..., description='Unique name for the job')
    interval: timedelta = Field(..., description='Time interval for the job')
    fn: Callable = Field(..., description='Function to execute')
    kwargs: dict[str, Any] = Field(default_factory=dict, description='Arguments for the function')
