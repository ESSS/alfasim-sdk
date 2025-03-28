from pathlib import Path

import numpy as np
from barril.curve.curve import Curve
from barril.units import Array, Scalar

from alfasim_sdk import LeakLocation
from alfasim_sdk._internal import constants
from alfasim_sdk._internal.alfacase import case_description
from alfasim_sdk._internal.alfacase.alfacase_to_case import get_category_for

from . import case_builders, get_acme_tab_file_path

BIP_DESCRIPTION = case_description.BipDescription(
    component_1="C1", component_2="C2", value=0.5
)
COMPOSITION_DESCRIPTION_C1 = case_description.CompositionDescription(
    component="C1",
    molar_fraction=Scalar(5, "mol/mol"),
    reference_enthalpy=Scalar(10, "J/mol"),
)
COMPOSITION_DESCRIPTION_C2 = case_description.CompositionDescription(
    component="C2",
    molar_fraction=Scalar(15, "mol/mol"),
    reference_enthalpy=Scalar(20, "J/mol"),
)
HEAVY_COMPONENT_DESCRIPTION = case_description.HeavyComponentDescription(
    name="C7", scn=7, MW=Scalar(0.100204, "kg/mol"), rho=Scalar(687.4, "kg/m3")
)
LIGH_COMPONENT_DESCRIPTION = case_description.LightComponentDescription(
    name="Component X",
    Pc=Scalar("pressure", 1, "Pa"),
    Tc=Scalar("temperature", 2, "K"),
    Vc=Scalar("molar volume", 3, "m3/mol"),
    omega=Scalar("dimensionless", 5, "-"),
    MW=Scalar("mass per mol", 6, "kg/mol"),
    Tb=Scalar("temperature", 7, "K"),
    Parachor=Scalar("dimensionless", 8, "-"),
    Cp_0=Scalar("dimensionless", 9, "-"),
    Cp_1=Scalar("dimensionless", 10, "-"),
    Cp_2=Scalar("dimensionless", 11, "-"),
    Cp_3=Scalar("dimensionless", 12, "-"),
    Cp_4=Scalar("dimensionless", 13, "-"),
)
LIGH_COMPONENT_DESCRIPTION_OVERWRITE_C3 = case_description.LightComponentDescription(
    name="C3", Pc=Scalar("pressure", 42, "Pa")
)
PVT_MODEL_CORRELATION_DEFINITION = case_description.PvtModelCorrelationDescription(
    oil_density_std=Scalar(42, "kg/m3"),
    gas_density_std=Scalar(2, "kg/m3"),
    rs_sat=Scalar(4, "sm3/sm3"),
    pvt_correlation_package=constants.CorrelationPackage.Lasater,
    h2s_mol_frac=Scalar(0, "-"),
    co2_mol_frac=Scalar(0, "-"),
    oil_viscosity=constants.CorrelationsOilViscosity.Egbogah,
    gas_viscosity=constants.CorrelationsGasViscosity.LeeGonzalezEakin,
    surface_tension=constants.CorrelationsSurfaceTension.BakerSwerdloff,
)
COMPOSITIONAL_FLUID_DESCRIPTION = case_description.CompositionalFluidDescription(
    composition=[COMPOSITION_DESCRIPTION_C1, COMPOSITION_DESCRIPTION_C2],
    fraction_pairs=[BIP_DESCRIPTION],
)
PVT_MODEL_COMPOSITIONAL_DEFINITION = case_description.PvtModelCompositionalDescription(
    equation_of_state_type=constants.EquationOfStateType.SoaveRedlichKwong,
    surface_tension_model_type=constants.SurfaceTensionType.Leechien,
    viscosity_model=constants.PVTCompositionalViscosityModel.LohrenzBrayClark,
    heavy_components=[HEAVY_COMPONENT_DESCRIPTION],
    light_components=[
        LIGH_COMPONENT_DESCRIPTION,
        LIGH_COMPONENT_DESCRIPTION_OVERWRITE_C3,
    ],
    fluids={"fluid_1": COMPOSITIONAL_FLUID_DESCRIPTION},
)
COMBINED_FLUID_DESCRIPTION = case_description.CombinedFluidDescription(
    pvt_model="acme",
)
PVT_MODEL_COMBINED_DEFINITION = case_description.PvtModelCombinedDescription(
    reference_pvt_model="acme",
    fluids={"combined_fluid_1": COMBINED_FLUID_DESCRIPTION},
)
PVT_MODEL_PT_TABLE_PARAMETERS = (
    case_description.PvtModelPtTableParametersDescription.create_constant(
        has_water=True
    )
)
PVT_MODEL_PH_TABLE_PARAMETERS = (
    case_description.PvtModelPhTableParametersDescription.create_constant(
        has_water=True
    )
)
PVT_MODEL_CONST_TABLE_DEFINITION = (
    case_description.PvtModelConstantPropertiesDescription()
)
PVT_MODELS_DEFINITION = case_description.PvtModelsDescription(
    default_model="acme",
    compositional={
        "composition 1": PVT_MODEL_COMPOSITIONAL_DEFINITION,
        "composition 2": PVT_MODEL_COMPOSITIONAL_DEFINITION,
    },
    combined={
        "combined 1": PVT_MODEL_COMBINED_DEFINITION,
    },
    correlations={
        "correlation 1": PVT_MODEL_CORRELATION_DEFINITION,
        "correlation 2": PVT_MODEL_CORRELATION_DEFINITION,
    },
    tables={"acme": get_acme_tab_file_path(), "gavea_2": get_acme_tab_file_path()},
    constant_properties={"constant 1": PVT_MODEL_CONST_TABLE_DEFINITION},
)

