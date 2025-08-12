"""Define higher-order functions for common operations."""

# standard library
import functools
from collections.abc import Callable, Iterable
from contextlib import AbstractContextManager, ExitStack, contextmanager
from typing import Any, ParamSpec, TypeVar

A = TypeVar('A')
B = TypeVar('B')
P = ParamSpec('P')


def compose(
    first: Callable[P, A],
    second: Callable[[A], B],
) -> Callable[P, B]:
    """Return a function that is the composition of the given functions."""

    def composed_function(*args: P.args, **kwargs: P.kwargs) -> B:
        """Return the result of the composed function."""
        return second(first(*args, **kwargs))

    return composed_function


def pipe(first: Callable[P, A], *rest: Callable, last: Callable[[Any], B]) -> Callable[P, B]:
    """Return a function that pipes the output of the first function through the other functions."""
    fns = [first, *rest, last]
    return functools.reduce(compose, fns)


@contextmanager
def combine_context_managers(*managers: AbstractContextManager[A]) -> Iterable[list[A]]:
    """Combine multiple context managers into one.

    The yielded value will be a list of the values yielded by each context manager.
    """
    with ExitStack() as stack:
        yield [stack.enter_context(m) for m in managers]
