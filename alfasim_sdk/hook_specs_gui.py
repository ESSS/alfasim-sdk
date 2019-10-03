from typing import List
from typing import Union

from pluggy import HookspecMarker

from alfasim_sdk.status import ErrorMessage
from alfasim_sdk.status import WarningMessage

hookspec = HookspecMarker("ALFAsim")


@hookspec
def alfasim_get_data_model_type():
    """
    Entry point for the creation of models in ALFAsim
    """


@hookspec
def alfasim_get_additional_variables():
    """
    Allows plugins to register new additional variables on ALFAsim.
    This variable can be used to store internal data from the plugin,
    or it can be used to expose data to the user in the plot window.
    """


@hookspec
def alfasim_get_status(ctx) -> List[Union[WarningMessage, ErrorMessage]]:
    """
    Allows plugins to execute custom checks on ALFAsim.
    This checks can be used to guarantee the consistency of the data,
    or compatibility with some configuration made on ALFAsim.

    Example:
        from alfasim_sdk.status import ErrorMessage
        @alfasim_sdk.hookimpl
        def alfasim_get_status(ctx):
            results = []

            plugin_info_2 = ctx.GetPluginByName('Plugin2')
            if plugin_info_2.enabled:
                if ctx.GetModel('MyModel').distance.value < 0:
                    results.append(ErrorMessage(model_name="MyModel", message='Distance must be greater than 0'))

            return results


    :param ctx: ALFAsim's plugins context
        The ctx parameter has the following attributes:

            GetPluginInfo:
                Method that return a list of PluginInfo, with the name of the plugin and its current state
                Check :class:`alfasim_sdk.status.PluginInfo` for more details about the returned value.

            GetModel:
                Method to access the Models registry, it receives a single argument that should be name of the class defined.

                Example.:

                @data_model
                Class MyModel
                    distance = Quantity(value=1, unit='m', caption='Distance')

                @alfasim_sdk.hookimpl
                def alfasim_get_status(ctx):
                    results = []

                    if ctx.GetModel('MyModel').distance.value < 0:
                        results.append(ErrorMessage(model_name="MyModel", message='Distance must be greater than 0'))

                :param str model_name: Name of the class to access
                :raises TypeError: When the model informed is not available.

    :returns: A list of status message either WarningMessage or ErrorMessage
    """


@hookspec
def alfasim_configure_fields():
    """
    Configure new fields to be added in ALFAsim's hydrodynamic model.
    Example:

    return [
        AddField(name='plugin_continuous_field'),
        AddField(name='plugin_dispersed_field')
    ]
    """


@hookspec
def alfasim_configure_layers():
    """
    Configure new or update layers for ALFAsim's hydrodynamic model.
    Example:

    return [
        AddLayer(name='plugin_layer', fields=['plugin_continuous_field', DROPLET_FIELD], continuous_field='plugin_continuous_field'),
        UpdateLayer(name=WATER_LAYER, additional_fields=['plugin_dispersed_field']),
    ]
    """


@hookspec
def alfasim_configure_phases():
    """
    Configure new or update phases for ALFAsim's hydrodynamic model.
    Example:

    return [
        AddPhase(name='plugin_phase', fields=['plugin_continuous_field', DROPLET_FIELD], primary_field='plugin_continuous_field'),
        UpdatePhase(name=WATER_PHASE, additional_fields=['plugin_dispersed_field']),
    ]
    """


@hookspec
def alfasim_get_phase_properties_calculated_from_plugin():
    """
    Must return a list of phases in which state variables will be computed for. In order to
    implement the properties, HOOK_CALCULATE_STATE_VARIABLE must be implemented on the C plugin.

    Example:
    from alfasim_sdk.constants import GAS_PHASE
    return [GAS_PHASE, 'solid,]
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
