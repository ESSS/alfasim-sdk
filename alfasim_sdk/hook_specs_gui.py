from typing import List

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
def alfasim_get_status(ctx) -> List[WarningMessage, ErrorMessage]:
    """
    Allows plugins to execute custom checks on ALFAsim.
    This checks can be used to guarantee the consistency of the data,
    or compatibility with some configuration made on ALFAsim.
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
