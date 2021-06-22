.. _alfacase-syntax:

Syntax
======


An :program:`ALFAcase` file is a text-based file that must be written following the YAML syntax, only a restricted subset of the YAML specification
is supported and the this section and the next cover the differences.

Our root object is a map (equivalent to a dictionary) that represents a :py:class:`CaseDescription <alfasim_sdk.CaseDescription>`
with its attributes.

The majority of the values from :program:`ALFAcase` are based on ``key`` and ``value``, the example below illustrates some of these cases:

.. code-block:: yaml
   :caption: key and value syntax

    key: value

    # Case 1
    material_name: string

    # Case 2
    string: string

    # Case 3
    mass_fractions:
    string:
      value: number
      unit: string

    # Case 4
    position:
    values: [ number ]
    unit: string

    # Case 5
    node_type: NodeCellType⠀

    # Case 6
    physics: physics_description_schema⠀


Case 1:
    ``material_name`` is a pre-defined key and you can just inform the value (``string``).

    .. rubric:: Example

    .. code-block:: yaml

        material_name: Steel

    Check the :ref:`string-alfacase-schema` section for more information on the possible ways to enter a string

Case 2:
    Both key and value must be informed (note the ``string`` indication)

    .. rubric:: Example

    .. code-block:: yaml

        PVTModelName: some_name

    Check the :ref:`string-alfacase-schema` section for more information on the possible ways to enter a string

Case 3:
    The key ``mass_fractions`` is creating a mapping with the ``string`` informed as key, and for each entry, two keys are required
    ``value`` and ``unit``.

    .. rubric:: Example

    .. code-block:: yaml

        mass_fractions:
          first entry:
            value: 42
            unit: m
          second entry:
            value: 1.5
            unit: m

    .. admonition:: Info

        All entries that accept a ``string`` as a key can have multiples entries, as demonstrated above.

    .. admonition:: About the unit

        The unit depends on the category of the attribute, the :ref:`alfacase-reference-section` lists the category and the valid units for each attribute.

    Check the :ref:`number-alfacase-schema` section for more information on the possible ways to enter a ``number``

Case 4:
    Similar to ``Case 3``, but instead  of a single value it accepts multiples values

    .. rubric:: Example

    .. code-block:: yaml

        position:
          values: [ 1.5, 4.5 ]
          unit: m

    Check the section :ref:`list-alfacase-schema` for more information about how to creates a ``list``

Case 5:
    In this case, the value is an ``Enum`` and one of the options must be filled, each attribute listed on :ref:`alfacase-reference-section`
    has a link for the respective ``Enum`` to check all options, on the example, bellow is used a :py:class:`NodeCellType <alfasim_sdk._internal.constants.NodeCellType>`
    that has the following options

    .. autoclass:: alfasim_sdk.NodeCellType
       :noindex:

    .. rubric:: Example

    .. code-block:: yaml

        node_type: mass_source_boundary⠀


Case 6:
    The last case is a composition of components, the definition is informing that the value of physics must be
    filled with the key and values defined for :py:class:`PhysicsDescription <alfasim_sdk.PhysicsDescription>`


    .. rubric:: Example

    .. code-block:: yaml

        physics:
          hydrodynamic_model: hydrodynamic_model_4_fields
          simulation_regime: simulation_regime_transient


All the definitions offer default values, this allows us to abbreviate the syntax and let |sdk| just use its defaults.
Check the :ref:`alfacase-reference-section` section which informs all the default values of each attribute on each ``Description``.


The next sections go deep on the syntax, showing different ways to fill some values.

.. _string-alfacase-schema:

String
------

.. code-block:: yaml
   :caption: string syntax

    # key: value
    material_name: Another value goes here.

    # It is possible to put quotes in a string, but it is not necessary
    material_name: 'A string, enclosed in quotes.'

    # variable: variable
    key with spaces: value


.. _number-alfacase-schema:

Number
-------

.. code-block:: yaml
   :caption: number syntax

    # Integer
    value: 100

    # Float
    value: 1.5

    # Scientific Notation
    value: 1e+12



.. _list-alfacase-schema:

List
----

``list`` is a sequence of values and on :program:`ALFAcase` list is denoted by a series of dashes (``-``)
It is possible to define a list in a compressed inserting the value between brackets (``[`` ``]``):


.. code-block:: yaml
   :caption: list syntax

    values:
      - 1
      - 2
      - 3

    # Flow style
    values: [ 1, 2 , 3 ]


.. _bool-alfacase-schema:

Bool
----

``bool`` is case-insensitive and accepts the following options:

    .. code-block:: yaml
        :caption: boolean syntax

        enable_solver_caching: True     # True
        enable_solver_caching: true     # True
        enable_solver_caching: yes      # True
        enable_solver_caching: on       # True
        enable_solver_caching: 1        # True
        enable_solver_caching: False    # False
        enable_solver_caching: false    # False
        enable_solver_caching: no       # False
        enable_solver_caching: off      # False
        enable_solver_caching: 0        # False
