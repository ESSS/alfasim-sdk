.. _case-description-example:

Example
=======

In this section, we will walk trough the creation of a simple network, with two nodes and one pipe, to illustrate how to
create a project and how to interpret the definitions available on :ref:`alfacase-reference-section`.

The root level of a ``Description`` is always the class :py:class:`CaseDescription <alfasim_sdk.CaseDescription>`
which has the following attributes:

.. note::

   This guide assumes the reader is familiar with `Python 3 <https://www.python.org/>`__.

.. code-block:: python

    class CaseDescription:
        name: Optional[str] = None
        physics: PhysicsDescription = PhysicsDescription()
        time_options: TimeOptionsDescription = TimeOptionsDescription()
        numerical_options: NumericalOptionsDescription = NumericalOptionsDescription()
        ipr_models: IPRModelsDescription = IPRModelsDescription()
        pvt_models: PvtModelsDescription = PvtModelsDescription()
        tracers: TracersDescription = TracersDescription()
        outputs: CaseOutputDescription = CaseOutputDescription()
        pipes: List[PipeDescription] = []
        nodes: List[NodeDescription] = []
        wells: List[WellDescription] = []
        materials: List[MaterialDescription] = []
        walls: List[WallDescription] = []

In the following section, these steps will be covered:

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

.. code-block:: python

    class CaseDescription:
        physics: PhysicsDescription = PhysicsDescription()
        time_options: TimeOptionsDescription = TimeOptionsDescription()
        numerical_options: NumericalOptionsDescription = NumericalOptionsDescription()


For this example, the application will be configured with the ALFAsim correlation package using a hydrodynamic model
with two-phase and four fields, the time steps will be changed as well and the tolerance will be set to 1e-4

.. rubric:: Example

.. code-block:: python

    from alfasim_sdk import (
        CaseDescription,
        PhysicsDescription,
        NumericalOptionsDescription,
        TimeOptionsDescription,
    )
    from barril.units import Scalar

    CaseDescription(
        name="basic_case",
        physics=PhysicsDescription(
            correlations_package=CorrelationPackageType.Alfasim,
            hydrodynamic_model=HydrodynamicModelType.FourFields,
        ),
        numerical_options=NumericalOptionsDescription(tolerance=1e-4),
        time_options=TimeOptionsDescription(
            minimum_timestep=Scalar(1e-4, "s"),
            maximum_timestep=Scalar(0.5, "s"),
            final_time=Scalar(1.0, "s"),
        ),
    )

PVT Model
---------

The second step will add a PVT model to the project and configure it as the default PVT for the entire project.

The :py:class:`PvtModelsDescription <alfasim_sdk.PvtModelsDescription>` class configures PVT models used in the project.

Each element in the project can have a PVT model assigned, however it is possible to configure a default model that
will be used when an element doesn't have an assigned PVT model.
That default model is the model assigned to the `default_model` attribute.

For this example, a PVT model will be created from a ``.tab`` file. Path definitions inside the ``.alfacase``
file are always relative for portability.
And for this, we need to populate the ``tables`` field with the PVT name and a file.

.. note::

     Each PVT model name must be unique.

    Check the :ref:`alfacase-reference-pvt-section` section for a detailed description of each PVT type option.


.. rubric:: Example


.. code-block:: python

    from alfasim_sdk import (
        CaseDescription,
        PvtModelsDescription,
    )

    CaseDescription(
        # Omitting fields that configure option
        pvt_models=PvtModelsDescription(
            default_model="Pvt1",
            tables={"Pvt1": "my_pvt_file.tab"},
        ),
    )


Nodes
-----

The third step will add two different types of nodes: a mass source node and a pressure node.

Nodes are added over the ``nodes`` section of the :py:class:`CaseDescription <alfasim_sdk.CaseDescription>`.

The :py:class:`NodeDescription <alfasim_sdk.NodeDescription>` class configures several types of nodes
through the ``node_type`` field and their respective property fields.

For example:

* When ``node_type`` is :py:class:`NodeCellType.MassSource <alfasim_sdk._internal.constants.NodeCellType.MassSource>`, ``mass_source_properties`` will be taken in account.
* When ``node_type`` is :py:class:`NodeCellType.Pressure <alfasim_sdk._internal.constants.NodeCellType.Pressure>`, ``pressure_properties`` will be taken in account.

