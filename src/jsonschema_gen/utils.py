"""Type hints manipulation utilities."""

import inspect
import sys
from textwrap import dedent
from typing import Any, Type, Union, _GenericAlias, _TypedDictMeta  # noqa: magic

__all__ = [
    'NoneType',
    'is_generic',
    'is_typeddict',
    'is_namedtuple',
    'is_union',
    'get_origin',
    'get_args',
    'get_generic_alias',
    'get_function_summary',
    'compatible_py39',
    'compatible_py310',
    'compatible_py311'
]

NoneType = type(None)


def compatible_py39() -> bool:
    return sys.version_info >= (3, 9)


def compatible_py310() -> bool:
    return sys.version_info >= (3, 10)


def compatible_py311() -> bool:
    return sys.version_info >= (3, 11)


def get_function_summary(doc: Union[str, None], /) -> Union[str, None]:
    """Extract and normalize function description (first row)."""
    if doc:
        doc = dedent(doc)
        doc = doc.split('\n')[0]
        doc.capitalize()
        return doc
    return None


def get_origin(value, /):
    return getattr(value, '__origin__', None)


def get_args(value, /):
    return getattr(value, '__args__', None)


def is_generic(value: Any, /) -> bool:
    return isinstance(value, _GenericAlias)


def get_generic_alias(obj: Type, /) -> Union[_GenericAlias, None]:
    return next((n for n in getattr(obj, '__orig_bases__', []) if is_generic(n)), None)


def is_typeddict(value, /) -> bool:
    return isinstance(value, _TypedDictMeta)


def is_namedtuple(value, /) -> bool:
    return inspect.isclass(value) and issubclass(value, tuple) and hasattr(value, '_fields')


def is_union(value, /) -> bool:
    if getattr(value, '__origin__', None) is Union:
        return True
    if compatible_py310():
        from types import UnionType
        return type(value) is UnionType
    return False
