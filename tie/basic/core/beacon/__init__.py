"""Define an api for doing extremely late-binding dependency injection."""

from .beacon import factory, inject, provide
from .proxy import reify
from .transpose import Transpose
