.. _customization:

Customization
=============

Use :py:class:`~jsonschema_gen.Parser.TypeParser` as you base class to create custom type classes.

Let's try to create a custom type parser for a special user-defined `Email` type.

.. code-block:: python

    from typing import NewType

    Email = NewType('Email', str)

    def set_user_email(user_id: str, email: Email) -> bool: ...

We have to create a special `EmailParser` for this type. However the `NewType` is not a real type and cannot be used
in type checks. We have to customize `can_parse` method then to tell the parser when to parse an annotation.

.. code-block:: python

    from typing import NewType

    from jsonschema_gen.parsers import TypeParser, TYPES
    from jsonschema_gen.schema import Email

    class EmailParser(TypeParser):
        # JSONSchema type to map to
        annotation = Email

        # you may pass a dictionary of default attributes for the JSONSchema object here
        attrs = {'title': 'user email'}

        # allow this type in the Parser strict mode
        strict = True

        def can_parse(self, annotation, /) -> bool:
            return type(annotation) is NewType and annotation.__name__ == 'Email'

Then you need to add it to the list of standard types. Note that the resolution order of types is from 0 to the last
element, so you must insert your parser at the beginning for it to take effect.

.. code-block:: python

    TYPES.insert(0, EmailParser)

Now you can parse the email type and create a JSONSchema annotation with it.

.. code-block:: python

    annotation = parser.parse_function(set_user_email)

The annotation `kwargs` would look like this in this case.

.. code-block:: python

    {
        'properties': {
            'user_id': {'type': 'string'},
            'email': {'format': 'email', 'type': 'string', 'title': 'user email'}
        },
        'additionalProperties': False,
        'required': ['user_id', 'email'],
        'type': 'object'
    }
