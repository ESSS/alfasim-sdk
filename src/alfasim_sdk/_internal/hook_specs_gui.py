from pluggy import HookspecMarker

from alfasim_sdk._internal.context import Context

hookspec = HookspecMarker("ALFAsim")


@hookspec
def alfasim_get_data_model_type():
    """
    This hook allows the creation of models in ALFAsim, models can:

    - Customize items on ALFAsim application, by adding new components over the Tree.
    - Hold input data information to be accessed from the solver.
    - Validate input data or configuration made on ALFAsim, to ensure that the plugin has all configuration necessary to be run successfully.

    This hook needs to return a class decorated with one of the following options:

    - :func:`~alfasim_sdk.container_model`
    - :func:`~alfasim_sdk.data_model`

    The image below shows the locations where a custom model can be inserted implementing the hook.

    .. image:: /_static/images/hooks/tree_plugin_marker.png
        :scale: 80%

    .. image:: /_static/images/hooks/model_explorer_with_marker.png
        :scale: 80%

    .. |m_1| image:: /_static/images/marker_1.png
        :scale: 80%

    .. |m_2| image:: /_static/images/marker_2.png
        :scale: 80%

    |m_1| Location to where the models :func:`~alfasim_sdk.container_model` or :func:`~alfasim_sdk.data_model` will be placed. |br|
    |m_2| Location to where the :ref:`inputs fields <api-types-section>` will be placed.

    Example 1: The following example shows how to create a new model.

    .. code-block:: python

        import alfasim_sdk
        from alfasim_sdk import data_model
        from alfasim_sdk import Quantity

        @data_model(icon="", caption="My Plugin")
        class MyModel:
            distance = Quantity(value=1, unit="m", caption="Distance")

        @alfasim_sdk.hookimpl
        def alfasim_get_data_model_type():
            return [MyModel]

    The image below shows the output of example 1 when executing on ALFAsim.

    .. image:: /_static/images/hooks/alfasim_get_data_model_type_example_1.png
        :scale: 80%


    Example 2: This second example shows how to create a new container model.

    Notice that when using the :func:`~alfasim_sdk.container_model` you only need to inform the container class
    to the :func:`~alfasim_get_data_model_type` hook

    .. code-block:: python

        import alfasim_sdk
        from alfasim_sdk import data_model, container_model
        from alfasim_sdk import Quantity, String

        @data_model(icon="", caption="My Child")
        class ChildModel:
            distance = Quantity(value=1, unit="m", caption="Distance")


        @container_model(icon='', caption='My Container', model=ChildModel)
        class MyModelContainer:
            my_string = String(value='Initial Value', caption='My String')


        @alfasim_sdk.hookimpl
        def alfasim_get_data_model_type():
            return [MyModelContainer]

    The image below shows the output of example 2 when executing on ALFAsim.

    .. image:: /_static/images/hooks/alfasim_get_data_model_type_example_2.png
        :scale: 80%

    Example 3: This third example demonstrates that it's possible to create multiple models within the plugin

    .. code-block:: python

        import alfasim_sdk
        from alfasim_sdk import data_model, container_model
        from alfasim_sdk import Quantity, String

        @data_model(icon="", caption="My Model")
        class MyModel:
            distance = Quantity(value=1, unit="m", caption="Distance")

        @data_model(icon="", caption="My Child")
        class ChildModel:
            distance = Quantity(value=1, unit="m", caption="Distance")

        @container_model(icon='', caption='My Container', model=ChildModel)
        class MyModelContainer:
            my_string = String(value='Initial Value', caption='My String')


        @alfasim_sdk.hookimpl
        def alfasim_get_data_model_type():
            return [MyModelContainer, MyModel]

    The image below shows the output of example 3 when executing on |alfasim|.

    .. image:: /_static/images/hooks/alfasim_get_data_model_type_example_3.png
        :scale: 80%
    """


@hookspec
def alfasim_get_additional_variables():
    """
    Allows plugins to register new additional variables on ALFAsim.

    It can be used to store the internal variable from the plugin (on solver), or it can be used to expose as an
    output to the user in the plot window (on application). To calculate and update the registered variables the Solver
    `hooks` described on :ref:`update_secondary_variables` section must be implemented.

    This method expects to return a list of :class:`~alfasim_sdk.SecondaryVariable`, for more details checkout
    the reference section with all details about :ref:`variables <api-variables-section>`

    Usage example:

    .. code-block:: python

        from alfasim_sdk import SecondaryVariable
        from alfasim_sdk import Visibility
        from alfasim_sdk import Location
        from alfasim_sdk import Scope

        @alfasim_sdk.hookimpl
        def alfasim_get_additional_variables():
            return [
                SecondaryVariable(
                    name='dummy_variable',
                    caption='Plugin 1',
                    unit='m',
                    visibility=Visibility.Internal,
                    location=Location.Center,
                    multifield_scope=Scope.Global,
                    checked_on_gui_default=True,
                )]
    """


