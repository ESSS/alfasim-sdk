from typing import List
from typing import Optional
from typing import Union

from pluggy import HookspecMarker

from alfasim_sdk.context import Context
from alfasim_sdk.status import ErrorMessage
from alfasim_sdk.status import WarningMessage
from alfasim_sdk.variables import SecondaryVariable


hookspec = HookspecMarker("ALFAsim")


@hookspec
def alfasim_get_data_model_type():
    """
    This hook allows the creation of models in ALFAsim, models can:

    - Customize items on ALFAsim application, by adding new components over the Tree.
    - Hold input data information to be accessed from the solver.
    - Validate input data or configuration made on ALFAsim, to ensure that the plugin has all configuration necessary to be run successfully.

    This hook needs to return a class decorated with one of the following options:

    - :func:`alfasim_sdk.models.container_model`
    - :func:`alfasim_sdk.models.data_model`

    The image bellow shows the locations where a custom model can be inserted implementing the hook.

    .. image:: _static/tree_plugin_marker.png
        :scale: 80%
        :target: /_static/tree_plugin_marker.png

    .. image:: _static/model_explorer_with_marker.png
        :scale: 80%
        :target: _static/model_explorer_with_marker.png

    .. |m_1| image:: _static/marker_1.png
        :scale: 80%

    .. |m_2| image:: _static/marker_2.png
        :scale: 80%

    |m_1| Location to where the models :func:`~alfasim_sdk.models.container_model` or :func:`~alfasim_sdk.models.data_model` will be placed. |br|
    |m_2| Location to where the :ref:`inputs fields <api-types-section>` will be placed.

    Example 1: The following example shows how to create a new model.

    .. code-block:: python

        import alfasim_sdk
        from alfasim_sdk.models import data_model
        from alfasim_sdk.types import Quantity

        @data_model(icon="", caption="My Plugin")
        class MyModel:
            distance = Quantity(value=1, unit="m", caption="Distance")

        @alfasim_sdk.hookimpl
        def alfasim_get_data_model_type():
            return [MyModel]

    The image below shows the output of example 1 when executing on ALFAsim.

    .. image:: _static/alfasim_get_data_model_type_example_1.png
        :scale: 80%


    Example 2: This second example shows hot to create a new container model.

    Notice that when using the :func:`~alfasim_sdk.models.container_model` you only need to inform the container class
    to the :func:`~alfasim_sdk.hook_specs_gui.alfasim_get_data_model_type` hook

    .. code-block:: python

        import alfasim_sdk
        from alfasim_sdk.models import data_model, container_model
        from alfasim_sdk.types import Quantity, String

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

    .. image:: _static/alfasim_get_data_model_type_example_2.png
        :scale: 80%

    Example 3: This third example demonstrates that it's possible to create multiple models within the plugin

    .. code-block:: python

        import alfasim_sdk
        from alfasim_sdk.models import data_model, container_model
        from alfasim_sdk.types import Quantity, String

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

    The image below shows the output of example 3 when executing on ALFAsim.

    .. image:: _static/alfasim_get_data_model_type_example_3.png
        :scale: 80%
    """


