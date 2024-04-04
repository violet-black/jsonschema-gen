.. _type-map:

Type reference
==============

These tables contain the full list of supported type hints and their normalized JSONSchema types.
The `strict` attribute means that the conversion is available only in the parser's *strict* mode.

The mapping between the standard Python types and JSONSchema types.

.. csv-table::
   :header: "Annotation", "JSONSchema", "strict", "comment"
   :align: left

   "bool",                   "boolean",       "YES",        ""
   "str",                    "string",        "YES",        ""
   "bytes",                  "string",        "YES",        ""
   "date",                   "string",        "no",         "format=date"
   "datetime",               "string",        "no",         "format=date-time"
   "UUID",                   "string",        "no",         "format=uuid"
   "SafeUUID",               "string",        "no",         "format=uuid"
   "float",                  "number",        "YES",         ""
   "int",                    "integer",       "YES",         ""
   "Decimal",                "number",        "YES",         ""
   "Number",                 "number",        "YES",         ""
   "None",                   "null",          "YES",         ""
   "Any",                    "unspecified",   "YES",         ""
   "list",                   "array",         "YES",         ""
   "tuple",                  "array",         "YES",         "with prefixItems"
   "NamedTuple",             "array",         "no",          "with prefixItems=true"
   "set",                    "array",         "YES",         "with uniqueItems=true"
   "frozenset",              "array",         "YES",         "with uniqueItems=true"
   "dict",                   "object",        "YES",         ""
   "TypedDict",              "object",        "YES",         "additionalProperties=false"
   "dataclass",              "object",        "no",          "additionalProperties=false"
   "Enum",                   "enum",          "no",          "non-strict because in Python enum type != its value"
   "*args",                  "",              "YES",         "ignored"
   "**kwargs",               "",              "YES",         "sets additionalProperties=true"

The mapping between Python base and abstract types and JSONSchema types.

.. csv-table::
   :header: "Annotation", "JSONSchema", "strict", "comment"
   :align: left

   "typing.List",                       "array",        "YES",        ""
   "typing.Collection",                 "array",        "YES",        ""
   "collections.abc.Collection",        "array",        "YES",        ""
   "typing.Iterable",                   "array",        "YES",        ""
   "collections.abc.Iterable",          "array",        "YES",        ""
   "typing.Tuple",                      "array",        "YES",        "with prefixItems=true"
   "typing.Set",                        "array",         "YES",         "with uniqueItems=true"
   "collections.abc.Set",               "array",         "YES",         "with uniqueItems=true"
   "typing.MutableSet",                  "array",         "YES",         "with uniqueItems=true"
   "collections.abc.MutableSet",        "array",         "YES",         "with uniqueItems=true"
   "typing.FrozenSet",                  "array",         "YES",         "with uniqueItems=true"
   "typing.Dict",                       "object",        "YES",        ""
   "collections.abc.Collection",        "object",        "YES",        ""
   "typing.Mapping",                       "object",        "YES",        ""
   "collections.abc.Mapping",               "object",        "YES",        ""
   "typing.MutableMapping",                 "object",        "YES",        ""
   "collections.abc.MutableMapping",        "object",        "YES",        ""

The mapping between Python special type hint types and JSONSchema types.

.. csv-table::
   :header: "Annotation", "JSONSchema", "strict", "comment"
   :align: left

   "typing.Literal",       "enum",        "YES",        "constant value or values"
   "typing.Union",         "anyOf",       "YES",        ""
   "union operator |",     "anyOf",       "YES",        ""
   "typing.Optional",      "anyOf",       "YES",        "value or null"
   "typing.TypeVar",       "",            "YES",        "converts to the bound type"
   "typing.NewType",       "",            "YES",        "converts to the bound type"
   "typing.Generic",       "",            "YES",        "resolves type vars to the bound type"
   "typing.TypeVar",       "",            "YES",        "converts to a bound type"
   "typing.Required",      "",            "YES",        "required key added to the 'required' array"
   "typing.NotRequired",   "",            "YES",        "not required key removed from the 'required' array"