The other properties not related to the ``node_type`` are read by the application, but are not considered for the solution.


.. note::

    Check the :ref:`alfacase-reference-node-section` section for a detailed description of each ``Node`` type.

.. rubric:: Example

.. code-block:: python

    from alfasim_sdk import (
        CaseDescription,
        NodeDescription,
        MassSourceNodePropertiesDescription,
        PressureNodePropertiesDescription,
    )

    CaseDescription(
        # Omitting fields that configure Options and Pvt
        nodes=[
            NodeDescription(
                name="Inlet",
                node_type=NodeCellType.MassSource,
                mass_source_properties=MassSourceNodePropertiesDescription(
                    mass_flow_rates={
                        "gas": Scalar(0.0, "kg/s"),
                        "oil": Scalar(0.0, "kg/s"),
                    },
                ),
            ),
            NodeDescription(
                name="Outlet",
                node_type=NodeCellType.Pressure,
                pressure_properties=PressureNodePropertiesDescription(
                    pressure=Scalar(50.0, "bar"),
                    volume_fractions={
                        "gas": Scalar(1.0, "-"),
                        "oil": Scalar(1.0, "-"),
                    },
                ),
            ),
        ],
    )


Pipes
-----

Let's add a Pipe to the application through the ``pipes`` fields.

The ``pipes`` attribute accepts a list of :py:class:`PipeDescription <alfasim_sdk.PipeDescription>` definitions that connects two nodes.

The connection is defined by the ``source`` and ``target`` fields, and to configure them it is only necessary
to inform the name of the :py:class:`NodeDescription <alfasim_sdk.NodeDescription>` that will be used.

.. note::

    Check the :ref:`alfacase-reference-pipe-section` section for a detailed description of the attributes available.

.. rubric:: Example


.. code-block:: python

    from alfasim_sdk import (
        CaseDescription,
        PipeDescription,
        ProfileDescription,
        LengthAndElevationDescription,
        PipeSegmentsDescription,
    )

    CaseDescription(
        # Omitting fields that configure Options, Pvt and Node
        pipes=[
            PipeDescription(
                name="pipe",
                source="Inlet",
                target="Outlet",
                profile=ProfileDescription(
                    length_and_elevation=LengthAndElevationDescription(
                        length=Array([0.0, 15.0, 30.0, 30.0, 15.0], "m"),
                        elevation=Array([0.0, 15.0, 30.0, 30.0, 15.0], "m"),
                    ),
                ),
                segments=PipeSegmentsDescription(
                    start_positions=Array([0.0], "m"),
                    diameters=Array([0.1], "m"),
                    roughnesses=Array([5e-05], "m"),
                ),
            ),
        ],
    )




Output
------

The final step for our example will configure a trend and a profile for our project.

As indicated on :py:class:`CaseDescription <alfasim_sdk.CaseDescription>`, the ``outputs`` field must be filled with
a :py:class:`CaseOutputDescription <alfasim_sdk.CaseOutputDescription>` instance which configures ``trends``
and ``profiles``.

.. note::

    Check the :ref:`alfacase-reference-output-section` section for a detailed description of each output type, that
    shows all the available curves that can be used.

.. rubric:: Example

.. code-block:: python

    from alfasim_sdk import (
        CaseDescription,
        CaseOutputDescription,
        TrendsOutputDescription,
        PositionalPipeTrendDescription,
        OutputAttachmentLocation,
        ProfileOutputDescription,
    )

    CaseDescription(
        # Omitting fields that configure Options, Pvt, Node and Pipes
        outputs=CaseOutputDescription(
            trends=TrendsOutputDescription(
                positional_pipe_trends=[
                    PositionalPipeTrendDescription(
                        element_name="pipe",
                        curve_names=["oil mass flow rate"],
                        position=Scalar(100.0, "m"),
                        location=OutputAttachmentLocation.Main,
                    )
                ]
            ),
            automatic_trend_frequency=True,
            trend_frequency=Scalar(0.1, "s"),
            profiles=[
                ProfileOutputDescription(
                    curve_names=["pressure"],
                    element_name="pipe",
                    location=OutputAttachmentLocation.Main,
                )
            ],
            automatic_profile_frequency=True,
            profile_frequency=Scalar(0.1, "s"),
        ),
    )