SPEED_CURVE_DESCRIPTION = case_description.SpeedCurveDescription(
    time=Array([0.0, 0.1], "s"), speed=Array([10.0, 50.0], "rpm")
)
COMPRESSOR_PRESSURE_TABLE_DESCRIPTION = (
    case_description.CompressorPressureTableDescription(
        speed_entries=Array(
            [25000.0, 25000.0, 25000.0, 50000.0, 50000.0, 50000.0], "rpm"
        ),
        corrected_mass_flow_rate_entries=Array([0.1, 0.2, 0.3, 0.1, 0.2, 0.3], "kg/s"),
        pressure_ratio_table=Array(
            [1.0, 1.0, 2.7, 2.5, 2.3, 1.8],
            "-",
        ),
        isentropic_efficiency_table=Array(
            [1.0, 1.0, 0.95, 0.95, 0.9, 0.85],
            "-",
        ),
    )
)
COMPRESSOR_DESCRIPTION = case_description.CompressorEquipmentDescription(
    position=Scalar(500.0, "m"),
    table=COMPRESSOR_PRESSURE_TABLE_DESCRIPTION,
    reference_pressure=Scalar(1.0, "bar"),
    reference_temperature=Scalar(25, "degC"),
    speed_curve=SPEED_CURVE_DESCRIPTION,
    constant_speed=Scalar(600, "rpm"),
    compressor_type=constants.CompressorSpeedType.ConstantSpeed,
    speed_curve_interpolation_type=constants.InterpolationType.Linear,
    flow_direction=constants.FlowDirection.Backward,
)
CV_TABLE_DESCRIPTION_SCHEMA = case_description.CvTableDescription(
    opening=Array([0.0, 0.2, 0.5, 1.0], "-"),
    flow_coefficient=Array([0.0, 7.16, 44.97, 180.68], "(galUS/min)/(psi^0.5)"),
)
CASING_SECTION_DESCRIPTION = case_description.CasingSectionDescription(
    name="Casing 1",
    hanger_depth=Scalar(1, "m"),
    settings_depth=Scalar(2, "m"),
    hole_diameter=Scalar("diameter", 2.0, "m"),
    outer_diameter=Scalar("diameter", 0.65, "m"),
    inner_diameter=Scalar("diameter", 0.6, "m"),
    inner_roughness=Scalar(0.0, "m"),
    material="Carbon Steel",
    top_of_filler=Scalar(0.0, "m"),
    filler_material="Cement",
    material_above_filler="Cement",
)
GAS_LIST_VALVE_DESCRIPTION = case_description.GasLiftValveEquipmentDescription(
    position=Scalar(800.0, "m"),
    diameter=Scalar("diameter", 1.0, "cm"),
    valve_type=constants.ValveType.CheckValve,
    delta_p_min=Scalar(4.0e6, "Pa"),
    discharge_coefficient=Scalar(0.826, "-"),
)
HEAT_SOURCE_DESCRIPTION = case_description.HeatSourceEquipmentDescription(
    start=Scalar(200.0, "m"),
    length=Scalar(550.0, "m"),
    power=Scalar(20.0e3, "W"),
    power_curve=Curve(
        Array("power", [2e4, 2.1e4, 2.3e4], "W"), Array("time", [0, 10, 20], "h")
    ),
)
INITIAL_CONDITIONS_DESCRIPTION = case_description.InitialConditionsDescription(
    pressures=case_builders.build_constant_initial_pressure_description(50.0, "bar"),
    velocities=case_builders.build_constant_initial_velocities_description(
        {
            constants.FLUID_GAS: Scalar(0.0, "m/s"),
            constants.FLUID_OIL: Scalar(0.0, "m/s"),
            constants.FLUID_WATER: Scalar(0, "m/s"),
        }
    ),
    volume_fractions=case_builders.build_constant_initial_volume_fractions_description(
        {
            constants.FLUID_GAS: Scalar("volume fraction", 0.999, "-"),
            constants.FLUID_OIL: Scalar("volume fraction", 0.001, "-"),
            constants.FLUID_WATER: Scalar("volume fraction", 0.0, "-"),
        }
    ),
    tracers_mass_fractions=case_builders.build_constant_initial_tracers_mass_fractions_description(
        [0.0, 1.0], "-"
    ),
    temperatures=case_builders.build_constant_initial_temperatures_description(
        123.4, "K"
    ),
    fluid="fluid_1",
)
MASS_SOURCE_DESCRIPTION = case_description.MassSourceEquipmentDescription(
    position=Scalar(10, "m"),
    gas_oil_ratio=Scalar(100.0, "sm3/sm3", get_category_for("sm3/sm3")),
    water_cut=Scalar(0.2, "-", "volume fraction"),
    volumetric_flow_rates_std_input_type=constants.MultiInputType.Constant,
    volumetric_flow_rates_std={
        "gas": Scalar(1000.5, "sm3/d"),
        "oil": Scalar(20.5, "sm3/d"),
        "water": Scalar(20.5, "sm3/d"),
    },
    volumetric_flow_rates_std_curve={
        "gas": Curve(Array([1000.5, 2000.5], "sm3/d"), Array([0, 3.5], "s")),
        "oil": Curve(Array([20.5, 30.5], "sm3/d"), Array([0, 2.0], "s")),
        "water": Curve(Array([20.5, 10.5], "sm3/d"), Array([0, 10], "s")),
    },
    tracer_mass_fraction=Array([1.0, 0.0], "-", "mass fraction"),
    temperature=Scalar(15, "degC"),
    fluid="fluid_1",
    source_type=constants.MassSourceType.MassFlowRates,
    mass_flow_rates_input_type=constants.MultiInputType.Constant,
    mass_flow_rates={
        constants.FLUID_GAS: Scalar(0.005, "kg/s"),
        constants.FLUID_OIL: Scalar(0.5, "kg/s"),
        constants.FLUID_WATER: Scalar(0.001, "kg/s"),
    },
    mass_flow_rates_curve={
        constants.FLUID_GAS: Curve(Array([0.005, 0.009], "kg/s"), Array([0, 5], "s")),
        constants.FLUID_OIL: Curve(Array([0.5, 0.3], "kg/s"), Array([0, 2], "s")),
        constants.FLUID_WATER: Curve(Array([0.001, 0.002], "kg/s"), Array([0, 7], "s")),
    },
)
MATERIAL_DESCRIPTION = case_description.MaterialDescription(
    name="Durepoxi",
    material_type=constants.MaterialType.Fluid,
    density=Scalar("density", 2900.0, "kg/m3"),
    heat_capacity=Scalar("specific heat capacity", 1000.0, "J/kg.degC"),
    thermal_conductivity=Scalar("thermal conductivity", 5.9, "W/m.degC"),
    inner_emissivity=Scalar("emissivity", 0.5, "-"),
    outer_emissivity=Scalar("emissivity", 0.5, "-"),
    expansion=Scalar("volumetric thermal expansion", 0.0001, "1/degC"),
    viscosity=Scalar("dynamic viscosity", 20, "cP"),
)
MASS_SOURCE_NODE_PROPERTIES_DESCRIPTION = (
    case_description.MassSourceNodePropertiesDescription(
        fluid="fluid_1",
        tracer_mass_fraction=Array([1.0, 0.0], "-", "mass fraction"),
        source_type=constants.MassSourceType.TotalMassFlowRatePvtSplit,
        total_mass_flow_rate_input_type=constants.MultiInputType.Constant,
        total_mass_flow_rate=Scalar(0.05, "kg/s"),
        volumetric_flow_rates_std={
            constants.FLUID_GAS: Scalar(10.0, "sm3/d"),
            constants.FLUID_OIL: Scalar(20, "sm3/d"),
            constants.FLUID_WATER: Scalar(50, "sm3/d"),
        },
        volumetric_flow_rates_std_curve={
            constants.FLUID_GAS: Curve(Array([10.0], "sm3/d"), Array([0], "s")),
            constants.FLUID_OIL: Curve(Array([20], "sm3/d"), Array([0], "s")),
            constants.FLUID_WATER: Curve(Array([50], "sm3/d"), Array([0], "s")),
        },
    )
)
NODE_MASS_SOURCE_DESCRIPTION = case_description.NodeDescription(
    name="mass_source_node",
    pvt_model="gavea",
    node_type=constants.NodeCellType.MassSource,
    mass_source_properties=MASS_SOURCE_NODE_PROPERTIES_DESCRIPTION,
)
SEPARATOR_NODE_PROPERTIES_DESCRIPTION = (
    case_description.SeparatorNodePropertiesDescription(
        environment_temperature=Scalar("temperature", 288.6, "K"),
        geometry=constants.SeparatorGeometryType.Sphere,
        length=Scalar(10.0, "m"),
        nozzles={
            "Pipe1": Scalar(2.0, "m"),
            "Pipe2": Scalar(4.0, "m"),
            "Pipe3": Scalar(0.0, "m"),
        },
        overall_heat_transfer_coefficient=Scalar(0.0, "W/m2.K"),
        diameter=Scalar("diameter", 4.0, "m"),
        initial_phase_volume_fractions={
            constants.FLUID_GAS: Scalar("volume fraction", 0.5, "-"),
            constants.FLUID_OIL: Scalar("volume fraction", 0.5, "-"),
            constants.FLUID_WATER: Scalar("volume fraction", 0.5, "-"),
        },
        gas_separation_efficiency=Scalar("dimensionless", 1.0, "-"),
        liquid_separation_efficiency=Scalar("dimensionless", 1.0, "-"),
    )
)
NODE_SEPARATOR_DESCRIPTION = case_description.NodeDescription(
    name="separator_node",
    node_type=constants.NodeCellType.Separator,
    pvt_model="gavea",
    separator_properties=SEPARATOR_NODE_PROPERTIES_DESCRIPTION,
)

