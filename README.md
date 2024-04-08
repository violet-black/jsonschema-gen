[![pypi](https://img.shields.io/pypi/v/jsonschema-gen.svg)](https://pypi.python.org/pypi/jsonschema-gen/)
[![docs](https://readthedocs.org/projects/jsonschema-gen/badge/?version=latest&style=flat)](https://jsonschema-gen.readthedocs.io)
[![codecov](https://codecov.io/gh/violet-black/jsonschema-gen/graph/badge.svg?token=FEUUMQELFX)](https://codecov.io/gh/violet-black/jsonschema-gen)
[![tests](https://github.com/violet-black/jsonschema-gen/actions/workflows/tests.yaml/badge.svg)](https://github.com/violet-black/jsonschema-gen/actions/workflows/tests.yaml)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![python](https://img.shields.io/pypi/pyversions/uvlog.svg)](https://pypi.python.org/pypi/jsonschema-gen/)

**jsonschema-gen** is Python type hints parser which can convert function and method annotations
into [JSONSchema](https://json-schema.org) objects.

- Pythonic [classes](https://jsonschema-gen.readthedocs.io/schema.html) for JSONSchema types
- Extensive type coverage: TypedDict, Generic, NewType, etc.
- No external dependencies

# Installation

With pip and python 3.8+:

```bash
pip3 install jsonschema-gen
```

# How to use

See the [user guide](https://jsonschema-gen.readthedocs.io/guide.html) for more info.

Create a parser:

```python
from jsonschema_gen import Parser

parser = Parser(strict=True)
```

Generate schema for your function or method from Python type hints
(see the list of [supported types](https://jsonschema-gen.readthedocs.io/type_map.html)):

```python
from typing import NewType

UserName = NewType('UserName', str)

class UserData:
    def get_user(self, name: UserName, active: bool = True) -> dict:
        """Get user by username."""

annotation = parser.parse_function(UserData.get_user, UserData)
```

The result is an annotation object with input `.kwargs` and output `.returns`. You can get a JSONSchema compatible dict
using `json_repr()` on `.kwargs`:

```python
schema = annotation.kwargs.json_repr()
```

The result would look like this (if converted to JSON with `dumps`):

```json
{
  "type": "object",
  "title": "Get user by username.",
  "properties": {
    "name": {
      "title": "Username",
      "type": "string"
    },
    "active": {
      "type": "boolean",
      "default": true
    }
  },
  "required": [
    "name"
  ],
  "additionalProperties": false
}
```

Use [fastjsonschema](https://github.com/horejsek/python-fastjsonschema) or other JSONSchema validation library to
create a validator for the schema:

```python
from fastjsonschema import compile

validator = compile(schema)
valiator({'name': 'John', 'email': 'john@dowe'})
```

Alternatively you can pass the whole class to the parser to get the annotation mapping:

```python
annotations = parser.parse_class(UserData)
annotations['get_user'].kwargs.json_repr()
```

# Compatibility

The Python type hints are vast and yet not well organized, so there could always be some data type I forgot to add
here. Read the customization guide to extend the standard list of type parsers.

Some annotations cannot be converted to JSONSchema objects, for example: positional-only arguments, variable
positionals, etc. There are [different strategies](https://jsonschema-gen.readthedocs.io/guide.html#variable-args)
considering these types of parameters.

Python 3.8 compatibility is so-so due to lots of features and changes made in 3.9. However, it still should support
most of the functionality.

Also read about the [strict mode](https://jsonschema-gen.readthedocs.io/guide.html#strict-mode).