Full Case
---------

This section brings together all the previous sections, showing the full example of a
Description with a project configuration and being converted to a ``.alfacase`` file, using
`convert_description_to_alfacase` making this project ready to be imported by the application.

.. code-block:: python

    from alfasim_sdk import (
        CaseDescription,
        PhysicsDescription,
        NumericalOptionsDescription,
        TimeOptionsDescription,
        PvtModelsDescription,
        NodeDescription,
        MassSourceNodePropertiesDescription,
        PressureNodePropertiesDescription,
        PipeDescription,
        ProfileDescription,
        LengthAndElevationDescription,
        PipeSegmentsDescription,
        CaseOutputDescription,
        TrendsOutputDescription,
        PositionalPipeTrendDescription,
        OutputAttachmentLocation,
        ProfileOutputDescription,
        CaseOutputDescription,
    )

    case_description = CaseDescription(
        name="basic_case",
        physics=PhysicsDescription(
            correlations_package=CorrelationPackageType.Alfasim,
            hydrodynamic_model=HydrodynamicModelType.FourFields,
        ),
        numerical_options=NumericalOptionsDescription(tolerance=1e-4),
        time_options=TimeOptionsDescription(
            minimum_timestep=Scalar(1e-4, "s"),
            maximum_timestep=Scalar(0.5, "s"),
            final_time=Scalar(1.0, "s"),
        ),
        pvt_models=PvtModelsDescription(
            default_model="Pvt1",
            tables={"Pvt1": "my_pvt_file.tab"},
        ),
        nodes=[
            NodeDescription(
                name="Inlet",
                node_type=NodeCellType.MassSource,
                mass_source_properties=MassSourceNodePropertiesDescription(
                    mass_flow_rates={
                        "gas": Scalar(0.0, "kg/s"),
                        "oil": Scalar(0.0, "kg/s"),
                    },
                ),
            ),
            NodeDescription(
                name="Outlet",
                node_type=NodeCellType.Pressure,
                pressure_properties=PressureNodePropertiesDescription(
                    pressure=Scalar(50.0, "bar"),
                    volume_fractions={
                        "gas": Scalar(1.0, "-"),
                        "oil": Scalar(1.0, "-"),
                    },
                ),
            ),
        ],
        pipes=[
            PipeDescription(
                name="pipe",
                source="Inlet",
                target="Outlet",
                profile=ProfileDescription(
                    length_and_elevation=LengthAndElevationDescription(
                        length=Array([0.0, 15.0, 30.0, 30.0, 15.0], "m"),
                        elevation=Array([0.0, 15.0, 30.0, 30.0, 15.0], "m"),
                    ),
                ),
                segments=PipeSegmentsDescription(
                    start_positions=Array([0.0], "m"),
                    diameters=Array([0.1], "m"),
                    roughnesses=Array([5e-05], "m"),
                ),
            ),
        ],
        outputs=CaseOutputDescription(
            trends=TrendsOutputDescription(
                positional_pipe_trends=[
                    PositionalPipeTrendDescription(
                        element_name="pipe",
                        curve_names=["oil mass flow rate"],
                        position=Scalar(100.0, "m"),
                        location=OutputAttachmentLocation.Main,
                    )
                ]
            ),
            automatic_trend_frequency=True,
            trend_frequency=Scalar(0.1, "s"),
            profiles=[
                ProfileOutputDescription(
                    curve_names=["pressure"],
                    element_name="pipe",
                    location=OutputAttachmentLocation.Main,
                )
            ],
            automatic_profile_frequency=True,
            profile_frequency=Scalar(0.1, "s"),
        ),
    )

And the ``case_description`` above can be converted to a ``.alfacase`` file using ``convert_description_to_alfacase``.

.. code-block:: python

    from pathlib import Path
    from alfasim_sdk import convert_description_to_alfacase

    case_description = CaseDescription(  [...] )
    alfacase_content = convert_description_to_alfacase(case_description)

    # Dump the content to a file
    alfacase_file = Path("c:\\user\\") / 'my_project.alfacase'
    alfacase_file.write_text(data=alfacase_content, encoding='UTF-8')
