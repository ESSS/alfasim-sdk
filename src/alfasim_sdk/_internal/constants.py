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
WATER_DROPLET_IN_OIL_FIELD = "water in oil"
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
    FromPlugin = "from_plugin"


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

    - FromPlugin:
        Slip velocity and slurry viscosity are calculated from plugin hooks with an external implementation.
    """

    NoModel = "no_model"
    Thomas1965Equilibrium = "thomas1965_equilibrium"
    Mills1985Equilibrium = "mills1985_equilibrium"
    Santamaria2010Equilibrium = "santamaria2010_equilibrium"
    FromPlugin = "from_plugin"


class NodeCellType(Enum):
    Internal = "internal_node"
    MassSource = "mass_source_boundary"
    Pressure = "pressure_boundary"
    Separator = "separator_node"
    Controller = "controller_node"


class MassInflowSplitType(Enum):
    """
    PvtUserGorWc is currently only used for GenKey
    """

    ConstantVolumeFraction = "mass_inflow_split_type_constant_volume_fraction"
    ConstantMassFraction = "mass_inflow_split_type_constant_mass_fraction"
    Pvt = "mass_inflow_split_type_pvt"
    PvtUserGorWc = "mass_inflow_split_type_pvt_user_gor_wc"
    PvtUserGlrWc = "mass_inflow_split_type_pvt_user_glr_wc"


class WellIndexPhaseType(Enum):
    Gas = "well_index_phase_gas"
    Oil = "well_index_phase_oil"
    Water = "well_index_phase_water"
    Liquid = "well_index_phase_liquid"


class MassSourceType(Enum):
    MassFlowRates = "mass_source_type_mass_flow_rates"
    AllVolumetricFlowRates = "mass_source_type_all_volumetric_flow_rates"
    FlowRateOilGorWc = "mass_source_type_flow_rate_oil_gor_wc"
    FlowRateGasGorWc = "mass_source_type_flow_rate_gas_gor_wc"
    FlowRateWaterGorWc = "mass_source_type_flow_rate_water_gor_wc"
    TotalMassFlowRatePvtSplit = "mass_source_type_total_mass_flow_rate_pvt_split"


class PipeThermalModelType(Enum):
    AdiabaticWalls = "adiabatic_walls"
    SteadyState = "steady_state_heat_transfer"
    Transient = "transient_heat_transfer"


class PipeThermalPositionInput(Enum):
    Tvd = "position_by_tvd"
    Md = "position_by_md"


class PipeEnvironmentHeatTransferCoefficientModelType(Enum):
    WallsAndEnvironment = "walls_and_environment_heat_transfer_coefficient"
    WallsAndWater = "walls_and_water_heat_transfer_coefficient_model"
    WallsAndAir = "walls_and_air_heat_transfer_coefficient_model"
    Overall = "overall_heat_transfer_coefficient_model"
    WallsWithoutEnvironment = "walls_without_environment_heat_transfer_coefficient"


class PVTCompositionalViscosityModel(Enum):
    CorrespondingStatesPrinciple = "corresponding_states_principle"
    LohrenzBrayClark = "lohrenz_bray_clark"


class MaterialType(Enum):
    Solid = "solid"
    Fluid = "fluid"


FLUID_GAS = "gas"
FLUID_OIL = "oil"
FLUID_WATER = "water"
FLUID_PHASE_NAMES = [FLUID_GAS, FLUID_OIL, FLUID_WATER]


class CorrelationPackageType(Enum):
    Classical = "correlation_package_classical"
    Alfasim = "correlation_package_alfasim"
    ISDBTests = "correlation_package_isdb_tests"  # TODO ASIM-2545: Overview ISDb optimization changes


class SurfaceTensionType(Enum):
    Weinaugkatz = "WeinaugKatz"
    Leechien = "LeeChien"
    Schechterguo = "SchechterGuo"


class EquationOfStateType(Enum):
    PengRobinson = "pvt_compositional_peng_robinson"
    SoaveRedlichKwong = "pvt_compositional_soave_redlich_kwong"


class EnergyModel(Enum):
    """
    Do not rely on the value of this enum, it is used exclusively for backward compatibility
    """

    NoModel = "no_model"
    GlobalModel = "global_model"
    LayersModel = "layers_model"


class EnergyModelPrimaryVariable(Enum):
    """
    Do not rely on the value of this enum, it is used exclusively for backward compatibility
    """

    Enthalpy = "enthalpy"
    Temperature = "temperature"


class FlashModel(Enum):
    """
    Do not rely on the value of this enum, it is used exclusively for backward compatibility
    """

    HydrocarbonOnly = "hydrocarbon_only"
    HydrocarbonAndWater = "hydrocarbon_and_water"


class DrainageRateMode(Enum):
    """
    Drainage Rate mode used by Surge Volume curves calculation.
    """

    #: Uses a default drain flow rate = (AccLiq(end_time) - AccLiq(start_time))/(end_time - start_time)
    Automatic = "automatic"
    #: Allows the user to input a maximum drainage rate
    UserDefined = "user_defined"


class SurgeVolumeTimeMode(Enum):
    """
    Time mode used by Surge Volume curves calculation.
    """

    #: Uses the initial and final time of the whole simulation.
    AllSimulation = "all_simulation"
    #: Uses custom initial/final time input by the user.
    UserDefined = "user_defined"


class FlowDirection(Enum):
    Forward = "forward"
    Backward = "backward"


class InterpolationType(Enum):
    Constant = "constant"
    Linear = "linear"
    Quadratic = "quadratic"


class SeparatorGeometryType(Enum):
    VerticalCylinder = "vertical_cylinder"
    HorizontalCylinder = "horizontal_cylinder"
    Sphere = "sphere"


class TableInputType(Enum):
    """
    Indicates the semantics of a position field

    vertical_position: Interpolation will be calculated in relation to the y-axis
    horizontal_position: Interpolation will be calculated in relation to the x-axis
    length: Interpolation will be calculated in relation to the pipeline trajectory
    """

    vertical_position = "vertical_position"
    horizontal_position = "horizontal_position"
    length = "length"


class TracerModelType(Enum):
    Global = "tracer_model_global"
    Compositional = "tracer_model_compositional"


class SimulationRegimeType(Enum):
    Transient = "simulation_regime_transient"
    SteadyState = "simulation_regime_steady_state"


class SimulationModeType(Enum):
    Default = "default"
    Robust = "robust"


DEFAULT_TEMPERATURE_IN_K = 288.6


class MultiInputType(Enum):
    Constant = "constant"
    Curve = "curve"


class PumpType(Enum):
    ConstantPressure = "constant_pressure"
    TableInterpolation = "table_interpolation"


class ValveOpeningType(Enum):
    ConstantOpening = "constant_opening"
    TableInterpolation = "table_interpolation"


class ValveType(Enum):
    PerkinsValve = "perkins_valve"
    ChokeValveWithFlowCoefficient = "choke_valve_with_flow_coefficient"
    CheckValve = "check_valve"


class LeakModel(Enum):
    Orifice = "orifice"
    FlowCoefficient = "flow_coefficient"
    GasLiftValve = "gas_lift_valve"


class LeakType(Enum):
    Internal = "internal"
    External = "external"


class GasLiftValveOpeningType(Enum):
    MinimumPressureDifference = "minimum_pressure_difference"
    PressureOperated = "pressure_operated"


class CompressorSpeedType(Enum):
    SpeedCurve = "speed_curve"
    ConstantSpeed = "constant_speed"


class OutputAttachmentLocation(Enum):
    """
    Output Attachment Location will tell the location in which this attachment's data should be retrieved from.
    """

    Main = "main"
    Annulus = "annulus"
    NotDefined = "not_defined"


LeakLocation = OutputAttachmentLocation


class EquipmentAttachmentLocation(Enum):
    """
    Location in which an equipment can be attached.
    """

    Main = "main"
    Annulus = "annulus"
    Both = "both"


class CorrelationPackage(Enum):
    Lasater = "pvt_correlation_package_lasater"
    Standing = "pvt_correlation_package_standing"
    VazquezBeggs = "pvt_correlation_package_vazquez_beggs"
    Glaso = "pvt_correlation_package_glaso"


class InitialConditionStrategyType(Enum):
    Constant = "constant"
    SteadyState = "steady_state"
    Restart = "restart"


class NonlinearSolverType(Enum):
    NewtonBasic = "nonlinear_solver_newton_basic"
    NewtonBacktracking = "nonlinear_solver_newton_backtracking"
    AlfasimQuasiNewton = "nonlinear_solver_alfasim_quasi_newton"


class EvaluationStrategyType(Enum):
    TimeExplicit = "time_explicit"
    NewtonExplicit = "newton_explicit"
    Implicit = "implicit"


class WellConnectionPort(Enum):
    """
    Available ports for connecting to a Well node.
    """

    Top = "port"  # 'port' is being used for backwards compatibility.
    LeftAnnulus = "left_annulus_port"
    RightAnnulus = "right_annulus_port"


class ControllerType(Enum):
    PID = "pid"


class PigTrappingMode(Enum):
    """
    Trapping mode of a PIG equipment.
    """

    #: The PIG is automatically trapped whenever it reaches a boundary node (e.g.,
    #: pressure or mass boundary).
    Automatic = "automatic"

    #: The PIG is trapped according to user-defined pipe and position unless it
    #: reaches a boundary node first.
    UserDefined = "user_defined"


class PigRoutingMode(Enum):
    """
    Trapping mode of a PIG equipment.
    """

    #: When a PIG encounters an internal node, the next pipe in which the PIG goes to
    #: is selected based on the pipe with greatest total mass flow rate at that point.
    Automatic = "automatic"

    #: When a PIG encounters an internal node, the next pipe in which the PIG goes
    #: to is selected based on a user-defined trajectory (edge group).
    UserDefined = "user_defined"


MULTI_INPUT_TYPE_SUFFIX = "_input_type"
