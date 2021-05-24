.. _alfacase-example:

Example
=======

In this section, we will walk trough the creation of a simple network, with two nodes and one pipe, to illustrate how to
crete a project and how to interpret the definitions available on :ref:`alfacase-reference-section`.

The root level of our :program:`ALFAcase` file is always a :py:class:`CaseDescription <alfasim_sdk.CaseDescription>`
which has the following attributes:

.. code-block:: yaml

    name: string    # optional
    physics: physics_description_schema⠀
    time_options: time_options_description_schema⠀
    numerical_options: numerical_options_description_schema⠀
    ipr_models: ipr_models_description_schema⠀
    pvt_models: pvt_models_description_schema⠀
    tracers: tracers_description_schema⠀
    outputs: case_output_description_schema⠀

    ....

In the following section, this steps will be covered:

- How to configure the project options.
- How to add a PVtModel.
- How to add Nodes.
- How to add Pipes.
- How to add output curves.


.. note::

    For the full reference check the :ref:`alfacase-reference-section`


Project Options
---------------

We will start the example by configuring the project options, as discussed in the previous section,
the root level of an ``ALFacase`` file is the :py:class:`CaseDescription <alfasim_sdk.CaseDescription>` and it has the following options:

- ``physics``
- ``time_options``
- ``numerical_options``



For this example, the application will be configured with the ALFAsim correlation package using a hydrodynamic model
with two-phase and four fields, the time steps will be changed as well and the tolerance will be set to 1e-4

.. note::

    As indicated in :ref:`alfacase-syntax` section, each option has its own schema definition that needs to be
    filled accordingly to the reference showed at :ref:`alfacase-reference-options-section` section.

.. rubric:: Example

.. code-block:: yaml

    name: basic_case

    physics:
      correlations_package: correlation_package_alfasim
      hydrodynamic_model: hydrodynamic_model_4_fields

    numerical_options:
      tolerance: 1e-4

    time_options:
      minimum_timestep:
        value: 1e-4
        unit: s
      maximum_timestep:
        value: 0.5
        unit: s
      final_time:
        value: 1.0
        unit: s

PVT Model
---------

The second step will add a ``PVTModel`` to the project and configure it as the default PVT for the entire project.

The ``pvt_models`` field from :py:class:`CaseDescription <alfasim_sdk.CaseDescription>` needs to be configured with the
definition provided from :py:class:`PvtModelsDescription <alfasim_sdk.PvtModelsDescription>`.

The :py:class:`PvtModelsDescription <alfasim_sdk.PvtModelsDescription>` is the root configuration of all PVTs over the application,
its possible to add new PVTs and defined one of them to be used automatically on all fields that requires a
PVT through the option `default_model`

For this example a PVT will be created from a ``.tab`` file and the path to the file is relative to the ``.alfacase`` file.
And for this we need to populate the ``tables`` field with the PVT name and a file.


.. admonition:: About the tab file path

    Considering that a ``.alfacase`` file is located at ``C:\Users\alfasim`` and the ``table`` section is configured with
    a relative path to ``my_pvt_file.tab``.

    In this case, the application will look for the ``.tab`` file at  ``C:\Users\alfasim\my_pvt_file.tab``

    .. code-block:: yaml

        tables:
           # PVT name  : file path
          'Pvt1': my_pvt_file.tab


.. note::

    The PVT name must be unique.

    Check the :ref:`alfacase-reference-pvt-section` section for a detailed description of each PVT type option.


.. rubric:: Example

.. code-block:: yaml

    [ ... ]

    pvt_models:
      default_model: 'Pvt1'
      tables:
        'Pvt1': my_pvt_file.tab

    [ ... ]


Nodes
-----

The third step will add two different types of nodes, a mass source node and a pressure node.

All nodes that will be used on the application need to be added over the ``nodes`` section of the
:class:`CaseDescription <alfasim_sdk.CaseDescription>`.

The :class:`NodeDescription <alfasim_sdk.NodeDescription>` is responsible to configure several types of nodes
through the ``node_type`` field and their respective property fields.

For example, when the ``node_type`` is  ``mass_source_boundary``, besides the fields from :py:class:`NodeDescription <alfasim_sdk.NodeDescription>`
only the fields available at ``mass_source_properties`` will be considered.

And when ``node_type`` is ``pressure_boundary`` only the fields from  ``pressure_properties`` will be considered.


.. note::

    Check the :ref:`alfacase-reference-node-section` section for a detailed description of each ``Node`` type.

.. rubric:: Example

.. code-block:: yaml

    nodes:
    - name: Inlet
      node_type: mass_source_boundary
      mass_source_properties:
        mass_flow_rates:
          gas:
            value: 0.0
            unit: kg/s
          oil:
            value: 0.0
            unit: kg/s
    - name: Outlet
      node_type: pressure_boundary
      pressure_properties:
        volume_fractions:
          gas:
            value: 1.0
            unit: '-'
          oil:
            value: 0.0
            unit: '-'
        pressure:
          value: 50.0
          unit: bar


