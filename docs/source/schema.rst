.. _schema:

:tocdepth: 2

JSONSchema types
================

This module contains Python classes for `JSONSchema types <https://json-schema.org/understanding-json-schema/reference/type>`_
which can be helpful when manipulating such data in Python. Each class has a number of attributes and
`json_repr()` method which returns a JSONSchema compatible dictionary.

.. code-block:: python

    import json
    import jsonschema_gen.schema as js

    user = js.Object({
        'name': js.String(title='full name', minLength=1),
        'email': js.String(pattern='/^[^\.\s][\w\-]+(\.[\w\-]+)*@([\w-]+\.)+[\w-]{2,}$/gm')
    }, required=['name', 'email'], additionalProperties=False)

    user_or_guest = js.Nullable(user)

    user_or_guest.json_repr()  # dumps the resulting schema into the python dict
    json.dumps(user_or_guest.json_repr())  # dumps the schema to the JSON string

To create your own type you need to implement :py:class:`~jsonschema_gen.schema.JSONSchemaType` interface, i.e.
the `json_repr()` method itself (subclassing is not required).

.. note::

    To make it easier to use with the original JSONSchema documentation the type attribute names have been left in
    camel-case.

.. autoclass:: jsonschema_gen.schema.JSONSchemaType
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.schema.JSONSchemaObject
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.schema.AllOf
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.schema.AnyOf
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.schema.Array
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.schema.Boolean
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.schema.Const
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.schema.Date
   :members:
   :inherited-members:
   :undoc-members:
   :exclude-members: __init__, format, __post_init__

.. autoclass:: jsonschema_gen.schema.DateTime
   :members:
   :inherited-members:
   :undoc-members:
   :exclude-members: __init__, format, __post_init__

.. autoclass:: jsonschema_gen.schema.Email
   :members:
   :inherited-members:
   :undoc-members:
   :exclude-members: __init__, format, __post_init__

.. autoclass:: jsonschema_gen.schema.Enum
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.schema.GUID
   :members:
   :inherited-members:
   :undoc-members:
   :exclude-members: __init__, format, __post_init__

.. autoclass:: jsonschema_gen.schema.Integer
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.schema.Not
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.schema.Null
   :members:
   :inherited-members:
   :undoc-members:
   :exclude-members: __init__, enum, __post_init__

.. autoclass:: jsonschema_gen.schema.Nullable
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.schema.Number
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.schema.Object
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.schema.OneOf
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.schema.String
   :members:
   :undoc-members:
   :exclude-members: __init__