@hookspec
def alfasim_get_additional_variables() -> List[SecondaryVariable]:
    """
    Allows plugins to register new additional variables on ALFAsim.

    This variable can be used to store internal data from the plugin, (on solver)
    or it can be used to expose data to the user in the plot window (on application).

    This method expects to return a list of :func:`alfasim_sdk.variables.SecondaryVariable`, for more details checkout
    the reference section with all details about :ref:`variables <api-variables-section>`

    Usage example:

    .. code-block:: python

        from alfasim_sdk.variables import SecondaryVariable, Visibility
        from alfasim_sdk.variables import Location, Scope

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
    ctx: Context
) -> Optional[List[Union[WarningMessage, ErrorMessage]]]:
    """
    Allows plugins to execute custom checks on ALFAsim.
    These checks can be used to guarantee the consistency of the data or compatibility with some configuration made on ALFAsim.

    The status monitor accepts two types of message:

     - :func:`~alfasim_sdk.status.ErrorMessage`:
        Signalize the application to lock the simulation until the error is fixed.

     - :func:`~alfasim_sdk.status.WarningMessage`:
        Signalize the application that the user needs to fix this problem, but does not need to block the simulation.

    When no errors are detected, an empty list must be returned.

    The ``alfasim_get_status`` will be called for:

     - Each time an input from the plugin model is modified.
     - Each time a ``Physics options`` from ALFAsim are modified. |br|
       Ex.: Hydrodynamic model changed

    The ``ctx`` parameter is provided in order to retrieve information about the current state of the application and the curretn value
    of the models implemented by the user.

    Checkout the full documentation of :class:`alfasim_sdk.context.Context` for more details.

    The following example shows how to display an ErrorMessage when a :func:`~alfasim_sdk.types.Quantity` field does not have a desired value.

    .. code-block:: python

        import alfasim_sdk
        from alfasim_sdk.models import data_model
        from alfasim_sdk.types import Quantity
        from alfasim_sdk.status import ErrorMessage

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


    For the status monitor above the application will show the following message, when the distance is lower than 0:

    .. image:: _static/status_monitor_with_distance_error.png

    """


@hookspec
def alfasim_configure_fields():
    """
    Allows plugins to configure new fields to be added in ALFAsim's hydrodynamic model.

    An added ``field`` must be associated with:

     - Phase, defined by :func:`~alfasim_sdk.types.AddPhase` or :func:`~alfasim_sdk.types.UpdatePhase`.
     - Layer, defined by :func:`~alfasim_sdk.types.AddLayer` or :func:`~alfasim_sdk.types.UpdateLayer`.


    Example of usage:

    .. code-block:: python

        @alfasim_sdk.hookimpl
        def alfasim_configure_fields():
           return [
                   AddField(name='plugin_continuous_field'),
                   AddField(name='plugin_dispersed_field'),
           ]


    """


@hookspec
def alfasim_configure_layers():
    """
    Allows plugins to configure new layers or associate a new field with a existing layer for ALFAsim's hydrodynamic model

    In order to configure a new layer is necessary to return an :func:`~alfasim_sdk.types.AddLayer` object defining the
    required fields.


    Example of usage:

    .. code-block:: python

        @alfasim_sdk.hookimpl
        def alfasim_configure_layers():
           return [
                   AddLayer(
                       name='plugin_layer',
                       fields=['plugin_continuous_field'],
                       continuous_field='plugin_continuous_field',
                   ),
                   UpdateLayer(
                       name=LIQUID_LAYER,
                       additional_fields=['plugin_dispersed_field'],
                   ),
           ]

    The image bellow shows the new added phase on the application.

    .. image:: _static/alfasim_configure_layer_example_1.png
        :scale: 80%



    """


@hookspec
def alfasim_configure_phases():
    """
    Allows plugins to configure new phases or associate a new field with a existing phase from the application.
    In order to configure a new phases is necessary to return an :func:`~alfasim_sdk.types.AddPhase` object defining the
    required fields.

    Example of usage:

    .. code-block:: python

        @alfasim_sdk.hookimpl
        def alfasim_configure_phases():
            return [
                AddPhase(
                    name='plugin_phase',
                    fields=[
                        'plugin_continuous_field',
                        'plugin_dispersed_field',
                    ],
                    primary_field='plugin_continuous_field',
                )
            ]

    With this new phase, all existing hydrodynamic models from the application will have this additional phase.
    Notice that the ``fields`` parameter must be a field registered from the hook :func:`~alfasim_sdk.hook_specs_gui.alfasim_configure_fields`.

    .. note:

        If your plugin cannot work with an existing ALFAsim phase, for example the water phase.
        Your can restrict the ALFAsim application through the status monitor, by checking the current hydrodynamic model
        from the Physic option, for more details checkout the documentation of :ref:`~alfasim_sdk.hook_specs_gui.alfasim_get_status`

    The image bellow shows the new added phase on the application.

    .. image:: _static/alfasim_configure_phase_example_1.png
        :scale: 80%

    Is also possible to add additional fields to an existent phases using the :func:`~alfasim_sdk.types.UpdatePhase`.

    Example of usage:

    .. code-block:: python

        @alfasim_sdk.hookimpl
        def alfasim_configure_phases():
            return [
                UpdatePhase(
                name=LIQUID_PHASE,
                additional_fields=['plugin_dispersed_field'],
                )
            ]

    """


@hookspec
def alfasim_get_phase_properties_calculated_from_plugin():
    """
    Must return a list of phases in which state variables will be computed for. In order to
    implement the properties, HOOK_CALCULATE_STATE_VARIABLE must be implemented on the C plugin.

    Example:
    from alfasim_sdk.constants import GAS_PHASE
    return [GAS_PHASE, 'solid']

    """


@hookspec
def alfasim_get_phase_interaction_properties_calculated_from_plugin():
    """
    Must return a list of tuple of phases in which state variables will be computed for. In order to
    implement the properties, HOOK_CALCULATE_PHASE_PAIR_STATE_VARIABLE must be implemented on the C
    plugin.

    Example:
    from alfasim_sdk.constants import GAS_PHASE, LIQUID_PHASE, WATER_PHASE
    return [
        (GAS_PHASE, LIQUID_PHASE),
        (GAS_PHASE, WATER_PHASE),
    ]

    """


@hookspec
def alfasim_get_user_defined_tracers_from_plugin():
    """
    Must return a list of tracers in which the internal tracer model hooks will be implemented for.
    the HOOK_COMPUTE_MASS_FRACTION_OF_TRACER_IN_PHASE, HOOK_COMPUTE_MASS_FRACTION_OF_TRACER_IN_FIELD
    and UPDATE_BOUNDARY_CONDITION_OF_MASS_FRACTION_OF_TRACER must be implemented on the C plugin.

    Example:
    return ['my_tracer']

    """
