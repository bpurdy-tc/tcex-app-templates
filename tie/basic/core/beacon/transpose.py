"""Define a protocol for objects that can be transposed"""

from typing import Protocol


class Transpose(Protocol):
    """Define a protocol for objects that can be transposed.

    This enables the beacon injector to transparently swap out objects provided by the injector.
    """

    def __transpose__(self, new_, provided_for: type) -> None:
        """Transpose the object with the new_ value.

        Update new_ so that its state is the same as this object, and it can be swapped out
        with self without any issues.

        Args:
            new_ (Any): The object to be updated to match the state of this object.
            provided_for (Type): The type of object that `new_` is being provided for.

        Returns:
            None
        """