.. note::

    The ``nodes`` field accepts a list of definitions, and each definition must begin with a dash (``-``).

    So whenever dash (``-``) character appears, ``ALFAcase`` will consider that a new definition is being created.

    .. rubric:: Example

    .. code-block:: yaml

        nodes:

        # First Node.
        -   name: Node 1
            node_type: mass_source_boundary

        # Second Node, because it has a dash character.
        -   node_type: pressure_boundary
            name: Node 2


Pipes
-----

The fourth step will add a Pipe to the application through the ``pipes`` fields.

The ``pipes`` accepts a list of :py:class:`PipeDescription <alfasim_sdk.PipeDescription>` definitions which connects two nodes.

The connection occurs with the fields ``source`` and ``target`` and to configure these fields, it is only necessary
to inform the name of the :py:class:`NodeDescription <alfasim_sdk.NodeDescription>` that will be used.

.. note::

    Check the :ref:`alfacase-reference-pipe-section` section for a detailed description of the attributes available.

.. rubric:: Example

.. code-block:: yaml

    pipes:
    - name: pipe
      source: Inlet
      target: Outlet
      profile:
        length_and_elevation:
          length:
            values: [ 0.0, 15.0, 30.0, 30.0, 15.0 ]
            unit: m
          elevation:
            values: [ 0.0, 15.0, 30.0, 30.0, 15.0 ]
            unit: m
      segments:
        start_positions:
          values: [ 0.0 ]
          unit: m
        diameters:
          values: [ 0.1 ]
          unit: m
        roughnesses:
          values: [ 5e-05 ]
          unit: m


Output
------

The final step for our example will add a trend and a profile for our project.

As indicate on :py:class:`CaseDescription <alfasim_sdk.CaseDescription>`, the ``outputs`` field must be filled with
the definition of :py:class:`CaseOutputDescription <alfasim_sdk.CaseOutputDescription>` which allows the configuration of ``trends``
and ``profiles``.

.. note::

    Check the :ref:`alfacase-reference-output-section` section for a detailed description about each output type, that
    shows all the available curves that can be used.

.. rubric:: Example

.. code-block:: yaml

    outputs:
      trends:
        - element_name: pipe
          location: main
          position:
            value: 100.0
            unit: m
          curve_names:
            - oil mass flow rate

      trend_frequency:
        value: 0.1
        unit: s

      profiles:
        - element_name: pipe
          location: main
          curve_names:
            - pressure

      profile_frequency:
        value: 0.1
        unit: s

Full Case
---------

This section brings together all the previous sections, showing the full example that can be now used
and imported by the application.

.. code-block:: yaml

    name: basic_case

    physics:
      correlations_package: correlation_package_alfasim
      hydrodynamic_model: hydrodynamic_model_4_fields

    numerical_options:
      tolerance: 1e-4

    time_options:
      minimum_timestep:
        value: 0.0001
        unit: s

      maximum_timestep:
        value: 0.5
        unit: s

      final_time:
        value: 1.0
        unit: s

    pvt_models:
      default_model: 'Pvt1'
      tables:
        'Pvt1': my_pvt_file.tab

    outputs:
      trends:
        - element_name: pipe
          location: main
          position:
            value: 100.0
            unit: m
          curve_names:
            - oil mass flow rate

      trend_frequency:
        value: 0.1
        unit: s

      profiles:
        - element_name: pipe
          location: main
          curve_names:
            - pressure

      profile_frequency:
        value: 0.1
        unit: s

    pipes:
    - name: pipe
      source: Inlet
      target: Outlet
      profile:
        length_and_elevation:
          length:
            values: [ 0.0, 15.0, 30.0, 30.0, 15.0 ]
            unit: m
          elevation:
            values: [ 0.0, 15.0, 30.0, 30.0, 15.0 ]
            unit: m
      segments:
        start_positions:
          values: [ 0.0 ]
          unit: m
        diameters:
          values: [ 0.1 ]
          unit: m
        roughnesses:
          values: [ 5e-05 ]
          unit: m

    nodes:
    - name: Inlet
      node_type: mass_source_boundary
      mass_source_properties:
        mass_flow_rates:
          gas:
            value: 0.0
            unit: kg/s
          oil:
            value: 0.0
            unit: kg/s

    - name: Outlet
      node_type: pressure_boundary
      pressure_properties:
        volume_fractions:
          gas:
            value: 1.0
            unit: '-'
          oil:
            value: 0.0
            unit: '-'
        pressure:
          value: 50.0
          unit: bar
