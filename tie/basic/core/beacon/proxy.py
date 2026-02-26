"""A proxy for a type that can be injected at runtime."""

from typing import Generic, TypeVar

_NotResolved = object()


A = TypeVar('A')


class InjectionProxy(Generic[A]):
    """A proxy for a type that can be injected at runtime."""

    __slots__ = ['__factory', '__resolved']

    def __init__(self, _type: type[A], factory):
        """."""
        object.__setattr__(self, '__factory', factory)
        object.__setattr__(self, '__resolved', _NotResolved)

    #
    # proxying (special cases)
    #
    def __getattribute__(self, name):
        """."""
        resolved = object.__getattribute__(self, '__resolved')
        if resolved is _NotResolved:
            resolved = object.__getattribute__(self, '__factory')()
            object.__setattr__(self, '__resolved', resolved)

        return getattr(object.__getattribute__(self, '__resolved'), name)

    def __delattr__(self, name):
        """."""
        resolved = object.__getattribute__(self, '__resolved')
        if resolved is _NotResolved:
            resolved = object.__getattribute__(self, '__factory')()
            object.__setattr__(self, '__resolved', resolved)
        delattr(object.__getattribute__(self, '__resolved'), name)

    def __setattr__(self, name, value):
        """."""
        resolved = object.__getattribute__(self, '__resolved')
        if resolved is _NotResolved:
            resolved = object.__getattribute__(self, '__factory')()
            object.__setattr__(self, '__resolved', resolved)
        setattr(object.__getattribute__(self, '__resolved'), name, value)

    def __nonzero__(self):
        """."""
        resolved = object.__getattribute__(self, '__resolved')
        if resolved is _NotResolved:
            resolved = object.__getattribute__(self, '__factory')()
            object.__setattr__(self, '__resolved', resolved)
        return bool(object.__getattribute__(self, '__resolved'))

    def __str__(self):
        """."""
        resolved = object.__getattribute__(self, '__resolved')
        if resolved is _NotResolved:
            resolved = object.__getattribute__(self, '__factory')()
            object.__setattr__(self, '__resolved', resolved)
        return str(object.__getattribute__(self, '__resolved'))

    def __repr__(self):
        """."""
        resolved = object.__getattribute__(self, '__resolved')
        if resolved is _NotResolved:
            resolved = object.__getattribute__(self, '__factory')()
            object.__setattr__(self, '__resolved', resolved)
        return repr(object.__getattribute__(self, '__resolved'))

    #
    # factories
    #
    _special_names = (
        '__abs__',
        '__add__',
        '__and__',
        '__call__',
        '__cmp__',
        '__coerce__',
        '__contains__',
        '__delitem__',
        '__delslice__',
        '__div__',
        '__divmod__',
        '__eq__',
        '__float__',
        '__floordiv__',
        '__ge__',
        '__getitem__',
        '__getslice__',
        '__gt__',
        '__hash__',
        '__hex__',
        '__iadd__',
        '__iand__',
        '__idiv__',
        '__idivmod__',
        '__ifloordiv__',
        '__ilshift__',
        '__imod__',
        '__imul__',
        '__int__',
        '__invert__',
        '__ior__',
        '__ipow__',
        '__irshift__',
        '__isub__',
        '__iter__',
        '__itruediv__',
        '__ixor__',
        '__le__',
        '__len__',
        '__long__',
        '__lshift__',
        '__lt__',
        '__mod__',
        '__mul__',
        '__ne__',
        '__neg__',
        '__oct__',
        '__or__',
        '__pos__',
        '__pow__',
        '__radd__',
        '__rand__',
        '__rdiv__',
        '__rdivmod__',
        '__reduce__',
        '__reduce_ex__',
        '__repr__',
        '__reversed__',
        '__rfloorfiv__',
        '__rlshift__',
        '__rmod__',
        '__rmul__',
        '__ror__',
        '__rpow__',
        '__rrshift__',
        '__rshift__',
        '__rsub__',
        '__rtruediv__',
        '__rxor__',
        '__setitem__',
        '__setslice__',
        '__sub__',
        '__truediv__',
        '__xor__',
        'next',
    )

    @classmethod
    def _create_class_proxy(cls, theclass):
        """Create a proxy for the given class"""

        def make_method(name):
            def method(self, *args, **kw):
                resolved = object.__getattribute__(self, '__resolved')
                if resolved is _NotResolved:
                    resolved = object.__getattribute__(self, '__factory')()
                    object.__setattr__(self, '__resolved', resolved)

                return getattr(object.__getattribute__(self, '__resolved'), name)(*args, **kw)

            return method

        namespace = {}
        for name in cls._special_names:
            if hasattr(theclass, name):
                namespace[name] = make_method(name)
        return type(f'{cls.__name__}({theclass.__name__})', (cls,), namespace)

    def __new__(
        cls,
        type_: A,
        factory,  # noqa: ARG004
    ) -> 'type[InjectionProxy[A]]':
        """Create an proxy instance referencing `obj`."""
        return object.__new__(cls._create_class_proxy(type_))


def reify(obj: A) -> A:
    """Reify a function or property."""
    try:
        real_value = object.__getattribute__(obj, '__resolved')
        if real_value is _NotResolved:
            real_value = object.__getattribute__(obj, '__factory')()
            object.__setattr__(obj, '__resolved', real_value)
        return real_value
    except AttributeError:
        return obj