PRESSURE_NODE_PROPERTIES_DESCRIPTION = (
    case_description.PressureNodePropertiesDescription(
        pressure=Scalar(10.0, "bar"),
        temperature=Scalar(343.0, "K"),
        fluid="fluid_1",
        tracer_mass_fraction=Array([1.0, 0.0], "-", "mass fraction"),
        gas_oil_ratio=Scalar(100.0, "sm3/sm3", get_category_for("sm3/sm3")),
        gas_liquid_ratio=Scalar(5.0, "sm3/sm3", get_category_for("sm3/sm3")),
        water_cut=Scalar(0.2, "-", "volume fraction"),
        split_type=constants.MassInflowSplitType.ConstantMassFraction,
        mass_fractions={
            constants.FLUID_GAS: Scalar("mass fraction", 0.1, "-"),
            constants.FLUID_OIL: Scalar("mass fraction", 0.2, "-"),
            constants.FLUID_WATER: Scalar("mass fraction", 0.3, "-"),
        },
        volume_fractions={
            constants.FLUID_GAS: Scalar("volume fraction", 0.4, "-"),
            constants.FLUID_OIL: Scalar("volume fraction", 0.5, "-"),
            constants.FLUID_WATER: Scalar("volume fraction", 0.6, "-"),
        },
    )
)
NODE_PRESSURE_DESCRIPTION = case_description.NodeDescription(
    name="pressure_node",
    node_type=constants.NodeCellType.Pressure,
    pvt_model="gavea",
    pressure_properties=PRESSURE_NODE_PROPERTIES_DESCRIPTION,
)

INTERNAL_NODE_PROPERTIES_DESCRIPTION = (
    case_description.InternalNodePropertiesDescription(fluid="fluid_1")
)

