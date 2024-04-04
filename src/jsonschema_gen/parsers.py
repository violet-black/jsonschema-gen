"""Collection of type parsers."""

import collections.abc as c
import inspect
import typing as t
from abc import ABC
from contextlib import suppress
from dataclasses import MISSING, fields, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from inspect import _ParameterKind  # noqa: magic is required
from numbers import Number
from uuid import UUID, SafeUUID
from weakref import proxy

import jsonschema_gen.schema as j
from jsonschema_gen.utils import (NoneType, compatible_py39, compatible_py310,
                                  compatible_py311, get_args,
                                  get_function_summary, get_generic_alias,
                                  get_origin, is_namedtuple, is_typeddict,
                                  is_union)

__all__ = [
    'TYPES', 'IncompatibleTypesError', 'Parser',
    'TypeParser', 'ListParser', 'TupleParser', 'DictParser', 'SetParser',
    'StringParser', 'IntegerParser', 'NumberParser', 'BooleanParser',
    'ConstantParser', 'EnumTypeParser', 'EnumValueParser', 'TypedDictParser',
    'NewTypeParser', 'NamedTupleParser', 'AnyParser', 'NullParser', 'UnionParser'
]

TYPES: t.List[t.Type['TypeParser']] = []  #: default collection of type parsers


class IncompatibleTypesError(ValueError):
    """Annotation type is incompatible with JSONSchema."""


class FunctionAnnotation(t.NamedTuple):
    """Function annotation with input kwargs and return values schemas."""
    kwargs: t.Optional[j.Object]
    returns: t.Optional[j.JSONSchemaType]


class Parser:
    """Python annotations parser.

    Parse an annotation:

    >>> Parser().parse_annotation(t.List[str], default=[]).json_repr()
    {'items': {'type': 'string'}, 'default': [], 'type': 'array'}

    Parse a function (method):

    >>> def test(value: str) -> int: ...
    >>> annotations = Parser().parse_function(test)
    >>> annotations.kwargs.json_repr()
    {'properties': {'value': {'type': 'string'}}, 'additionalProperties': False, 'required': ['value'], 'type': 'object'}

    Parse a class:

    >>> class C:
    ...     def test(self, value: str) -> int: ...
    >>> annotations_map = Parser().parse_class(C)
    >>> annotations_map['test'].kwargs.json_repr()
    {'properties': {'value': {'type': 'string'}}, 'additionalProperties': False, 'required': ['value'], 'type': 'object'}
    """

    def __init__(
            self, *,
            strict: bool = True,
            private_arg_prefix: str = '_',
            types: t.Optional[t.List[t.Type['TypeParser']]] = None,
            locals: t.Optional[dict] = None
    ):
        """Initialize

        :param strict: strict parsing - allow only JSONSchema compatible types
            for example: UUID type is not allowed in `strict` because it's not an actual data type in JSON
        :param private_arg_prefix: ignore args starting with such prefix
        :param types: list of type parsers, by default :py:obj:`~jsonschema_gen.parsers.TYPES` is used
        :param locals: a map of local variables to resolve plain string references in type hints
        """
        self.strict = strict
        self.private_arg_prefix = private_arg_prefix
        self.types = types or TYPES
        self.locals = locals or {}
        self._types = [t(self) for t in self.types]

    def parse_class(self, cls: t.Type, /) -> t.Dict[str, FunctionAnnotation]:
        """Parse class methods and create an annotation map for the whole class."""
        _method_map = {}
        for name, value in vars(cls).items():
            if self.private_arg_prefix and name.startswith(self.private_arg_prefix):
                continue
            if inspect.isfunction(value):
                _method_map[name] = self.parse_function(value, cls)
        return _method_map

    def parse_function(self, f: t.Callable, /, cls: t.Optional[t.Type] = None) -> FunctionAnnotation:
        """Parse method or function arguments and return type into jsonschema style annotations."""
        sign = inspect.signature(f)
        params, required = {}, []
        additional_properties = False
        is_staticmethod = isinstance(f, staticmethod)

        for n, (name, arg) in enumerate(sign.parameters.items()):

            if self.private_arg_prefix and name.startswith(self.private_arg_prefix):
                continue

            # ignoring the first argument for class and instance methods
            if cls and n == 0 and not is_staticmethod:
                continue

            if arg.kind == _ParameterKind.VAR_POSITIONAL:
                continue

            if arg.kind == _ParameterKind.VAR_KEYWORD:
                additional_properties = True
                continue

            if arg.kind == _ParameterKind.POSITIONAL_ONLY:
                raise IncompatibleTypesError('Positional only arguments cannot be converted to a JSONSchema object.')

            if type(arg.annotation) is t.TypeVar:
                if cls:
                    annotation = _parse_generic_class(cls, arg.annotation)
                else:
                    annotation = TypeVarParser(self).parse_annotation(arg.annotation)
            else:
                annotation = arg.annotation

            if arg.default == arg.empty:
                default = ...
                required.append(name)
            else:
                default = arg.default

            params[name] = self.parse_annotation(annotation, default=default)

        if params:
            params = j.Object(properties=params, required=required, additionalProperties=additional_properties)
        else:
            params = None

        if sign.return_annotation is inspect._empty:  # noqa: magic
            returns = None
        else:
            returns = self.parse_annotation(sign.return_annotation, default=...)
        return FunctionAnnotation(params, returns)

    def parse_annotation(self, annotation, /, default=...) -> j.JSONSchemaType:
        """Convert python annotation into a jsonschema object."""
        if type(annotation) is t.ForwardRef:
            annotation = self.locals.get(annotation.__forward_arg__, t.Any)

        for parser in self._types:
            if not parser.can_parse(annotation):
                continue
            if self.strict and not parser.strict:
                continue

            annotation = parser.parse_annotation(annotation)
            if default is not ...:
                annotation.default = default
            return annotation

        if self.strict:
            raise IncompatibleTypesError(
                f'Unable to parse annotation of type {annotation} as jsonschema type in strict mode')

        title = None if annotation == inspect._empty else str(annotation)  # noqa: magic
        return j.JSONSchemaObject(title=title, default=default)


