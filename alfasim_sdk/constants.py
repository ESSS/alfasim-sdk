from enum import Enum


GAS_PHASE = "gas"
"""
Constant to identify the gas phase
"""

OIL_PHASE = "oil"
"""
Constant to identify the oil phase
"""

WATER_PHASE = "water"
"""
Constant to identify the water phase
"""

SOLID_PHASE = "solid"

GAS_FIELD = "gas"
OIL_FIELD = "oil"
WATER_FIELD = "water"
WATER_DROPLET_IN_OIL_FIELD = "water_in_oil_droplet"
DROPLET_FIELD = "droplet"
BUBBLE_FIELD = "bubble"

GAS_LAYER = "gas"
"""
Constant to identify the gas layer
"""

OIL_LAYER = "oil"
"""
Constant to identify the oil layer
"""

WATER_LAYER = "water"
"""
Constant to identify the water layer
"""

EXTRAS_REQUIRED_VERSION_KEY = "required-alfasim-sdk"
"""
The dict key which identifies the required version of alfasim-sdk for a given plugin
"""


class HydrodynamicModelType(Enum):
    """
    Informs which base Hydrodynamic model is being used, without any modification from plugins:

    TwoFields is valid only for the slug/regime capturing

    - TwoFields - 'Two-fluid, Regime Capturing (gas-oil)':
        Two phase (gas and oil) with two fields (continuous gas and continuous oil) using Regime Capturing strategy.

    - FourFields - 'Multi-field, Unit Cell (gas-oil)':
        Two phase (gas and oil) with four fields (continuous gas, continuous oil, dispersed gas bubble, and dispersed oil droplet).

    - ThreeLayersGasOilWater - 'Multi-field, Unit Cell (gas-oil-water)':
        Three phase (gas, oil, and water) with five fields (continuous gas, continuous oil, continuous water, dispersed gas bubble, and dispersed liquid droplet).

    """

    TwoFields = "hydrodynamic_model_2_fields"
    FourFields = "hydrodynamic_model_4_fields"
    ThreeLayersGasOilWater = "hydrodynamic_model_3_layers_gas_oil_water"
    FiveFieldsSolid = "hydrodynamic_model_5_fields_solid"  # Under Development
    FiveFieldsWater = "hydrodynamic_model_5_fields_water"  # Under Development
    FiveFieldsCO2 = "hydrodynamic_model_5_fields_co2"  # Under Development
    ThreeLayersNoBubbleGasOilWater = (
        "hydrodynamic_model_3_layers_no_bubble_gas_oil_water"  # Under Development
    )
    ThreeLayersWaterWithCO2 = (
        "hydrodynamic_model_3_layers_water_with_co2"  # Under Development
    )

    two_phase_four_field_ucm = FourFields  # backward compatibility
    three_phase_five_field_ucm = ThreeLayersGasOilWater  # backward compatibility
    two_phase_two_field_slug_capturing = TwoFields  # backward compatibility
