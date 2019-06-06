from pluggy import HookspecMarker

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
