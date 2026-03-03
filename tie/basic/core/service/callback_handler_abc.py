"""Callback Module"""

from abc import ABC, abstractmethod
from collections.abc import Callable


class CallbackHandlerABC(ABC):
    """Callback handler abstract base class."""

    def __init__(self):
        """Init method for the CallbackHandlerABC class."""
        # Initialize the callbacks dictionary
        self.callbacks: dict[str, Callable] = {}

    def register_callback(self, name: str, func: Callable):
        """Register a callback function for a specific hook."""
        if name not in self.callbacks:
            error_message = (
                f'{name} is not a valid callback hook.'
                f'Valid hooks are: {list(self.callbacks.keys())}'
            )
            raise ValueError(error_message)
        if not callable(func):
            msg = f"The callback for '{name}' must be callable."
            raise TypeError(msg)
        self.callbacks[name] = func

    def trigger_callback(self, name: str, *args, **kwargs):
        """Trigger a specific callback by name."""
        if self.callbacks.get(name):
            return self.callbacks[name](*args, **kwargs)
        msg = f"No callback registered for '{name}'"
        raise ValueError(msg)

    @abstractmethod
    def define_callbacks(self):
        """Abstract method to define valid callback hooks."""
