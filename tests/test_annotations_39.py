import collections.abc as c
import typing as t

import pytest

from jsonschema_gen.parsers import *
from jsonschema_gen.utils import compatible_py39

TYPES_39 = []

if compatible_py39():
    TYPES_39 = [
        (dict, {"type": "object"}),
        (list[str], {"type": "array", "items": {"type": "string"}}),
        (tuple[str], {"type": "array", "prefixItems": [{"type": "string"}]}),
        (tuple[str, int], {"type": "array", "prefixItems": [{"type": "string"}, {"type": "integer"}]}),
        (tuple[str, ...], {"type": "array", "items": {"type": "string"}}),
        (set[int], {"type": "array", "items": {"type": "integer"}, "uniqueItems": True}),
        (c.Collection[str], {"type": "array", "items": {"type": "string"}}),
        (c.Iterable[str], {"type": "array", "items": {"type": "string"}}),
        (c.Mapping[str, ...], {"type": "object"}),
        (c.Mapping[str, int], {"type": "object", "patternProperties": {"^.+$": {"type": "integer"}}}),
        (c.MutableMapping[str, ...], {"type": "object"}),
        (c.MutableMapping[str, int], {"type": "object", "patternProperties": {"^.+$": {"type": "integer"}}}),
        (c.Set[int], {"type": "array", "items": {"type": "integer"}, "uniqueItems": True}),
        (c.MutableSet[int], {"type": "array", "items": {"type": "integer"}, "uniqueItems": True}),
        (t.List, {"type": "array"}),
        (t.Collection, {"type": "array"}),
        (t.Iterable, {"type": "array"}),
        (t.Tuple, {"type": "array"}),
        (t.Dict, {"type": "object"}),
        (t.Set, {"type": "array", "uniqueItems": True}),
        (t.MutableSet, {"type": "array", "uniqueItems": True}),
        (t.FrozenSet, {"type": "array", "uniqueItems": True}),
        (t.Mapping, {"type": "object"}),
        (t.MutableMapping, {"type": "object"}),
    ]


@pytest.mark.parametrize(["annotation", "result"], [*TYPES_39])
def test_types(annotation, result):
    assert Parser(locals=globals()).parse_annotation(annotation).json_repr() == result
