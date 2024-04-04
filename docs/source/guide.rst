.. _guide:

User guide
==========

Using the generator is quite simple. You need to create a parser and pass a class and a method of this class
there to generate an annotation namedtuple with `kwargs` containing the input schema and `returns` containing
the return value schema (:py:meth:`~jsonschema_gen.Parser.parse_function`).

.. code-block:: python

    from typing import NewType, TypedDict
    from jsonschema_gen import Parser

    Username = NewType('Username', str)


    class User(TypedDict):
        name: str
        blocked: bool


    class UserData:

        def get_user(self, name: Username) -> User:
            """Get an API user."""

    parser = Parser()
    annotations = parser.parse_function(UserData.get_user, UserData)

The schema consists of a schema object (see :ref:`schema`) which can be converted to a JSON-compatible dict using
its :py:meth:`~jsonschema_gen.schema.JSONSchemaType.json_repr` method (keep in mind that you should check for `None`
there since for a method with no input args the `kwargs` may be `None`).

.. code-block:: python

    annotations.kwargs.json_repr()

The resulting object for this particular example would look like this.

.. code-block:: python

    {
      "type": "object",
      "title": "Get an API user.",
      "properties": {
        "name": {
          "title": "Username",
          "type": "string"
        }
      },
      "required": [
        "name"
      ],
      "additionalProperties": False
    }

There's also a way to parse all public methods of the class using :py:meth:`~jsonschema_gen.Parser.parse_class`.

.. code-block:: python

    annotations = parser.parse_class(UserData)

The result is a dictionary with name: annotations data.

You can use a JSONSchema validation library, such as `fastjsonschema <https://github.com/horejsek/python-fastjsonschema>`_,
to validate input arguments for your API methods. Something like this:

.. code-block:: python

    from fastjsonschema import compile

    users_validators = {method_name: compile(annotation.kwargs.json_repr())}

    @route('/users/{method}')
    def handle_request(request):
        method = request.match_args['method']
        args = request.json()
        users_validators[method](args)
        return getattr(users, method)(**args)

Private args
------------

You can specify 'private' arguments for your input by prefixing them with underscore. They will be ignored in the
annotation output. However, the parser does no default value check - it's on your own responsibility.

You can use this pattern if you, for example, have a public API where the session is passed automatically by some
middleware. You then can create her as a 'private' input argument.

.. code-block:: python

    def get_user(self, name: Username, _session=None) -> User:
        """Get an API user."""

`_session` will not be present in the resulting schema, so if someone will try to pass it explicitly from the API,
the validator would raise a validation error.

Variable args
-------------

Since the resulting schema must translate to a JSONSchema object, currently the positional variable arguments are
ignored. In this case the two method definitions are equivalent for the parser:

.. code-block:: python

    def get_user(self, name: Username, *args) -> User: ...

    def get_user(self, name: Username) -> User: ...

Variable keyword arguments are accepted and would change `additionalProperties` of the input schema object to `true`.
However, I would not recommend using variable keyword arguments in a public API.

.. code-block:: python

    def get_user(self, name: Username, **kwargs) -> User: ...
    # "additionalProperties" will be 'true'

Strict mode
-----------

By default the parser is initialize in the *strict mode*. It means that it won't be able to parse types what cannot be
mapped to JSON types explicitly.

For example, the python `UUID` type, although the JSONSchema has 'uuid' string format, has no equivalent in JSON, which
means that it may create confusion and errors when the method expecting a `UUID` object will receive an UUID formatted
`string` instead. The same can be said for `datetime`, `date` and other special types.

See :ref:`type-map` for the full list of types supported in the strict mode.

Some JSON parsers like `orjson <https://github.com/ijl/orjson>`_ can in fact convert date-time strings to Python `datetime`
objects. In this case you may either switch to the non-strict mode or modify a particular type parser to
allow it in the strict mode.

.. code-block:: python

    from jsonschema_gen.parsers import DateTimeParser, DateParser

    DateTimeParser.strict = True
    DateParser.strict = True

It depends on the situation whether you want to use the strict or non-strict mode in your code.

Limitations
-----------

Positional-only arguments are not supported at the moment (and I honestly don't know how to support them properly).

.. code-block:: python

    # would raise a `IncompatibleTypesError`
    def get_user(self, name: Username, /) -> User: ...

To resolve string annotations (references) you must pass a dictionary of your globals to the parser's `__init__`.
