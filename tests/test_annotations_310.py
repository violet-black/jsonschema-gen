import pytest

from jsonschema_gen.parsers import *
from jsonschema_gen.utils import compatible_py311

TYPES_310 = []


if compatible_py311():
    TYPES_310 = [
        (int | str, {"anyOf": [{"type": "integer"}, {"type": "string"}]}),
    ]


@pytest.mark.parametrize(["annotation", "result"], [*TYPES_310])
def test_types(annotation, result):
    assert Parser(locals=globals()).parse_annotation(annotation).json_repr() == result
