"""
This is not supposed to be a real package.
It is the namespace of user plugins and is manipulated by the user plugins infrastructure.

The documentation explicitly states that the `namespace packages`_' __path__ is read-only and
automatically updated if the `sys.path` changes (also `PEP-420`_), initial tests show that it
is not read-only and was not magically updated, but better to write code to the spec when possible.

Using this to avoid polluting the global `sys.path` with random user plugin stuff.

.. `namespace packages`_: https://docs.python.org/3.10/reference/import.html#namespace-packages
.. `PEP-420`_: https://peps.python.org/pep-0420/
"""
