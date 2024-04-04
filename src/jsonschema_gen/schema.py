"""Jsonschema types."""
# pylint: disable=C0103

from dataclasses import dataclass, field
from typing import Any, Collection, Dict, List, Literal, Mapping, Protocol, TypeVar

__all__ = (
    "JSONSchemaObject",
    "JSONSchemaType",
    "Boolean",
    "String",
    "Number",
    "Integer",
    "Array",
    "Object",
    "AnyOf",
    "OneOf",
    "AllOf",
    "Not",
    "GUID",
    "Date",
    "DateTime",
    "Null",
    "Const",
    "Nullable",
    "Enum",
    "Email"
)

_T = TypeVar("_T")
_StringFormat = Literal[
    "JSONSchemaType",
    "date-time",
    "time",
    "date",
    "email",
    "idn-email",
    "hostname",
    "idn-hostname",
    "ipv4",
    "ipv6",
    "uri",
    "uri-reference",
    "iri",
    "iri-reference",
    "regex",
]


class JSONSchemaType(Protocol):
    """Json schema object interface."""

    def json_repr(self) -> Dict[str, Any]:
        """Produce a JSON-compatible representation of the object."""
        return _serialize_schema_keys(vars(self))


def _serialize_schema_value(value: Any, /) -> Any:
    if isinstance(value, Mapping):
        return _serialize_schema_keys(value)
    if isinstance(value, (list, tuple)):
        return [_serialize_schema_value(sub_value) for sub_value in value]
    if hasattr(value, "json_repr"):
        return value.json_repr()
    return value


def _serialize_schema_keys(obj: Mapping) -> Dict[str, Any]:
    return {
        key: _serialize_schema_value(value)
        for key, value in obj.items()
        if not key.startswith("_") and value is not None and value is not ...
    }


@dataclass
class JSONSchemaObject(JSONSchemaType):
    """Generic JSONSchema object.

    >>> JSONSchemaObject().json_repr()
    {}
    """
    title: str = None
    description: str = None
    examples: List = None
    default: Any = ...


@dataclass
class Enum(JSONSchemaType):
    """Enum value.

    >>> Enum([1, 2, 3]).json_repr()
    {'enum': [1, 2, 3]}
    """
    enum: List
    title: str = None
    description: str = None
    examples: List = None
    default: Any = ...


@dataclass
class Const(JSONSchemaType):
    """Constant value.

    See `constants <https://json-schema.org/understanding-json-schema/reference/const#constant-values>`_

    >>> Const('1').json_repr()
    {'const': '1'}
    """
    const: Any
    title: str = None
    description: str = None


@dataclass
class Boolean(JSONSchemaType):
    """Boolean type.

    See `boolean type <https://json-schema.org/understanding-json-schema/reference/boolean>`_

    >>> Boolean().json_repr()
    {'type': 'boolean'}
    """
    title: str = None
    description: str = None
    default: bool = ...

    def json_repr(self) -> Dict[str, Any]:
        data = _serialize_schema_keys(vars(self))
        data["type"] = "boolean"
        return data


@dataclass
class String(JSONSchemaType):
    """String type.

    See `string type <https://json-schema.org/understanding-json-schema/reference/string>`_

    >>> String().json_repr()
    {'type': 'string'}
    """
    minLength: int = None
    maxLength: int = None
    pattern: str = None  #: regex validation pattern
    format: _StringFormat = None  #: string format
    title: str = None
    description: str = None
    examples: List = None
    enum: List[str] = None
    default: str = ...

    def json_repr(self) -> Dict[str, Any]:
        data = _serialize_schema_keys(vars(self))
        data["type"] = "string"
        return data


@dataclass
class DateTime(String):
    """Datetime type alias.

    >>> DateTime().json_repr()
    {'format': 'date-time', 'type': 'string'}
    """
    format: str = 'date-time'


@dataclass
class Date(String):
    """Date type alias.

    >>> Date().json_repr()
    {'format': 'date', 'type': 'string'}
    """
    format: str = field(init=False)

    def __post_init__(self):
        self.format = 'date'


@dataclass
class GUID(String):
    """UUID type alias.

    >>> GUID().json_repr()
    {'format': 'uuid', 'type': 'string'}
    """
    format: str = field(init=False)

    def __post_init__(self):
        self.format = 'uuid'


@dataclass
class Email(String):
    """UUID type alias.

    >>> Email().json_repr()
    {'format': 'email', 'type': 'string'}
    """
    format: str = field(init=False)

    def __post_init__(self):
        self.format = 'email'


@dataclass
class Null(Enum):
    """Null value alias.

    >>> Null().json_repr()
    {'enum': [None]}
    """
    enum: list = field(init=False)

    def __post_init__(self):
        self.enum = [None]