class TypeParser(ABC):
    """Type parser"""

    types: t.Tuple[t.Type]
    annotation: t.Type[j.JSONSchemaObject]
    attrs: dict = None
    strict: bool = True

    def __init__(self, _parser: 'Parser'):
        self._parser = proxy(_parser)

    def can_parse(self, annotation, /) -> bool:
        origin = get_origin(annotation)
        return origin in self.types if origin else annotation in self.types

    def parse_annotation(self, annotation, /) -> j.JSONSchemaType:
        _attrs = {} if self.attrs is None else self.attrs
        return self.annotation(**_attrs)  # noqa

    def parse_args(self, args, /):
        if args:
            for arg in args:
                if arg is not ...:
                    yield self._parser.parse_annotation(arg)


def _parse_generic_class(cls: t.Type, annotation, /) -> j.JSONSchemaObject:
    """Parse a class containing Generic hints in itself."""
    alias = base_alias = get_generic_alias(cls)
    args = base_args = alias.__args__
    while base_alias:
        base_args = base_alias.__args__
        base_cls = base_alias.__origin__
        base_alias = get_generic_alias(base_cls)
    with suppress(ValueError, IndexError):
        annotation = args[base_args.index(annotation)]
    return annotation


class AnyParser(TypeParser):
    types = (t.Any,)
    annotation = j.JSONSchemaObject


class StringParser(TypeParser):
    types = (str, bytes, t.AnyStr)
    annotation = j.String


class UUIDParser(TypeParser):
    types = (UUID, SafeUUID)
    annotation = j.GUID
    strict = False