NODE_INTERNAL_DESCRIPTION = case_description.NodeDescription(
    name="internal_node",
    node_type=constants.NodeCellType.Internal,
    pvt_model="gavea",
    internal_properties=INTERNAL_NODE_PROPERTIES_DESCRIPTION,
)
PACKER_DESCRIPTION = case_description.PackerDescription(
    name="Packer 1",
    position=Scalar(1000.0, "m"),
    material_above="Adhesive Polypropylene",
)
OPEN_HOLE_DESCRIPTION = case_description.OpenHoleDescription(
    name="Open Hole 1",
    length=Scalar(101.0, "m"),
    diameter=Scalar("diameter", 102.0, "m"),
    inner_roughness=Scalar(103.0, "m"),
)
PIPE_WALL_DESCRIPTION = case_description.PipeSegmentsDescription(
    start_positions=Array([0.0, 300.0], "m"),
    diameters=Array([0.1, 0.1], "m"),
    roughnesses=Array([1e-5, 1e-5], "m"),
    wall_names=["Riser", "Flowline"],
)
PROFILE_OUTPUT_DESCRIPTION = case_description.ProfileOutputDescription(
    curve_names=["elevation"],
    element_name="pipe 1",
    location=constants.OutputAttachmentLocation.Main,
)
LINEAR_IPR_DESCRIPTION = case_description.LinearIPRDescription(
    well_index_phase=constants.WellIndexPhaseType.Oil,
    min_pressure_difference=Scalar(0.0, "bar"),
    well_index=Scalar(1.0e-6, "m3/Pa.s"),
    well_index_curve=Curve(Array([1.0e-6, 0.9e-6], "m3/Pa.s"), Array([0, 1], "h")),
)
VOGEL_IPR_DESCRIPTION = case_description.VogelIPRDescription(
    well_index_phase=constants.WellIndexPhaseType.Oil,
    min_pressure_difference=Scalar(1.0e-6, "bar"),
    well_max_flow_rate=Scalar(1.0e-6, "sm3/d"),
    well_max_flow_rate_curve=Curve(
        Array([1.0e-6, 0.9e-6], "sm3/d"), Array([0, 1], "s")
    ),
)
FETKOVICH_IPR_DESCRIPTION = case_description.FetkovichIPRDescription(
    well_index_phase=constants.WellIndexPhaseType.Oil,
    min_pressure_difference=Scalar(1.0e-6, "bar"),
    bubble_point_pressure=Scalar(1.0e-6, "bar"),
    well_index=Scalar(1.0e-6, "m3/Pa.s"),
    well_index_curve=Curve(Array([1.0e-6, 0.9e-6], "m3/Pa.s"), Array([0, 1], "h")),
)
FORCHHEIMER_IPR_DESCRIPTION = case_description.ForchheimerIPRDescription(
    well_index_phase=constants.WellIndexPhaseType.Gas,
    min_pressure_difference=Scalar(1.0e-6, "bar"),
    calculate_coeff_option=constants.ForchheimerCoefficientsOption.ReservoirParameters,
    gas_viscosity=Scalar("dynamic viscosity", 1.0e-6, "Pa.s"),
    gas_z_factor=Scalar("dimensionless", 1.0e-6, "-"),
    reservoir_permeability=Scalar("permeability rock", 1.0e-6, "m2"),
    drainage_radius=Scalar("length", 1.0e-6, "m"),
    well_radius=Scalar("length", 1.0e-6, "m"),
    well_skin_factor=Scalar("dimensionless", 1.0e-6, "-"),
    non_darcy_parameter=Scalar("nonDarcy flow coefficient", 1.0e-6, "Pa.s/m6"),
)
IPR_CURVE_DESCRIPTION = case_description.IPRCurveDescription(
    pressure_difference=Array([0.0, 43.41, 62.19, 85.00], "Pa"),
    flow_rate=Array([0.0, 0.87, 2.07, 2.305], "MMscf/d"),
)
TABLE_IPR_DESCRIPTION = case_description.TableIPRDescription(
    well_index_phase=constants.WellIndexPhaseType.Gas, table=IPR_CURVE_DESCRIPTION
)
IPR_MODELS_DESCRIPTION = case_description.IPRModelsDescription(
    linear_models={"Linear IPR 1": LINEAR_IPR_DESCRIPTION},
    table_models={"Table IPR 1": TABLE_IPR_DESCRIPTION},
    vogel_models={"Vogel IPR 1": VOGEL_IPR_DESCRIPTION},
    fetkovich_models={"Fetkovich IPR 1": FETKOVICH_IPR_DESCRIPTION},
    forchheimer_models={"Forchheimer IPR 1": FORCHHEIMER_IPR_DESCRIPTION},
)
RESERVOIR_INFLOW_DESCRIPTION = case_description.ReservoirInflowEquipmentDescription(
    start=Scalar(50.0, "m"),
    length=Scalar(150.0, "m"),
    pressure=Scalar(12.0, "bar"),
    pressure_curve=Curve(Array([12.1, 13.7], "bar"), Array([0, 11], "s")),
    temperature_input_type=constants.MultiInputType.Curve,
    temperature=Scalar(50.0, "degC"),
    temperature_curve=Curve(Array([50.0], "degC"), Array([0], "s")),
    productivity_ipr="Table IPR 1",
    injectivity_ipr="Linear IPR 1",
    split_type=constants.MassInflowSplitType.Pvt,
    water_cut=Scalar(0.2, "-", "volume fraction"),
    gas_oil_ratio=Scalar(100.0, "sm3/sm3", get_category_for("sm3/sm3")),
    mass_fractions={
        constants.FLUID_GAS: Scalar("mass fraction", 0.4, "-"),
        constants.FLUID_OIL: Scalar("mass fraction", 0.6, "-"),
        constants.FLUID_WATER: Scalar("mass fraction", 0.8, "-"),
    },
    tracer_mass_fraction=Array("mass fraction", [1.0, 0.0], "-"),
    fluid="fluid_1",
)
TABLE_PUMP_DESCRIPTION = case_description.TablePumpDescription(
    speeds=Array([0.0] * 4 + [500.0] * 4, "rpm"),
    void_fractions=Array([0.0] * 4 + [0.1] * 4, "-"),
    flow_rates=Array([1.0] * 4 + [0.05] * 4, "m3/s"),
    pressure_boosts=Array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0], "bar"),
    heads=Array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0], "m") * 1.0e5 / (9.8 * 1000.0),
    efficiencies=Array([0.01, 0.2, 0.4, 0.2, 0.009, 0.18, 0.36, 0.18], "-"),
    powers=Array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0], "W"),
)
SURGE_VOLUME_OPTIONS_DESCRIPTION = case_description.SurgeVolumeOptionsDescription(
    time_mode=constants.SurgeVolumeTimeMode.UserDefined,
    start_time=Scalar(10, "s"),
    end_time=Scalar(100, "s"),
    drainage_mode=constants.DrainageRateMode.UserDefined,
    maximum_drainage_rate=Scalar(1, "m3/s"),
)
POSITIONAL_PIPE_TREND_OUTPUT_DESCRIPTION = (
    case_description.PositionalPipeTrendDescription(
        curve_names=["oil mass flow rate"],
        element_name="pipe 1",
        position=Scalar(2950.0, "m"),
        location=constants.OutputAttachmentLocation.Main,
        surge_volume_options=SURGE_VOLUME_OPTIONS_DESCRIPTION,
    )
)
GLOBAL_TREND_OUTPUT_DESCRIPTION = case_description.GlobalTrendDescription(
    curve_names=["timestep"],
)
EQUIPMENT_TREND_OUTPUT_DESCRIPTION = case_description.EquipmentTrendDescription(
    curve_names=["mass source temperature"],
    element_name="MASS SOURCE",
)
OVERALL_PIPE_TREND_OUTPUT_DESCRIPTION = case_description.OverallPipeTrendDescription(
    curve_names=["pipe total liquid volume"],
    element_name="pipe 1",
    location=constants.OutputAttachmentLocation.Main,
)
SEPARATOR_TREND_OUTPUT_DESCRIPTION = case_description.SeparatorTrendDescription(
    curve_names=["separator liquid level"],
    element_name="separator_node",
)
CONTROLLER_TREND_OUTPUT_DESCRIPTION = case_description.ControllerTrendDescription(
    curve_names=["controller output signal"],
    element_name="controller_node",
)
TRENDS_OUTPUT_DESCRIPTION = case_description.TrendsOutputDescription(
    positional_pipe_trends=[POSITIONAL_PIPE_TREND_OUTPUT_DESCRIPTION],
    equipment_trends=[EQUIPMENT_TREND_OUTPUT_DESCRIPTION],
    overall_pipe_trends=[OVERALL_PIPE_TREND_OUTPUT_DESCRIPTION],
    global_trends=[GLOBAL_TREND_OUTPUT_DESCRIPTION],
    separator_trends=[SEPARATOR_TREND_OUTPUT_DESCRIPTION],
    controller_trends=[CONTROLLER_TREND_OUTPUT_DESCRIPTION],
)
TUBING_DESCRIPTION = case_description.TubingDescription(
    name="Tubing 1",
    length=Scalar(42, "m"),
    outer_diameter=Scalar("diameter", 0.35, "m"),
    inner_diameter=Scalar("diameter", 0.3, "m"),
    inner_roughness=Scalar(0.0, "m"),
    material="Carbon Steel",
)
WALL_LAYER_DESCRIPTION = case_description.WallLayerDescription(
    thickness=Scalar(25.4, "mm"), material_name="Carbon Steel", has_annulus_flow=True
)
CASE_OUTPUT_DESCRIPTION = case_description.CaseOutputDescription(
    trends=TRENDS_OUTPUT_DESCRIPTION,
    automatic_trend_frequency=True,
    trend_frequency=Scalar(0.1, "s"),
    profiles=[PROFILE_OUTPUT_DESCRIPTION],
    automatic_profile_frequency=True,
    profile_frequency=Scalar(0.1, "s"),
)
CASING_DESCRIPTION = case_description.CasingDescription(
    casing_sections=[CASING_SECTION_DESCRIPTION],
    tubings=[TUBING_DESCRIPTION],
    packers=[PACKER_DESCRIPTION],
    open_holes=[OPEN_HOLE_DESCRIPTION],
)
PIG_DESCRIPTION = case_description.PigEquipmentDescription(
    position=Scalar(120.0, "m"),
    launch_times=Array([0.0, 50.0], "s"),
    diameter=Scalar("diameter", 0.02, "m"),
    mass_input_type=constants.MultiInputType.Curve,
    mass=Scalar(50.0, "kg"),
    mass_curve=Curve(Array([50.0], "kg"), Array([0], "s")),
    static_force_input_type=constants.MultiInputType.Curve,
    static_force=Scalar(60, "N"),
    static_force_curve=Curve(Array([60.0], "N"), Array([0], "s")),
    wall_friction_input_type=constants.MultiInputType.Curve,
    wall_friction=Scalar(70, "N.s/m"),
    wall_friction_curve=Curve(Array([70.0], "N.s/m"), Array([0], "s")),
    linear_friction_input_type=constants.MultiInputType.Curve,
    linear_friction=Scalar(80, "N.s/m"),
    linear_friction_curve=Curve(Array([80.0], "N.s/m"), Array([0], "s")),
    quadratic_friction_input_type=constants.MultiInputType.Curve,
    quadratic_friction=Scalar(90, "N.s2/m2"),
    quadratic_friction_curve=Curve(Array([90.0], "N.s2/m2"), Array([0], "s")),
    trap_mode=constants.PigTrappingMode.UserDefined,
    trap_pipe_name="pipe 1",
    trap_position=Scalar(40, "m"),
    route_mode=constants.PigRoutingMode.Automatic,  # Not using UserDefined for the filled case.
    pipe_route_names=None,
)
PUMP_DESCRIPTION = case_description.PumpEquipmentDescription(
    type=constants.PumpType.TableInterpolation,
    position=Scalar(350.0, "m"),
    flow_direction=constants.FlowDirection.Forward,
    pressure_boost=Scalar(1e5, "Pa"),
    thermal_efficiency=Scalar(100, "%"),
    thermal_efficiency_model=constants.PumpThermalEfficiencyModel.Constant,
    table=TABLE_PUMP_DESCRIPTION,
    speed_curve=SPEED_CURVE_DESCRIPTION,
    speed_curve_interpolation_type=constants.InterpolationType.Linear,
    esp_table=TABLE_PUMP_DESCRIPTION,
    esp_speed_input_type=constants.MultiInputType.Curve,
    esp_speed=Scalar(60.0, "Hz", "angle per time"),
    esp_speed_curve=Curve(
        Array([0.0, 60.0], "Hz", "angle per time"), Array([0.0, 100.0], "s")
    ),
    esp_number_of_stages=2,
    esp_reference_density=Scalar(1000.0, "kg/m3"),
    density_correction_enabled=False,
    esp_manufacturer="",
    esp_model="",
)
VALVE_DESCRIPTION = case_description.ValveEquipmentDescription(
    position=Scalar(100.0, "m"),
    diameter=Scalar("diameter", 0.01, "m"),
    flow_direction=constants.FlowDirection.Backward,
    type=constants.ValveType.ChokeValveWithFlowCoefficient,
    cv_table=CV_TABLE_DESCRIPTION_SCHEMA,
    opening_type=constants.ValveOpeningType.TableInterpolation,
    opening_curve_interpolation_type=constants.InterpolationType.Linear,
    opening_curve=Curve(Array([0.1, 0.2, 0.2], "-"), Array([0.0, 0.1, 0.5], "s")),
)
VALVE_DESCRIPTION_CONSTANT_OPENING = case_description.ValveEquipmentDescription(
    position=Scalar(100.0, "m"),
    diameter=Scalar("diameter", 0.01, "m"),
    flow_direction=constants.FlowDirection.Backward,
    type=constants.ValveType.ChokeValveWithFlowCoefficient,
    cv_table=CV_TABLE_DESCRIPTION_SCHEMA,
    opening_type=constants.ValveOpeningType.ConstantOpening,
    opening=Scalar("dimensionless", 42, "%"),
)
WALL_DESCRIPTION = case_description.WallDescription(
    name="Flowline",
    inner_roughness=Scalar(1, "mm"),
    wall_layer_container=[WALL_LAYER_DESCRIPTION, WALL_LAYER_DESCRIPTION],
)
LEAK_EQUIPMENT_DESCRIPTION = case_description.LeakEquipmentDescription(
    position=Scalar(350.0, "m"),
    diameter=Scalar("diameter", 0.025, "m"),
    discharge_coefficient=Scalar(0.825, "-"),
    location=LeakLocation.Main,
    target_pipe_name=None,
    target_position=Scalar(20.0, "m"),
    target_location=LeakLocation.Main,
    backflow=True,
)
EQUIPMENT_DESCRIPTION = case_description.EquipmentDescription(
    mass_sources={"MASS SOURCE": MASS_SOURCE_DESCRIPTION},
    pumps={"PUMP": PUMP_DESCRIPTION},
    valves={
        "VALVE": VALVE_DESCRIPTION,
        "VALVE CONSTANT OPENING": VALVE_DESCRIPTION_CONSTANT_OPENING,
    },
    reservoir_inflows={"RESERVOIR": RESERVOIR_INFLOW_DESCRIPTION},
    heat_sources={"HEAT": HEAT_SOURCE_DESCRIPTION},
    compressors={"COMPRESSOR": COMPRESSOR_DESCRIPTION},
    pigs={"PIG": PIG_DESCRIPTION},
    leaks={"LEAK": LEAK_EQUIPMENT_DESCRIPTION},
)
ANNULUS_EQUIPMENT_DESCRIPTION = case_description.AnnulusEquipmentDescription(
    leaks={"ANNULUS LEAK": LEAK_EQUIPMENT_DESCRIPTION},
    gas_lift_valves={"GAS LIFT VALVE": GAS_LIST_VALVE_DESCRIPTION},
)
ANNULUS_DESCRIPTION = case_description.AnnulusDescription(
    has_annulus_flow=True,
    pvt_model="gavea",
    top_node="mass_source_node",
    initial_conditions=INITIAL_CONDITIONS_DESCRIPTION,
    equipment=ANNULUS_EQUIPMENT_DESCRIPTION,
)
ENVIRONMENT_PROPERTY_DESCRIPTION = case_description.EnvironmentPropertyDescription(
    position=Scalar(1, "m"),
    temperature=Scalar(1, "degC"),
    type=constants.PipeEnvironmentHeatTransferCoefficientModelType.WallsAndEnvironment,
    heat_transfer_coefficient=Scalar(1.0e50, "W/m2.K"),
    overall_heat_transfer_coefficient=Scalar(2, "W/m2.K"),
    fluid_velocity=Scalar(1, "m/s"),
)
ENVIRONMENT_DESCRIPTION = case_description.EnvironmentDescription(
    thermal_model=constants.PipeThermalModelType.SteadyState,
    reference_y_coordinate=Scalar(5.0, "m"),
    position_input_mode=constants.PipeThermalPositionInput.Tvd,
    md_properties_table=[ENVIRONMENT_PROPERTY_DESCRIPTION],
    tvd_properties_table=[ENVIRONMENT_PROPERTY_DESCRIPTION],
)

