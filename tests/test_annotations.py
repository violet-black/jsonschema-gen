import collections.abc as c
import typing as t
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from numbers import Number
from uuid import UUID, SafeUUID

import pytest

from jsonschema_gen.parsers import *


class _InnerSchema(t.TypedDict):
    id: str
    value: int


class _CompoundSchema(t.TypedDict):
    """Compound schema"""

    id: str
    value: _InnerSchema


class _CompoundSchemaIndirectRef(t.TypedDict):
    id: str
    value: "_InnerSchema"


class _Schema(t.TypedDict):
    """Schema"""

    id: str
    value: int


class _VariableSchema(t.TypedDict, total=False):
    """Variable schema"""

    id: str
    value: int


class _NamedTuple(t.NamedTuple):
    id: int
    data: dict
    name: str = "test"


@dataclass
class _DataClass:
    """Data class"""

    id: int
    data: dict
    flag: bool = True


_NewTypeStr = t.NewType("_NewTypeStr", str)
_TypeVar = t.TypeVar("_TypeVar")
_TypeVarStr = t.TypeVar("_TypeVarStr", bound=str)
_T = t.TypeVar("_T", bound=dict)


class _Enum(Enum):
    """Enum value"""

    value_1 = "text"
    value_2 = 1


class _GenericClass(t.Generic[_T]):

    def f_type_var(self, value: _T): ...

    def f_default(self, value: int = 42): ...

    def f_var_kws(self, value: int, **kws): ...

    def f_pos_args(self, value: int, *args): ...


class _GenericSubclass(_GenericClass[_Schema]): ...


class _TestClass:

    value = {
        "properties": {"name": {"type": "string"}},
        "type": "object",
        "required": ["name"],
        "additionalProperties": False,
    }

    def f(self, name: str, _private: str = None): ...

    @classmethod
    def f_cls(cls, name: str, _private: str = None): ...

    @staticmethod
    def f_static(name: str, _private: str = None): ...


def func_with_positional_only_args(arg1, arg2, /, arg3): ...


BASIC_TYPES = [
    (int, {"type": "integer"}),
    (float, {"type": "number"}),
    (str, {"type": "string"}),
    (bytes, {"type": "string"}),
    (bool, {"type": "boolean"}),
    (None, {"enum": [None]}),
    (t.Any, {}),
    (Decimal, {"type": "number"}),
    (Number, {"type": "number"}),
]

SPECIAL_TYPES = [
    (datetime, {"type": "string", "format": "date-time"}),
    (date, {"type": "string", "format": "date"}),
    (UUID, {"type": "string", "format": "uuid"}),
    (SafeUUID, {"type": "string", "format": "uuid"}),
    (
        _NamedTuple,
        {
            "title": "_NamedTuple",
            "description": "_NamedTuple(id, data, name)",
            "type": "array",
            "prefixItems": [
                {"type": "integer", "title": "id"},
                {"type": "object", "title": "data"},
                {"type": "string", "title": "name", "default": "test"},
            ],
        },
    ),
    (
        _DataClass,
        {
            "title": "_DataClass",
            "description": "Data class",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "data": {"type": "object"},
                "flag": {"type": "boolean", "default": True},
            },
            "required": ["id", "data"],
            "additionalProperties": False,
        },
    ),
    (
        _Enum,
        {
            "title": "_Enum",
            "description": "Enum value",
            "enum": ["text", 1],
        },
    ),
    (
        _Enum.value_1,
        {
            "title": "_Enum.value_1",
            "const": "text",
        },
    ),
    (t.Hashable, {"title": "typing.Hashable"}),  # 'unsupported' types
]

COLLECTIONS = [
    (list, {"type": "array"}),
    (t.List[str], {"type": "array", "items": {"type": "string"}}),
    (t.List[t.List[str]], {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}),
    (t.Collection[str], {"type": "array", "items": {"type": "string"}}),
    (c.Collection, {"type": "array"}),
    (t.Iterable[str], {"type": "array", "items": {"type": "string"}}),
    (c.Iterable, {"type": "array"}),
    (tuple, {"type": "array"}),
    (t.Tuple[str], {"type": "array", "prefixItems": [{"type": "string"}]}),
    (t.Tuple[str, int], {"type": "array", "prefixItems": [{"type": "string"}, {"type": "integer"}]}),
    (t.Tuple[str, ...], {"type": "array", "items": {"type": "string"}}),
    (t.Dict[str, t.Any], {"type": "object"}),
    (t.Dict[str, dict], {"type": "object", "patternProperties": {"^.+$": {"type": "object"}}}),
    (t.Dict[str, int], {"type": "object", "patternProperties": {"^.+$": {"type": "integer"}}}),
    (t.Mapping[str, int], {"type": "object", "patternProperties": {"^.+$": {"type": "integer"}}}),
    (t.MutableMapping[str, int], {"type": "object", "patternProperties": {"^.+$": {"type": "integer"}}}),
    (c.MutableMapping, {"type": "object"}),
    (set, {"type": "array", "uniqueItems": True}),
    (frozenset, {"type": "array", "uniqueItems": True}),
    (t.Set[int], {"type": "array", "items": {"type": "integer"}, "uniqueItems": True}),
    (c.Set, {"type": "array", "uniqueItems": True}),
    (t.MutableSet[int], {"type": "array", "items": {"type": "integer"}, "uniqueItems": True}),
    (c.MutableSet, {"type": "array", "uniqueItems": True}),
    (t.FrozenSet[int], {"type": "array", "items": {"type": "integer"}, "uniqueItems": True}),
]

