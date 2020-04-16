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

    - ThreeLayersGasOilWater - 'Multi-field, Unit Cell (gas-oil-water), free water':
        Three phase (gas, oil, and water) with five fields (continuous gas, continuous oil, continuous water, dispersed gas bubble, and dispersed liquid droplet).
        Water does not disperse in any other phase

    - ThreeLayersSevenFieldsGasOilWater - 'Multi-field, Unit Cell (gas-oil-water), no liquid-liquid dispersion':
        Three phase (gas, oil, and water) with seven fields (continuous gas, continuous oil, continuous water, gas in oil, gas in water,
        oil in gas, and water in gas. There is no dispersion of oil in water and water in oil.

    - ThreeLayersNineFieldsGasOilWater - 'Multi-field, Unit Cell (gas-oil-water)':
        Full three phase gas oil water model. Three continuous fields and six dispersed fields.
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
    ThreeLayersSevenFieldsGasOilWater = (
        "hydrodynamic_model_3_layers_7_fields_gas_oil_water"
    )
    ThreeLayersNineFieldsGasOilWater = (
        "hydrodynamic_model_3_layers_9_fields_gas_oil_water"
    )


class EmulsionModelType(Enum):
    """
    Options for emulsion properties calculation.
    """

    NoModel = "no_model"
    ModelDefault = "model_default"
    Taylor1932 = "taylor1932"
    Brinkman1952 = "brinkman1952"
    Mooney1951a = "mooney1951a"
    Mooney1951b = "mooney1951b"
    Hinze1955 = "hinze1955"
    Sleicher1962 = "sleicher1962"
    Brauner2001 = "brauner2001"
    Boxall2012 = "boxall2012"
    Brinkman1952AndYeh1964 = "brinkman1952_and_yeh1964"


class SolidsModelType(Enum):
    """
    Informs which solid model should be used:

    - NoModel - None:RR
        Without slip velocity and slurry viscosity

    - Mills1985Equilibrium - Mills (1985):
        Employs the equilibrium slip velocity model and the Mills (1985) effective dynamic viscosity expression.

    - Santamaria2010Equilibrium - Santamaría-Holek (2010):
        This model is more appropriate to use when the solid phase has properties similar to or equal to hydrate.
        It was fitted by Qin et al. (2018) for hydrates.

    - Thomas1965Equilibrium - Thomas (1965):
        Employs the equilibrium slip velocity model and the Thomas (1965) effective dynamic viscosity expression.
    """

    NoModel = "no_model"
    Thomas1965Equilibrium = "thomas1965_equilibrium"
    Mills1985Equilibrium = "mills1985_equilibrium"
    Santamaria2010Equilibrium = "santamaria2010_equilibrium"
