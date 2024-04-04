.. _parser:

:tocdepth: 2

Parsers
=======

This module contains the main parser class as well as a list of type annotation parsers. To add your custom parser to
the default list of parsers you must add it to the :py:obj:`jsonschema_gen.parsers.TYPES` list.

.. autodata:: jsonschema_gen.parsers.TYPES
   :annotation: : List[TypeParser] - default list of type parsers

.. autoclass:: jsonschema_gen.parsers.FunctionAnnotation
   :members:
   :undoc-members:
   :exclude-members: __init__, __new__

.. autoclass:: jsonschema_gen.parsers.Parser
   :members:
   :undoc-members:
   :exclude-members:

Base type parser class.

.. autoclass:: jsonschema_gen.parsers.TypeParser
   :members:
   :undoc-members:
   :exclude-members: __init__

Type-specific parsers.

.. autoclass:: jsonschema_gen.parsers.AnyParser
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.parsers.BooleanParser
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.parsers.ConstantParser
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.parsers.DictParser
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.parsers.EnumTypeParser
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.parsers.EnumValueParser
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.parsers.IntegerParser
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.parsers.ListParser
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.parsers.NamedTupleParser
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.parsers.NewTypeParser
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.parsers.NullParser
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.parsers.NumberParser
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.parsers.SetParser
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.parsers.StringParser
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.parsers.TupleParser
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.parsers.TypedDictParser
   :members:
   :undoc-members:
   :exclude-members: __init__

.. autoclass:: jsonschema_gen.parsers.UnionParser
   :members:
   :undoc-members:
   :exclude-members: __init__