class DateParser(TypeParser):
    types = (date,)
    annotation = j.Date
    strict = False


class DateTimeParser(TypeParser):
    types = (datetime,)
    annotation = j.DateTime
    strict = False


class IntegerParser(TypeParser):
    types = (int,)
    annotation = j.Integer


class NumberParser(TypeParser):
    types = (float, Decimal, Number)
    annotation = j.Number


class BooleanParser(TypeParser):
    types = (bool,)
    annotation = j.Boolean


class NullParser(TypeParser):
    types = (None, NoneType)
    annotation = j.Null


class TypeVarParser(TypeParser):

    def can_parse(self, annotation, /) -> bool:
        return isinstance(annotation, t.TypeVar)

    def parse_annotation(self, annotation: t.TypeVar, /) -> j.JSONSchemaType:
        title = annotation.__name__
        annotation = annotation.__bound__
        if annotation:
            arg = self._parser.parse_annotation(annotation)
        else:
            arg = j.JSONSchemaObject()
        arg.title = title
        return arg


class NewTypeParser(TypeParser):

    def can_parse(self, annotation, /) -> bool:
        if compatible_py310():
            return isinstance(annotation, t.NewType)  # noqa: magic
        else:
            return getattr(annotation, '__qualname__', '').split('.')[0] == 'NewType'

    def parse_annotation(self, annotation, /) -> j.JSONSchemaType:
        title = annotation.__name__
        annotation = annotation.__supertype__
        arg = self._parser.parse_annotation(annotation)
        arg.title = title
        return arg


class ConstantParser(TypeParser):

    def can_parse(self, annotation, /) -> bool:
        return getattr(annotation, '__origin__', None) is t.Literal

    def parse_annotation(self, annotation, /) -> j.JSONSchemaType:
        return j.Enum(enum=list(annotation.__args__))


class UnionParser(TypeParser):

    def can_parse(self, annotation, /) -> bool:
        return is_union(annotation)

    def parse_annotation(self, annotation, /) -> j.JSONSchemaType:
        args = get_args(annotation)
        return j.AnyOf(list(self.parse_args(args)))


class ListParser(TypeParser):
    types = (list, t.List, t.Collection, c.Collection, c.Iterable, t.Iterable)
    annotation = j.Array

    def parse_annotation(self, annotation, /) -> j.JSONSchemaType:
        args = get_args(annotation)
        if args is None:
            return self.annotation()
        _args = []
        for arg in self.parse_args(args):
            if type(arg) is j.AnyOf:
                arg = t.cast(j.AnyOf, arg)
                _args.extend(arg.items)  # noqa (ported)
            else:
                _args.append(arg)
        return self.annotation(items=_args[0])


class SetParser(ListParser):
    types = (set, frozenset, t.Set, c.Set, t.FrozenSet, t.MutableSet, c.MutableSet)
    annotation = j.Array

    def parse_annotation(self, annotation, /) -> j.JSONSchemaType:
        annotation = super().parse_annotation(annotation)
        annotation.uniqueItems = True
        return annotation


class TupleParser(ListParser):
    types = (tuple, t.Tuple)
    annotation = j.Array

    def parse_annotation(self, annotation, /) -> j.JSONSchemaType:
        args = get_args(annotation)
        if not args or (len(args) > 1 and args[1] is ...):
            return super().parse_annotation(annotation)
        return self.annotation(prefixItems=list(self.parse_args(args)))


class DictParser(TypeParser):
    types = (dict, c.Mapping, t.Mapping, t.MutableMapping, c.MutableMapping)
    annotation = j.Object

    def parse_annotation(self, annotation, /) -> j.JSONSchemaType:
        args = get_args(annotation)
        properties = None
        if args and len(annotation.__args__) > 1:
            if self._parser.strict and annotation.__args__[0] not in (t.AnyStr, str, bytes):
                raise IncompatibleTypesError(f'Dictionary keys must be strings, got {annotation.__args__[0]}')
            if annotation.__args__[1] not in (t.Any, ...):
                properties = {
                    '^.+$': self._parser.parse_annotation(annotation.__args__[1])
                }
        return self.annotation(patternProperties=properties)