@dataclass
class Number(JSONSchemaType):
    """Numeric data type.

    See `numeric type <https://json-schema.org/understanding-json-schema/reference/numeric#number>`_

    >>> Number().json_repr()
    {'type': 'number'}
    """
    multipleOf: float = None
    minimum: float = None
    maximum: float = None
    exclusiveMinimum: float = None
    exclusiveMaximum: float = None
    title: str = None
    description: str = None
    examples: List = None
    enum: List[float] = None
    default: float = ...

    def json_repr(self) -> Dict[str, Any]:
        data = _serialize_schema_keys(vars(self))
        data["type"] = "number"
        return data


@dataclass
class Integer(JSONSchemaType):
    """Integer type.

    See `integer type <https://json-schema.org/understanding-json-schema/reference/numeric#integer>`_

    >>> Integer().json_repr()
    {'type': 'integer'}
    """
    multipleOf: int = None
    minimum: int = None
    maximum: int = None
    exclusiveMinimum: int = None
    exclusiveMaximum: int = None
    title: str = None
    description: str = None
    examples: List = None
    enum: List[int] = None
    default: int = ...

    def json_repr(self) -> Dict[str, Any]:
        data = _serialize_schema_keys(vars(self))
        data["type"] = "integer"
        return data


@dataclass
class Array(JSONSchemaType):
    """Array type.

    See `array type <https://json-schema.org/understanding-json-schema/reference/array>`_

    >>> Array(String()).json_repr()
    {'items': {'type': 'string'}, 'type': 'array'}
    """
    items: JSONSchemaType = None  #: item type for a strict typed array
    prefixItems: Collection[JSONSchemaType] = None  #: a List of fixed object positions for a tuple type
    contains: JSONSchemaType = None  #: must contain this type of object
    additionalItems: bool = None  #: allow additional items
    uniqueItems: bool = None  #: specify an array as a set type
    minItems: int = None
    maxItems: int = None
    title: str = None
    description: str = None
    examples: List = None
    enum: List[List] = None
    default: List = ...

    def json_repr(self) -> Dict[str, Any]:
        data = _serialize_schema_keys(vars(self))
        data["type"] = "array"
        return data


@dataclass
class Object(JSONSchemaType):
    """JSON object type (dictionary-like).

    See `object type <https://json-schema.org/understanding-json-schema/reference/object>`_

    >>> Object({'name': String()}).json_repr()
    {'properties': {'name': {'type': 'string'}}, 'type': 'object'}
    """
    properties: Dict[str, JSONSchemaType] = None
    patternProperties: Dict[str, JSONSchemaType] = None
    additionalProperties: bool = None
    minProperties: int = None
    maxProperties: int = None
    required: List[str] = None
    title: str = None
    description: str = None
    examples: List = None
    enum: List[Dict] = None
    default: Dict = ...

    def json_repr(self) -> Dict[str, Any]:
        data = _serialize_schema_keys(vars(self))
        data["type"] = "object"
        return data


@dataclass
class AnyOf(JSONSchemaType):
    """Any of the included schemas must be valid.

    See `anyOf keyword <https://json-schema.org/understanding-json-schema/reference/combining#anyOf>`_

    >>> AnyOf([String(), Integer()]).json_repr()
    {'anyOf': [{'type': 'string'}, {'type': 'integer'}]}
    """
    items: Collection[JSONSchemaType]

    def json_repr(self) -> Dict[str, Any]:
        return {"anyOf": [item.json_repr() for item in self.items]}


@dataclass
class OneOf(JSONSchemaType):
    """Only one of the included schemas must be valid.

    See `oneOf keyword <https://json-schema.org/understanding-json-schema/reference/combining#oneOf>`_

    >>> OneOf([String(), Integer()]).json_repr()
    {'oneOf': [{'type': 'string'}, {'type': 'integer'}]}
    """
    items: Collection[JSONSchemaType]

    def json_repr(self) -> Dict[str, Any]:
        return {"oneOf": [item.json_repr() for item in self.items]}


@dataclass
class AllOf(JSONSchemaType):
    """All the included schemas must be valid.

    See `allOf keyword <https://json-schema.org/understanding-json-schema/reference/combining#allOf>`_

    >>> AllOf([String(), Integer()]).json_repr()
    {'allOf': [{'type': 'string'}, {'type': 'integer'}]}
    """
    items: Collection[JSONSchemaType]

    def json_repr(self) -> Dict[str, Any]:
        return {"allOf": [item.json_repr() for item in self.items]}


@dataclass
class Not(JSONSchemaType):
    """Revert the condition of the schema.

    See `Not keyword <https://json-schema.org/understanding-json-schema/reference/combining#allOf>`_

    >>> Not(Boolean()).json_repr()
    {'not': {'type': 'boolean'}}
    """
    item: JSONSchemaType

    def json_repr(self) -> Dict[str, Any]:
        return {"not": self.item.json_repr()}


@dataclass
class Nullable(JSONSchemaType):
    """Nullable value alias.

    >>> Nullable(String()).json_repr()
    {'oneOf': [{'type': 'string'}, {'enum': [None]}]}
    """
    item: JSONSchemaType

    def json_repr(self) -> Dict[str, Any]:
        return {"oneOf": [self.item.json_repr(), Null().json_repr()]}