@hookspec
def alfasim_get_status(
    ctx: Context,
):
    """
    Allows plugins to execute custom checks on ALFAsim.
    These checks can be used to guarantee the consistency of the data or compatibility with some configuration made on |alfasim|.

    The status monitor accepts two types of message:

    :class:`~alfasim_sdk.ErrorMessage`:
        Signalize the application to block the simulation until the error is fixed.

    :class:`~alfasim_sdk.WarningMessage`:
        Signalize the application that the user needs to fix this problem, but does not need to block the simulation.

    When no errors are detected, an empty list must be returned.

    The :func:`alfasim_get_status` will be called for:

     - Each time a model from the plugin is modified.
     - Each time a ``Physics options`` from |alfasim| are modified. |br|
       Ex.: Hydrodynamic model changed

    The ``ctx`` parameter is provided to retrieve information about the current state of the application and the current value
    of the models implemented by the user.

    Check out the full documentation of :class:`~alfasim_sdk._internal.context.Context` for more details.

    The following example shows how to display an ErrorMessage when a :class:`~alfasim_sdk.Quantity` field does not have the desired value.

    .. code-block:: python

        import alfasim_sdk
        from alfasim_sdk import data_model
        from alfasim_sdk import Quantity
        from alfasim_sdk import ErrorMessage

        # Define MyModel used in this plugin
        @data_model(icon="", caption="My Plugin Model")
        class MyModel:
            distance = Quantity(
                value=1, unit="m", caption="Distance"
            )


        @alfasim_sdk.hookimpl
        def alfasim_get_data_model_type():
            return [MyModel]


        # Add status monitor in the plugin
        @alfasim_sdk.hookimpl
        def alfasim_get_status(ctx):
            results = []
            distance = ctx.GetModel("MyModel").distance.value
            if distance < 0:
                message = f"Distance must be greater than 0, got {distance}"

                results.append(
                    ErrorMessage(
                        model_name="MyModel",
                        message=message,
                    )
                )
            return results


    For the status monitor above, the application will show the following message when the distance is less than 0:

    .. image:: /_static/images/hooks/status_monitor_with_distance_error.png

    """


@hookspec
def alfasim_configure_fields(ctx: Context):
    """
    Allows plugins to configure new fields to be added in |alfasim|'s hydrodynamic model.

    An added ``field`` must be associated with:

     - Phase, defined by :class:`~alfasim_sdk.AddPhase` or :class:`~alfasim_sdk.UpdatePhase`.
     - Layer, defined by :class:`~alfasim_sdk.AddLayer` or :class:`~alfasim_sdk.UpdateLayer`.

    The ``ctx`` parameter is provided to retrieve information about the current state of the application and the current value
    of the models implemented by the user.

    Check out the full documentation of :class:`~alfasim_sdk._internal.context.Context` for more details.

    Example of usage:

    .. code-block:: python

        @alfasim_sdk.hookimpl
        def alfasim_configure_fields(ctx):
           return [
               AddField(name='plugin_continuous_field'),
               AddField(name='plugin_dispersed_field'),
           ]


    """


@hookspec
def alfasim_configure_layers(ctx: Context):
    """
    Allows plugins to configure new layers or associate a new field with a existing layer for |alfasim|'s hydrodynamic model

    In order to configure a new layer, it is necessary to return an :class:`~alfasim_sdk.AddLayer` object defining the
    required fields.

    The ``ctx`` parameter is provided to retrieve information about the current state of the application and the current value
    of the models implemented by the user.

    Check out the full documentation of :class:`~alfasim_sdk._internal.context.Context` for more details.

    Example of usage:

    .. code-block:: python

        @alfasim_sdk.hookimpl
        def alfasim_configure_layers(ctx):
           return [
               AddLayer(
                   name='plugin_layer',
                   fields=['plugin_continuous_field'],
                   continuous_field='plugin_continuous_field',
               ),
               UpdateLayer(
                   name=OIL_LAYER,
                   additional_fields=['plugin_dispersed_field'],
               ),
           ]

    The image below shows the new added phase on the application.

    .. image:: /_static/images/hooks/alfasim_configure_layer_example_1.png
        :scale: 80%

    """


@hookspec
def alfasim_configure_phases(ctx: Context):
    """
    Allows plugins to configure new phases or associate a new field with a existing phase from the application.
    In order to configure a new phase it is necessary to return an :class:`~alfasim_sdk.AddPhase` object defining the
    required fields.

    The ``ctx`` parameter is provided to retrieve information about the current state of the application and the current value
    of the models implemented by the user.

    Check out the full documentation of :class:`~alfasim_sdk._internal.context.Context` for more details.

    Example of usage:

    .. code-block:: python

        @alfasim_sdk.hookimpl
        def alfasim_configure_phases(ctx):
            return [
                AddPhase(
                    name='plugin_phase',
                    fields=[
                        'plugin_continuous_field',
                        'plugin_dispersed_field',
                    ],
                    primary_field='plugin_continuous_field',
                    is_solid=False,
                )
            ]

    With this new phase, all existing hydrodynamic models from the application will have this additional phase.
    Notice that the ``fields`` parameter must be a field registered from the hook :func:`alfasim_configure_fields`.

    .. note::

            You can restrict the operation of your plugin in the application to certain settings by using the status monitor.
            For example, if your plugin does not work with the water phase you can block the simulation
            if the user is using a hydrodynamic model with water.

            For more details check out the documentation of :func:`alfasim_get_status`


    The image below shows the new added phase on the application.

    .. image:: /_static/images/hooks/alfasim_configure_phase_example_1.png
        :scale: 80%

    It is also possible to add additional fields to existent phases using the :class:`~alfasim_sdk.UpdatePhase`.

    Example of usage:

    .. code-block:: python

        @alfasim_sdk.hookimpl
        def alfasim_configure_phases(ctx):
            return [
                UpdatePhase(
                    name=OIL_PHASE,
                    additional_fields=['plugin_dispersed_field'],
                )
            ]

    """


