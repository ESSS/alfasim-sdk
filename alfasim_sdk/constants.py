from enum import Enum


GAS_PHASE = "gas"
"""
Constant to identify the gas phase
"""

LIQUID_PHASE = "liquid"
"""
Constant to identify the liquid phase
"""

WATER_PHASE = "water"
"""
Constant to identify the water phase
"""

SOLID_PHASE = "solid"

GAS_FIELD = "gas"
LIQUID_FIELD = "liquid"
WATER_FIELD = "water"
WATER_DROPLET_IN_LIQUID_FIELD = "water_in_liquid_droplet"
DROPLET_FIELD = "droplet"
BUBBLE_FIELD = "bubble"

GAS_LAYER = "gas"
"""
Constant to identify the gas layer
"""

LIQUID_LAYER = "liquid"
"""
Constant to identify the liquid layer
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

    - TwoFields - 'Two-fluid, Regime Capturing (gas-liquid)':
        Two phase (gas and liquid) with two fields (continuous gas and continuous liquid) using Regime Capturing strategy.

    - FourFields - 'Multi-field, Unit Cell (gas-liquid)':
        Two phase (gas and liquid) with four fields (continuous gas, continuous liquid, dispersed gas bubble, and dispersed liquid droplet).

    - ThreeLayersGasOilWater - 'Multi-field, Unit Cell (gas-liquid-water)':
        Three phase (gas, liquid, and water) with five fields (continuous gas, continuous liquid, continuous water, dispersed gas bubble, and dispersed liquid droplet).

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