X_AND_Y_DESCRIPTION = case_description.XAndYDescription(
    x=Array([1, 2, 3], "m"), y=Array([4, 5, 6], "m")
)

PROFILE_DESCRIPTION_WITH_XY = case_description.ProfileDescription(
    x_and_y=X_AND_Y_DESCRIPTION
)
PIPE_DESCRIPTION = case_description.PipeDescription(
    environment=ENVIRONMENT_DESCRIPTION,
    equipment=EQUIPMENT_DESCRIPTION,
    initial_conditions=INITIAL_CONDITIONS_DESCRIPTION,
    name="pipe 1",
    profile=PROFILE_DESCRIPTION_WITH_XY,
    pvt_model="gavea",
    segments=PIPE_WALL_DESCRIPTION,
    source="mass_source_node",
    target="pressure_node",
)
FORMATION_LAYER_DESCRIPTION = case_description.FormationLayerDescription(
    name="f", start=Scalar(1, "m"), material="Carbon Steel"
)
FORMATION_LAYER_DESCRIPTION_1 = case_description.FormationLayerDescription(
    name="f (1)", start=Scalar(1, "m"), material="Carbon Steel"
)
FORMATION_DESCRIPTION = case_description.FormationDescription(
    reference_y_coordinate=Scalar(1, "m"),
    layers=[FORMATION_LAYER_DESCRIPTION, FORMATION_LAYER_DESCRIPTION_1],
)