@hookspec
def alfasim_get_phase_properties_calculated_from_plugin():
    """
    Allows the plugin to calculate the properties (state variables) of a phase.

    Must return a list of phase names in which state variables will be computed for. If the plugin implements this `hook`
    four C/C++ Solver `hooks` also must be implemented. They are:

     - :py:func:`HOOK_INITIALIZE_STATE_VARIABLE_CALCULATOR<alfasim_sdk._internal.hook_specs.initialize_state_variables_calculator>`
     - :py:func:`HOOK_CALCULATE_STATE_VARIABLE<alfasim_sdk._internal.hook_specs.calculate_state_variable>`
     - :py:func:`HOOK_CALCULATE_PHASE_PAIR_STATE_VARIABLE<alfasim_sdk._internal.hook_specs.calculate_phase_pair_state_variable>`
     - :py:func:`HOOK_FINALIZE_STATE_VARIABLE_CALCULATOR<alfasim_sdk._internal.hook_specs.finalize_state_variables_calculator>`

    The first and last hooks are called immediately before and after the state variables are calculated, respectively.

     Example of usage:

    .. code-block:: python

        from alfasim_sdk import GAS_PHASE

        @alfasim_sdk.hookimpl
        def alfasim_get_phase_properties_calculated_from_plugin():
            return [GAS_PHASE, 'solid']

    """


@hookspec
def alfasim_get_phase_interaction_properties_calculated_from_plugin():
    """
    Allows the plugin to calculate the properties that are related to a pair of phases, like `surface tension`.

    Must return a list of tuple of phases in which state variables will be computed for. In order to
    implement the properties, :py:func:`HOOK_CALCULATE_PHASE_PAIR_STATE_VARIABLE<alfasim_sdk._internal.hook_specs.calculate_phase_pair_state_variable>`
    must be implemented on the C/C++ part of the plugin.

    Example of usage:

    .. code-block:: python

        from alfasim_sdk import GAS_PHASE, OIL_PHASE, WATER_PHASE

        @alfasim_sdk.hookimpl
        def alfasim_get_phase_interaction_properties_calculated_from_plugin():
        return [
            (GAS_PHASE, OIL_PHASE),
            (GAS_PHASE, WATER_PHASE),
        ]

    """


@hookspec
def alfasim_get_user_defined_tracers_from_plugin():
    """
    Allows the plugin to add new tracers in the |alfasim|'s Tracer Solver, in which the transport equation will be
    modified by Solver `hooks` listed below.

    Must return a list of tracers in which the internal tracer model `hooks` will be implemented.
    The following C/C++ Solver `hooks` must be implemented:

     - :py:func:`HOOK_INITIALIZE_MASS_FRACTION_OF_TRACER<alfasim_sdk._internal.hook_specs.initialize_mass_fraction_of_tracer>`
     - :py:func:`HOOK_COMPUTE_MASS_FRACTION_OF_TRACER_IN_PHASE<alfasim_sdk._internal.hook_specs.calculate_mass_fraction_of_tracer_in_phase>`
     - :py:func:`HOOK_COMPUTE_MASS_FRACTION_OF_TRACER_IN_FIELD<alfasim_sdk._internal.hook_specs.calculate_mass_fraction_of_tracer_in_field>`
     - :py:func:`HOOK_SET_BOUNDARY_CONDITION_OF_MASS_FRACTION_OF_TRACER<alfasim_sdk._internal.hook_specs.set_prescribed_boundary_condition_of_mass_fraction_of_tracer>`
     - :py:func:`HOOK_UPDATE_BOUNDARY_CONDITION_OF_MASS_FRACTION_OF_TRACER<alfasim_sdk._internal.hook_specs.update_boundary_condition_of_mass_fraction_of_tracer>`

    Example of usage:

    .. code-block:: python

        @alfasim_sdk.hookimpl
        def alfasim_get_user_defined_tracers_from_plugin():
            return ['my_tracer']

    .. note::
        The tracer added in the `user-defined tracers from plugin` list will not be considered as a standard tracer, which
        has an output of its `mass fraction` and appears in the tracer container at |alfasim|'s User Interface. The `user-defined
        tracer` is hidden (does not appear in the User Interface) and the plugin developer can modify the transport equation
        to use its results internally. However, the `user-defined tracers` will be solved together with the standard tracers
        (Added via User Interface).

    """