TYPED_DICTS = [
    (
        _Schema,
        {
            "type": "object",
            "title": "_Schema",
            "description": "Schema",
            "properties": {"id": {"type": "string"}, "value": {"type": "integer"}},
            "additionalProperties": False,
            "required": ["id", "value"],
        },
    ),
    (
        _VariableSchema,
        {
            "type": "object",
            "title": "_VariableSchema",
            "description": "Variable schema",
            "properties": {"id": {"type": "string"}, "value": {"type": "integer"}},
            "additionalProperties": False,
            "required": [],
        },
    ),
    (
        _CompoundSchema,
        {
            "type": "object",
            "title": "_CompoundSchema",
            "description": "Compound schema",
            "properties": {
                "id": {"type": "string"},
                "value": {
                    "type": "object",
                    "title": "_InnerSchema",
                    "properties": {"id": {"type": "string"}, "value": {"type": "integer"}},
                    "additionalProperties": False,
                    "required": ["id", "value"],
                },
            },
            "additionalProperties": False,
            "required": ["id", "value"],
        },
    ),
    (
        _CompoundSchemaIndirectRef,
        {
            "type": "object",
            "title": "_CompoundSchemaIndirectRef",
            "properties": {
                "id": {"type": "string"},
                "value": {
                    "type": "object",
                    "title": "_InnerSchema",
                    "properties": {"id": {"type": "string"}, "value": {"type": "integer"}},
                    "additionalProperties": False,
                    "required": ["id", "value"],
                },
            },
            "additionalProperties": False,
            "required": ["id", "value"],
        },
    ),
]

OPERATORS = [
    (t.Union[str, int], {"anyOf": [{"type": "string"}, {"type": "integer"}]}),
    (t.Optional[str], {"anyOf": [{"type": "string"}, {"enum": [None]}]}),
    (t.Union[str, None], {"anyOf": [{"type": "string"}, {"enum": [None]}]}),
    (_TypeVar, {"title": "_TypeVar"}),
    (_TypeVarStr, {"title": "_TypeVarStr", "type": "string"}),
    (_NewTypeStr, {"title": "_NewTypeStr", "type": "string"}),
    (t.Literal["test"], {"enum": ["test"]}),
]


@pytest.mark.parametrize(["annotation", "result"], [*BASIC_TYPES, *COLLECTIONS, *TYPED_DICTS, *OPERATORS])
def test_types(annotation, result):
    assert Parser(locals=globals()).parse_annotation(annotation).json_repr() == result


@pytest.mark.parametrize(
    ["annotation", "result"],
    [
        *SPECIAL_TYPES,
    ],
)
def test_special_types(annotation, result):
    assert Parser(strict=False, locals=globals()).parse_annotation(annotation).json_repr() == result


@pytest.mark.parametrize(["annotation", "result"], [*SPECIAL_TYPES, (t.Dict[int, str], ())])
def test_strict_errors(annotation, result):
    with pytest.raises(IncompatibleTypesError):
        Parser(locals=globals()).parse_annotation(annotation)


@pytest.mark.parametrize(
    ["cls", "method", "result"],
    [
        (
            _GenericClass,
            _GenericClass.f_pos_args,
            {
                "additionalProperties": False,
                "properties": {"value": {"type": "integer"}},
                "required": ["value"],
                "type": "object",
            },
        ),
        (
            _GenericClass,
            _GenericClass.f_default,
            {
                "additionalProperties": False,
                "properties": {"value": {"type": "integer", "default": 42}},
                "required": [],
                "type": "object",
            },
        ),
        (
            _GenericClass,
            _GenericClass.f_var_kws,
            {
                "additionalProperties": True,
                "properties": {"value": {"type": "integer"}},
                "required": ["value"],
                "type": "object",
            },
        ),
        (
            _GenericClass,
            _GenericClass.f_type_var,
            {
                "additionalProperties": False,
                "properties": {"value": {"title": "_T", "type": "object"}},
                "required": ["value"],
                "type": "object",
            },
        ),
        (
            _GenericSubclass,
            _GenericSubclass.f_type_var,
            {
                "additionalProperties": False,
                "properties": {
                    "value": {
                        "additionalProperties": False,
                        "description": "Schema",
                        "properties": {"id": {"type": "string"}, "value": {"type": "integer"}},
                        "required": ["id", "value"],
                        "title": "_Schema",
                        "type": "object",
                    }
                },
                "required": ["value"],
                "type": "object",
            },
        ),
    ],
)
def test_method_args_parser(cls, method, result):
    assert Parser(locals=globals()).parse_function(method, cls).kwargs.json_repr() == result


@pytest.mark.parametrize("method", [func_with_positional_only_args])
def test_method_parser_errors(method):
    with pytest.raises(IncompatibleTypesError):
        Parser(locals=globals()).parse_function(method)


def test_class_parser():
    annotations = Parser(locals=globals()).parse_class(_TestClass)
    for key, value in annotations.items():
        assert value.kwargs.json_repr() == _TestClass.value