LENGTH_AND_ELEVATION_DESCRIPTION = case_description.LengthAndElevationDescription(
    length=Array([0, 1, 2], "m"), elevation=Array([0, 0.5, 1], "m")
)
PROFILE_DESCRIPTION_WITH_LENGTH_AND_ELEVATION_DESCRIPTION = (
    case_description.ProfileDescription(
        length_and_elevation=LENGTH_AND_ELEVATION_DESCRIPTION
    )
)
WELL_DESCRIPTION = case_description.WellDescription(
    name="Wellbore",
    pvt_model="gavea",
    stagnant_fluid="Lift Gas",
    profile=PROFILE_DESCRIPTION_WITH_LENGTH_AND_ELEVATION_DESCRIPTION,
    casing=CASING_DESCRIPTION,
    annulus=ANNULUS_DESCRIPTION,
    formation=FORMATION_DESCRIPTION,
    top_node="mass_source_node",
    bottom_node="pressure_node",
    environment=ENVIRONMENT_DESCRIPTION,
    initial_conditions=INITIAL_CONDITIONS_DESCRIPTION,
    equipment=EQUIPMENT_DESCRIPTION,
)
TIME_OPTIONS_DESCRIPTION = case_description.TimeOptionsDescription(
    stop_on_steady_state=True,
    initial_time=Scalar(1, "s"),
    final_time=Scalar(2, "s"),
    initial_timestep=Scalar(3, "s"),
    minimum_timestep=Scalar(4, "s"),
    maximum_timestep=Scalar(5, "s"),
    restart_autosave_frequency=Scalar(6, "s"),
    minimum_time_for_steady_state_stop=Scalar(7, "s"),
)

PHYSICS_DESCRIPTION = case_description.PhysicsDescription(
    hydrodynamic_model=constants.HydrodynamicModelType.ThreeLayersNineFieldsGasOilWater,
    simulation_regime=constants.SimulationRegimeType.SteadyState,
    energy_model=constants.EnergyModel.LayersModel,
    solids_model=constants.SolidsModelType.Mills1985Equilibrium,
    initial_condition_strategy=constants.InitialConditionStrategyType.SteadyState,
    restart_filepath=Path(__file__),
    keep_former_results=True,
    correlations_package=constants.CorrelationPackageType.Alfasim,
    emulsion_model_enabled=True,
    emulsion_relative_viscosity_model=constants.EmulsionRelativeViscosityModelType.Brinkman1952,
    emulsion_relative_viscosity_tuning_factor=Curve(
        image=Array([1.0, 1.5, 2.0, 1.0], "-"),
        domain=Array([0.0, 0.4, 0.6, 1.0], "m3/m3"),
    ),
    emulsion_droplet_size_model=constants.EmulsionDropletSizeModelType.Brauner2001,
    emulsion_inversion_point_model=constants.EmulsionInversionPointModelType.Brinkman1952AndYeh1964,
    flash_model=constants.FlashModel.HydrocarbonOnly,
)

NUMERICAL_OPTIONS_DESCRIPTION = case_description.NumericalOptionsDescription(
    tolerance=0.0,
    maximum_iterations=42,
    maximum_timestep_change_factor=4,
    maximum_cfl_value=2,
    relaxed_tolerance=42.42,
    divergence_tolerance=5.5,
    nonlinear_solver_type=constants.NonlinearSolverType.AlfasimQuasiNewton,
    friction_factor_evaluation_strategy=constants.EvaluationStrategyType.NewtonExplicit,
    simulation_mode=constants.SimulationModeType.Robust,
    enable_solver_caching=False,
    caching_rtol=3e-3,
    caching_atol=4e-4,
    always_repeat_timestep=False,
    enable_fast_compositional=True,
)
TRACER_MODEL_CONSTANT_COEFFICIENTS_DESCRIPTION = (
    case_description.TracerModelConstantCoefficientsDescription(
        partition_coefficients={
            "gas": Scalar("mass fraction", 0.1, "kg/kg"),
            "oil": Scalar("mass fraction", 0.2, "kg/kg"),
            "water": Scalar("mass fraction", 0.3, "kg/kg"),
        }
    )
)
TRACERS_DESCRIPTION = case_description.TracersDescription(
    constant_coefficients={
        "Tracer 0": TRACER_MODEL_CONSTANT_COEFFICIENTS_DESCRIPTION,
        "Tracer 1": TRACER_MODEL_CONSTANT_COEFFICIENTS_DESCRIPTION,
    }
)

ALFASIM_VERSION_INFO = case_description.AlfasimVersionInfo(
    platform="linux64",
    version="2024.1",
    revision="0123456789abcdef",
    date="2024-04-02 12:00",
)

