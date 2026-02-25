"""Transform ABC"""

# standard library
from abc import ABC

# first-party
from core.more.transform.transform_abc import TransformABC


class CustomTransformABC(TransformABC, ABC):
    """Transform ABC

    All transforms should inherit from this class so this class
    should be used to define the common methods that all transforms should have.
    """
