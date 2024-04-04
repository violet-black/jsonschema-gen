import typing as t

import pytest

from jsonschema_gen.parsers import *
from jsonschema_gen.utils import compatible_py311

TYPES_311 = []


if compatible_py311():

    class _SchemaNotRequired(t.TypedDict):
        """Schema not required"""

        id: str
        value: t.NotRequired[int]

    class _SchemaRequired(t.TypedDict, total=False):
        """Schema required"""

        id: t.Required[str]
        value: int

    TYPES_311 = [
        (t.Dict[str, ...], {"type": "object"}),
        (t.Mapping[str, ...], {"type": "object"}),
        (t.MutableMapping[str, ...], {"type": "object"}),
        (
            _SchemaNotRequired,
            {
                "title": "_SchemaNotRequired",
                "description": "Schema not required",
                "type": "object",
                "properties": {"id": {"type": "string"}, "value": {"type": "integer"}},
                "additionalProperties": False,
                "required": ["id"],
            },
        ),
        (
            _SchemaRequired,
            {
                "title": "_SchemaRequired",
                "description": "Schema required",
                "type": "object",
                "properties": {"id": {"type": "string"}, "value": {"type": "integer"}},
                "additionalProperties": False,
                "required": ["id"],
            },
        ),
    ]


@pytest.mark.parametrize(
    ["annotation", "result"],
    [
        *TYPES_311,
    ],
)
def test_types(annotation, result):
    assert Parser(locals=globals()).parse_annotation(annotation).json_repr() == result
