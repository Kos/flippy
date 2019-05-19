from typing import TypeVar, Generic, Any, GenericMeta, Generator, Iterable

from django.utils import inspect
from pytest import raises


class MoreThanOneGenericParamError(TypeError):
    pass


class NoGenericParamsError(TypeError):
    pass


def collect_metas(obj, seen_bases=None) -> Iterable[GenericMeta]:
    if seen_bases is None:
        seen_bases = set()

    if hasattr(obj, "__orig_class__"):
        yield obj.__orig_class__
    if hasattr(obj, "__orig_bases__"):
        for base in obj.__orig_bases__:
            # if base in seen_bases:
            #     continue
            # seen_bases.add(base)
            if isinstance(base, GenericMeta):
                yield base
            yield from collect_metas(base, seen_bases)
    else:
        for base in type(obj).__bases__:
            # if base in seen_bases:
            #     continue
            # seen_bases.add(base)
            yield from collect_metas(base, seen_bases)


def get_generic_type(obj):
    args = [arg for meta in collect_metas(obj) for arg in meta.__args__]

    if len(args) > 1:
        raise MoreThanOneGenericParamError()
    return args[0]


class ParamType:
    pass


def test_get_generic_type():

    T = TypeVar("T")

    class Foo(Generic[T]):
        pass

    obj = Foo[ParamType]()
    assert get_generic_type(obj) is ParamType


def test_multiple_bases():
    T = TypeVar("T")

    class Base:
        pass

    class Foo(Base, Generic[T]):
        pass

    obj = Foo[ParamType]()
    assert get_generic_type(obj) is ParamType


def test_inheritance():
    T = TypeVar("T")

    class Base:
        pass

    class Derived(Base, Generic[T]):
        pass

    class MoreDerived(Unrelated, Derived[ParamType], UnrelatedToo):
        pass

    class Foo(MoreDerived):
        pass

    obj = Foo()
    assert get_generic_type(obj) is ParamType


def test_multiple_generics():
    T = TypeVar("T")
    R = TypeVar("R")

    class Base:
        pass

    class Foo(Base, Generic[T, R]):
        ...

    obj = Foo[ParamType, int]()
    with raises(MoreThanOneGenericParamError):
        get_generic_type(obj)


def test_non_generic():
    with raises(NoGenericParamsError):
        get_generic_type(ParamType())


class Unrelated:
    pass


class UnrelatedToo:
    pass