class TypedDictParser(TypeParser):
    annotation = j.Object

    def can_parse(self, annotation, /) -> bool:
        return is_typeddict(annotation)

    def parse_annotation(self, annotation: t.TypedDict, /) -> j.JSONSchemaType:
        title = annotation.__name__
        total = getattr(annotation, '__total__', True)
        properties, required = {}, []
        for key, arg in annotation.__annotations__.items():
            origin = get_origin(arg)
            if compatible_py311():
                if origin is t.Required:  # noqa: magic
                    arg = get_args(arg)[0]
                    required.append(key)
                elif origin is t.NotRequired:  # noqa: magic
                    arg = get_args(arg)[0]
                elif total or key in annotation.__required_keys__:  # noqa: magic
                    required.append(key)
            elif compatible_py39():
                if total or key in annotation.__required_keys__:  # noqa: magic
                    required.append(key)
            elif total:
                required.append(key)
            arg = self._parser.parse_annotation(arg)
            properties[key] = arg
        return self.annotation(
            properties=properties,
            required=required,
            description=annotation.__doc__,
            additionalProperties=False,
            title=title,
        )


class NamedTupleParser(TypeParser):
    annotation = j.Array
    strict = False

    def can_parse(self, annotation, /) -> bool:
        return is_namedtuple(annotation)

    def parse_annotation(self, annotation: t.NamedTuple, /) -> j.JSONSchemaType:
        title = annotation.__name__
        defaults = annotation._field_defaults  # noqa: no public attr
        annotations = getattr(annotation, '__annotations__', {})
        items = []
        for key in annotation._fields:  # noqa: no public attr
            arg = self._parser.parse_annotation(annotations[key]) if key in annotations else j.JSONSchemaObject()
            arg.title = key
            if key in defaults:
                arg.default = defaults[key]
            items.append(arg)
        return self.annotation(prefixItems=items, description=annotation.__doc__, title=title)


class EnumValueParser(TypeParser):
    types = (Enum,)
    annotation = j.Const
    strict = False

    def can_parse(self, annotation, /) -> bool:
        return isinstance(annotation, self.types)

    def parse_annotation(self, annotation: Enum, /) -> j.JSONSchemaType:
        return j.Const(const=annotation.value, title=f'{annotation.__class__.__name__}.{annotation.name}')


class EnumTypeParser(TypeParser):
    types = (Enum,)
    annotation = j.Enum
    strict = False

    def can_parse(self, annotation, /) -> bool:
        return inspect.isclass(annotation) and issubclass(annotation, Enum)

    def parse_annotation(self, annotation: t.Type[Enum], /) -> j.JSONSchemaType:
        title = annotation.__name__
        return self.annotation(
            description=annotation.__doc__,
            enum=[v.value for k, v in annotation._member_map_.items()],  # noqa: no public attr
            title=title,
        )


class DataclassParser(TypeParser):
    annotation = j.Object
    strict = False

    def can_parse(self, annotation, /) -> bool:
        return is_dataclass(annotation)

    def parse_annotation(self, annotation, /) -> j.JSONSchemaType:
        title = annotation.__name__
        properties, required = {}, []
        for field in fields(annotation):
            if not field.name.startswith('_'):
                properties[field.name] = arg = self._parser.parse_annotation(field.type)
                if field.default is MISSING:
                    required.append(field.name)
                else:
                    arg.default = field.default
        return self.annotation(
            properties=properties, required=required, additionalProperties=False, title=title,
            description=get_function_summary(annotation.__doc__))


for value in tuple(locals().values()):
    if inspect.isclass(value) and issubclass(value, TypeParser) and value is not TypeParser:
        TYPES.append(value)