CASE = case_description.CaseDescription(
    name="divergent_pipes",
    time_options=TIME_OPTIONS_DESCRIPTION,
    physics=PHYSICS_DESCRIPTION,
    numerical_options=NUMERICAL_OPTIONS_DESCRIPTION,
    ipr_models=IPR_MODELS_DESCRIPTION,
    pvt_models=PVT_MODELS_DEFINITION,
    tracers=TRACERS_DESCRIPTION,
    outputs=CASE_OUTPUT_DESCRIPTION,
    pipes=[PIPE_DESCRIPTION],
    nodes=[
        NODE_MASS_SOURCE_DESCRIPTION,
        NODE_PRESSURE_DESCRIPTION,
        NODE_SEPARATOR_DESCRIPTION,
        NODE_INTERNAL_DESCRIPTION,
    ],
    wells=[WELL_DESCRIPTION],
    materials=[MATERIAL_DESCRIPTION],
    walls=[WALL_DESCRIPTION],
)
REFERENCED_VOLUME_FRACTIONS_CONTAINER_DESCRIPTION = (
    case_description.ReferencedVolumeFractionsContainerDescription(
        reference_coordinate=Scalar(1.0, "m"),
        positions=Array([1.0, 2.0, 3.0], "m"),
        fractions={
            constants.FLUID_GAS: Array([0.5, 0.5], "-"),
            constants.FLUID_OIL: Array([0.4, 0.6], "-"),
            constants.FLUID_WATER: Array([0.7, 0.3], "-"),
        },
    )
)
VOLUME_FRACTIONS_CONTAINER_DESCRIPTION = (
    case_description.VolumeFractionsContainerDescription(
        positions=Array([111.0, 222.0, 333.0], "m"),
        fractions={
            constants.FLUID_GAS: Array([0.91, 0.11], "-"),
            constants.FLUID_OIL: Array([0.82, 0.22], "-"),
            constants.FLUID_WATER: Array([0.53, 0.53], "-"),
        },
    )
)
INITIAL_FRACTIONS_DESCRIPTION = case_description.InitialVolumeFractionsDescription(
    position_input_type=constants.TableInputType.vertical_position,
    table_x=REFERENCED_VOLUME_FRACTIONS_CONTAINER_DESCRIPTION,
    table_y=REFERENCED_VOLUME_FRACTIONS_CONTAINER_DESCRIPTION,
    table_length=VOLUME_FRACTIONS_CONTAINER_DESCRIPTION,
)
REFERENCED_PRESSURE_CONTAINER_DESCRIPTION = (
    case_description.ReferencedPressureContainerDescription(
        reference_coordinate=Scalar(1.0, "m"),
        positions=Array([1.0, 2.0, 3.0], "m"),
        pressures=Array([33.0, 22.0, 11.0], "Pa"),
    )
)
PRESSURE_CONTAINER_DESCRIPTION = case_description.PressureContainerDescription(
    positions=Array([111.0, 222.0, 333.0], "m"),
    pressures=Array([3333.0, 2222.0, 1111.0], "Pa"),
)
INITIAL_PRESSURES_DESCRIPTION = case_description.InitialPressuresDescription(
    position_input_type=constants.TableInputType.horizontal_position,
    table_x=REFERENCED_PRESSURE_CONTAINER_DESCRIPTION,
    table_y=REFERENCED_PRESSURE_CONTAINER_DESCRIPTION,
    table_length=PRESSURE_CONTAINER_DESCRIPTION,
)
REFERENCED_VELOCITIES_CONTAINER_DESCRIPTION = (
    case_description.ReferencedVelocitiesContainerDescription(
        reference_coordinate=Scalar(1.0, "m"),
        positions=Array([1.0, 2.0, 3.0], "m"),
        velocities={
            constants.FLUID_GAS: Array([0.5, 0.5], "m/s"),
            constants.FLUID_OIL: Array([0.4, 0.6], "m/s"),
            constants.FLUID_WATER: Array([0.7, 0.3], "m/s"),
        },
    )
)
VELOCITIES_CONTAINER_DESCRIPTION = case_description.VelocitiesContainerDescription(
    positions=Array([111.0, 222.0, 333.0], "m"),
    velocities={
        constants.FLUID_GAS: Array([0.91, 0.11], "m/s"),
        constants.FLUID_OIL: Array([0.82, 0.22], "m/s"),
        constants.FLUID_WATER: Array([0.53, 0.53], "m/s"),
    },
)
INITIAL_VELOCITIES_DESCRIPTION = case_description.InitialVelocitiesDescription(
    position_input_type=constants.TableInputType.vertical_position,
    table_x=REFERENCED_VELOCITIES_CONTAINER_DESCRIPTION,
    table_y=REFERENCED_VELOCITIES_CONTAINER_DESCRIPTION,
    table_length=VELOCITIES_CONTAINER_DESCRIPTION,
)
REFERENCED_TEMPERATURES_CONTAINER_DESCRIPTION = (
    case_description.ReferencedTemperaturesContainerDescription(
        reference_coordinate=Scalar(1.0, "m"),
        positions=Array([1.0, 2.0, 3.0], "m"),
        temperatures=Array([0.5, 0.5, 0.5], "degC"),
    )
)
TEMPERATURES_CONTAINER_DESCRIPTION = case_description.TemperaturesContainerDescription(
    positions=Array([111.0, 222.0, 333.0], "m"),
    temperatures=Array([11.5, 12.5, 13.5], "degC"),
)
INITIAL_TEMPERATURES_DESCRIPTION = case_description.InitialTemperaturesDescription(
    position_input_type=constants.TableInputType.vertical_position,
    table_x=REFERENCED_TEMPERATURES_CONTAINER_DESCRIPTION,
    table_y=REFERENCED_TEMPERATURES_CONTAINER_DESCRIPTION,
    table_length=TEMPERATURES_CONTAINER_DESCRIPTION,
)
REFERENCED_TRACERS_MASS_FRACTIONS_CONTAINER_DESCRIPTION = (
    case_description.ReferencedTracersMassFractionsContainerDescription(
        reference_coordinate=Scalar(1.0, "m"),
        positions=Array([1.0, 2.0, 3.0], "m"),
        tracers_mass_fractions=[
            Array([0.5, 0.5], "-"),
            Array([0.4, 0.6], "-"),
            Array([0.7, 0.3], "-"),
        ],
    )
)
TRACERS_MASS_FRACTIONS_CONTAINER_DESCRIPTION = (
    case_description.TracersMassFractionsContainerDescription(
        positions=Array([1.0, 2.0, 3.0], "m"),
        tracers_mass_fractions=[
            Array([0.5, 0.5], "-"),
            Array([0.4, 0.6], "-"),
            Array([0.7, 0.3], "-"),
        ],
    )
)
INITIAL_TRACERS_MASS_FRACTIONS_DESCRIPTION = (
    case_description.InitialTracersMassFractionsDescription(
        position_input_type=constants.TableInputType.vertical_position,
        table_x=REFERENCED_TRACERS_MASS_FRACTIONS_CONTAINER_DESCRIPTION,
        table_y=REFERENCED_TRACERS_MASS_FRACTIONS_CONTAINER_DESCRIPTION,
        table_length=TRACERS_MASS_FRACTIONS_CONTAINER_DESCRIPTION,
    )
)


PIG_DESCRIPTION = case_description.PigEquipmentDescription(
    position=Scalar(120.0, "m"),
    launch_times=Array([0.0, 50.0], "s"),
    diameter=Scalar("diameter", 0.02, "m"),
    mass_input_type=constants.MultiInputType.Curve,
    mass=Scalar(50.0, "kg"),
    mass_curve=Curve(Array([50.0], "kg"), Array([0], "s")),
    static_force_input_type=constants.MultiInputType.Curve,
    static_force=Scalar(60, "N"),
    static_force_curve=Curve(Array([60.0], "N"), Array([0], "s")),
    wall_friction_input_type=constants.MultiInputType.Curve,
    wall_friction=Scalar(70, "N.s/m"),
    wall_friction_curve=Curve(Array([70.0], "N.s/m"), Array([0], "s")),
    linear_friction_input_type=constants.MultiInputType.Curve,
    linear_friction=Scalar(80, "N.s/m"),
    linear_friction_curve=Curve(Array([80.0], "N.s/m"), Array([0], "s")),
    quadratic_friction_input_type=constants.MultiInputType.Curve,
    quadratic_friction=Scalar(90, "N.s2/m2"),
    quadratic_friction_curve=Curve(Array([90.0], "N.s2/m2"), Array([0], "s")),
    trap_mode=constants.PigTrappingMode.UserDefined,
    trap_pipe_name="pipe 1",
    trap_position=Scalar(40, "m"),
    route_mode=constants.PigRoutingMode.Automatic,  # Not using UserDefined for the filled case.
    pipe_route_names=None,
)

CONTROLLER_INPUT_SIGNAL_PROPERTIES_DESCRIPTION = (
    case_description.ControllerInputSignalPropertiesDescription(
        target_variable="pressure",
        input_trend_name="Output Options > TrendOutDefinition",
        unit="bar",
    )
)

CONTROLLER_OUTPUT_SIGNAL_PROPERTIES_DESCRIPTION = (
    case_description.ControllerOutputSignalPropertiesDescription(
        controlled_property="opening",
        unit="%",
        network_element_name="VALVE",
        min_value=0.0,
        max_value=1.0,
        max_rate_of_change=1.0,
    )
)

CONTROLLER_NODE_PROPERTIES_DESCRIPTION = (
    case_description.ControllerNodePropertiesDescription(
        type=constants.ControllerType.PID,
        gain=1e-4,
        setpoint=1.0,
        integral_time=Scalar(1, "s"),
        derivative_time=Scalar(1, "s"),
        input_signal_properties=CONTROLLER_INPUT_SIGNAL_PROPERTIES_DESCRIPTION,
        output_signal_properties=CONTROLLER_OUTPUT_SIGNAL_PROPERTIES_DESCRIPTION,
    )
)

NODE_CONTROLLER_DESCRIPTION = case_description.NodeDescription(
    name="controller_node",
    node_type=constants.NodeCellType.Controller,
    controller_properties=CONTROLLER_NODE_PROPERTIES_DESCRIPTION,
)


PLUGIN_DESCRIPTION = case_description.PluginDescription(
    name="user_plugin",
    is_enabled=False,
    gui_models={},
)


def ensure_descriptions_are_equal(
    expected_case_description_dict,
    obtained_description_dict,
    ignored_properties,
    path="",
):
    """
    Check that two cases description are equals.
    """
    from more_itertools import first

    if path:
        path += "."

    for key, expected_value in expected_case_description_dict.items():
        if key in ignored_properties:
            continue
        if isinstance(expected_value, dict):
            ensure_descriptions_are_equal(
                expected_case_description_dict=expected_value,
                obtained_description_dict=obtained_description_dict[key],
                ignored_properties=ignored_properties,
                path=f"{path}{key}",
            )
            continue

        is_list = isinstance(expected_value, list)
        if is_list and isinstance(first(expected_value, None), dict):
            for index, value in enumerate(expected_value):
                ensure_descriptions_are_equal(
                    expected_case_description_dict=value,
                    obtained_description_dict=obtained_description_dict[key][index],
                    ignored_properties=ignored_properties,
                    path=f"{path}{key}[{index}]",
                )
            continue

        is_ndarray = isinstance(expected_value, np.ndarray)
        if is_ndarray or (
            is_list and isinstance(first(expected_value, None), np.ndarray)
        ):
            assert np.array_equal(obtained_description_dict[key], expected_value), (
                f"Not equal on {path}{key}"
            )
            continue  # pragma no cover [bug on coverage.py: https://github.com/nedbat/coveragepy/issues/198]

        is_array = isinstance(expected_value, Array)
        if is_array:
            unit = expected_value.GetUnit()
            obtained_values = np.array(obtained_description_dict[key].GetValues(unit))
            expected_values = np.array(expected_value.GetValues(unit))
            assert np.allclose(obtained_values, expected_values), (
                f"Not equal on {path}{key}\nObtained={obtained_values} != {expected_values}"
            )
            continue  # pragma no cover [bug on coverage.py

        is_curve = isinstance(expected_value, Curve)
        if is_curve:
            obtained_curve = obtained_description_dict[key]
            domain_unit = expected_value.GetDomain().GetUnit()
            expected_domain_values = expected_value.GetDomain().GetValues(domain_unit)
            obtained_domain_values = obtained_curve.GetDomain().GetValues(domain_unit)
            assert np.allclose(expected_domain_values, obtained_domain_values), (
                f"Not equal on {path}{key}\nObtained={obtained_values} != {expected_values}"
            )
            image_unit = expected_value.GetImage().GetUnit()
            expected_image_values = expected_value.GetImage().GetValues(image_unit)
            obtained_image_values = obtained_curve.GetImage().GetValues(image_unit)
            assert np.allclose(expected_image_values, obtained_image_values), (
                f"Not equal on {path}{key}\nObtained={obtained_values} != {expected_values}"
            )
            continue  # pragma no cover [bug on coverage.py: https://github.com/nedbat/coveragepy/issues/198]

        # Skip the check when materials or walls only has defaults values
        if key in ("materials", "walls") and first(expected_value, None) is None:
            continue

        assert obtained_description_dict[key] == expected_value, (
            f'Not equal on {path}{key}\nAttribute "{key}" doesn\'t match, obtained "{obtained_description_dict[key]}" while "{expected_value}" was expected.'
        )
