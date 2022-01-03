# fmt: off
# #[[[cog
# import cog
# from alfasim_sdk import CaseDescription
# from alfasim_sdk._internal.alfacase.generate_schema import get_all_classes_that_needs_schema, generate_alfacase_schema
# cog.out("from strictyaml import Bool, Enum, Int, Map, MapPattern, Optional, Seq, Str, Float # noreorder")
# cog.out("\n\n")
# cog.out("\n\n")
# list_of_classes_that_needs_schema = get_all_classes_that_needs_schema(CaseDescription)
# for class_ in list_of_classes_that_needs_schema:
#    cog.out(generate_alfacase_schema(class_))
# ]]]
from strictyaml import Bool, Enum, Int, Map, MapPattern, Optional, Seq, Str, Float # noreorder



bip_description_schema = Map(
    {
        "component_1": Str(),
        "component_2": Str(),
        "value": Float(),
    }
)
casing_section_description_schema = Map(
    {
        "name": Str(),
        "hanger_depth": Map({"value": Float(), "unit": Str()}),
        "settings_depth": Map({"value": Float(), "unit": Str()}),
        "hole_diameter": Map({"value": Float(), "unit": Str()}),
        "outer_diameter": Map({"value": Float(), "unit": Str()}),
        "inner_diameter": Map({"value": Float(), "unit": Str()}),
        "inner_roughness": Map({"value": Float(), "unit": Str()}),
        Optional("material"): Str(),
        "top_of_filler": Map({"value": Float(), "unit": Str()}),
        Optional("filler_material"): Str(),
        Optional("material_above_filler"): Str(),
    }
)
composition_description_schema = Map(
    {
        "component": Str(),
        Optional("molar_fraction"): Map({"value": Float(), "unit": Str()}),
        Optional("reference_enthalpy"): Map({"value": Float(), "unit": Str()}),
    }
)
compressor_pressure_table_description_schema = Map(
    {
        Optional("speed_entries"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("corrected_mass_flow_rate_entries"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("pressure_ratio_table"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("isentropic_efficiency_table"): Map({"values": Seq(Float()), "unit": Str()}),
    }
)
controller_input_signal_properties_description_schema = Map(
    {
        Optional("target_variable"): Str(),
        Optional("input_trend_name"): Str(),
        Optional("unit"): Str(),
    }
)
controller_output_signal_properties_description_schema = Map(
    {
        Optional("controlled_property"): Str(),
        Optional("unit"): Str(),
        Optional("network_element_name"): Str(),
        Optional("min_value"): Float(),
        Optional("max_value"): Float(),
        Optional("max_rate_of_change"): Float(),
    }
)
cv_table_description_schema = Map(
    {
        Optional("opening"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("flow_coefficient"): Map({"values": Seq(Float()), "unit": Str()}),
    }
)
environment_property_description_schema = Map(
    {
        "position": Map({"value": Float(), "unit": Str()}),
        "temperature": Map({"value": Float(), "unit": Str()}),
        "type": Enum(['walls_and_environment_heat_transfer_coefficient', 'walls_and_water_heat_transfer_coefficient_model', 'walls_and_air_heat_transfer_coefficient_model', 'overall_heat_transfer_coefficient_model', 'walls_without_environment_heat_transfer_coefficient']),
        Optional("heat_transfer_coefficient"): Map({"value": Float(), "unit": Str()}),
        Optional("overall_heat_transfer_coefficient"): Map({"value": Float(), "unit": Str()}),
        Optional("fluid_velocity"): Map({"value": Float(), "unit": Str()}),
    }
)
equipment_trend_description_schema = Map(
    {
        Optional("name"): Str(),
        "curve_names": Seq(Str()),
        "element_name": Str(),
    }
)
formation_layer_description_schema = Map(
    {
        "name": Str(),
        "start": Map({"value": Float(), "unit": Str()}),
        Optional("material"): Str(),
    }
)
gas_lift_valve_equipment_description_schema = Map(
    {
        "position": Map({"value": Float(), "unit": Str()}),
        "diameter": Map({"value": Float(), "unit": Str()}),
        "valve_type": Enum(['perkins_valve', 'choke_valve_with_flow_coefficient', 'check_valve']),
        "delta_p_min": Map({"value": Float(), "unit": Str()}),
        "discharge_coefficient": Map({"value": Float(), "unit": Str()}),
    }
)
global_trend_description_schema = Map(
    {
        Optional("name"): Str(),
        "curve_names": Seq(Str()),
    }
)
heat_source_equipment_description_schema = Map(
    {
        "start": Map({"value": Float(), "unit": Str()}),
        "length": Map({"value": Float(), "unit": Str()}),
        Optional("power_input_type"): Enum(['constant', 'curve']),
        Optional("power"): Map({"value": Float(), "unit": Str()}),
        Optional("power_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
    }
)
heavy_component_description_schema = Map(
    {
        "name": Str(),
        "scn": Int(),
        Optional("MW"): Map({"value": Float(), "unit": Str()}),
        Optional("rho"): Map({"value": Float(), "unit": Str()}),
    }
)
ipr_curve_description_schema = Map(
    {
        Optional("pressure_difference"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("flow_rate"): Map({"values": Seq(Float()), "unit": Str()}),
    }
)
internal_node_properties_description_schema = Map(
    {
        Optional("fluid"): Str(),
    }
)
length_and_elevation_description_schema = Map(
    {
        Optional("length"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("elevation"): Map({"values": Seq(Float()), "unit": Str()}),
    }
)
light_component_description_schema = Map(
    {
        "name": Str(),
        Optional("Pc"): Map({"value": Float(), "unit": Str()}),
        Optional("Tc"): Map({"value": Float(), "unit": Str()}),
        Optional("Vc"): Map({"value": Float(), "unit": Str()}),
        Optional("omega"): Map({"value": Float(), "unit": Str()}),
        Optional("MW"): Map({"value": Float(), "unit": Str()}),
        Optional("Tb"): Map({"value": Float(), "unit": Str()}),
        Optional("Parachor"): Map({"value": Float(), "unit": Str()}),
        Optional("Cp_0"): Map({"value": Float(), "unit": Str()}),
        Optional("Cp_1"): Map({"value": Float(), "unit": Str()}),
        Optional("Cp_2"): Map({"value": Float(), "unit": Str()}),
        Optional("Cp_3"): Map({"value": Float(), "unit": Str()}),
        Optional("Cp_4"): Map({"value": Float(), "unit": Str()}),
    }
)
linear_ipr_description_schema = Map(
    {
        Optional("well_index_phase"): Enum(['well_index_phase_gas', 'well_index_phase_oil', 'well_index_phase_water', 'well_index_phase_liquid']),
        Optional("min_pressure_difference"): Map({"value": Float(), "unit": Str()}),
        Optional("well_index_input_type"): Enum(['constant', 'curve']),
        Optional("well_index"): Map({"value": Float(), "unit": Str()}),
        Optional("well_index_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
    }
)
mass_source_equipment_description_schema = Map(
    {
        Optional("fluid"): Str(),
        Optional("tracer_mass_fraction"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("temperature_input_type"): Enum(['constant', 'curve']),
        Optional("temperature"): Map({"value": Float(), "unit": Str()}),
        Optional("temperature_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        Optional("source_type"): Enum(['mass_source_type_mass_flow_rates', 'mass_source_type_all_volumetric_flow_rates', 'mass_source_type_flow_rate_oil_gor_wc', 'mass_source_type_flow_rate_gas_gor_wc', 'mass_source_type_flow_rate_water_gor_wc', 'mass_source_type_total_mass_flow_rate_pvt_split']),
        Optional("volumetric_flow_rates_std_input_type"): Enum(['constant', 'curve']),
        Optional("volumetric_flow_rates_std"): MapPattern(Str(), Map({"value": Float(), "unit": Str()})),
        Optional("volumetric_flow_rates_std_curve"): MapPattern(
            Str(),
            Map(
                {
                    "image": Map({"values": Seq(Float()), "unit": Str()}),
                    "domain": Map({"values": Seq(Float()), "unit": Str()}),
                }
            ),
        ),
        Optional("mass_flow_rates_input_type"): Enum(['constant', 'curve']),
        Optional("mass_flow_rates"): MapPattern(Str(), Map({"value": Float(), "unit": Str()})),
        Optional("mass_flow_rates_curve"): MapPattern(
            Str(),
            Map(
                {
                    "image": Map({"values": Seq(Float()), "unit": Str()}),
                    "domain": Map({"values": Seq(Float()), "unit": Str()}),
                }
            ),
        ),
        Optional("total_mass_flow_rate_input_type"): Enum(['constant', 'curve']),
        Optional("total_mass_flow_rate"): Map({"value": Float(), "unit": Str()}),
        Optional("total_mass_flow_rate_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        Optional("water_cut_input_type"): Enum(['constant', 'curve']),
        Optional("water_cut"): Map({"value": Float(), "unit": Str()}),
        Optional("water_cut_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        Optional("gas_oil_ratio_input_type"): Enum(['constant', 'curve']),
        Optional("gas_oil_ratio"): Map({"value": Float(), "unit": Str()}),
        Optional("gas_oil_ratio_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        "position": Map({"value": Float(), "unit": Str()}),
    }
)
mass_source_node_properties_description_schema = Map(
    {
        Optional("fluid"): Str(),
        Optional("tracer_mass_fraction"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("temperature_input_type"): Enum(['constant', 'curve']),
        Optional("temperature"): Map({"value": Float(), "unit": Str()}),
        Optional("temperature_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        Optional("source_type"): Enum(['mass_source_type_mass_flow_rates', 'mass_source_type_all_volumetric_flow_rates', 'mass_source_type_flow_rate_oil_gor_wc', 'mass_source_type_flow_rate_gas_gor_wc', 'mass_source_type_flow_rate_water_gor_wc', 'mass_source_type_total_mass_flow_rate_pvt_split']),
        Optional("volumetric_flow_rates_std_input_type"): Enum(['constant', 'curve']),
        Optional("volumetric_flow_rates_std"): MapPattern(Str(), Map({"value": Float(), "unit": Str()})),
        Optional("volumetric_flow_rates_std_curve"): MapPattern(
            Str(),
            Map(
                {
                    "image": Map({"values": Seq(Float()), "unit": Str()}),
                    "domain": Map({"values": Seq(Float()), "unit": Str()}),
                }
            ),
        ),
        Optional("mass_flow_rates_input_type"): Enum(['constant', 'curve']),
        Optional("mass_flow_rates"): MapPattern(Str(), Map({"value": Float(), "unit": Str()})),
        Optional("mass_flow_rates_curve"): MapPattern(
            Str(),
            Map(
                {
                    "image": Map({"values": Seq(Float()), "unit": Str()}),
                    "domain": Map({"values": Seq(Float()), "unit": Str()}),
                }
            ),
        ),
        Optional("total_mass_flow_rate_input_type"): Enum(['constant', 'curve']),
        Optional("total_mass_flow_rate"): Map({"value": Float(), "unit": Str()}),
        Optional("total_mass_flow_rate_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        Optional("water_cut_input_type"): Enum(['constant', 'curve']),
        Optional("water_cut"): Map({"value": Float(), "unit": Str()}),
        Optional("water_cut_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        Optional("gas_oil_ratio_input_type"): Enum(['constant', 'curve']),
        Optional("gas_oil_ratio"): Map({"value": Float(), "unit": Str()}),
        Optional("gas_oil_ratio_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
    }
)
material_description_schema = Map(
    {
        "name": Str(),
        Optional("material_type"): Enum(['solid', 'fluid']),
        Optional("density"): Map({"value": Float(), "unit": Str()}),
        Optional("thermal_conductivity"): Map({"value": Float(), "unit": Str()}),
        Optional("heat_capacity"): Map({"value": Float(), "unit": Str()}),
        Optional("inner_emissivity"): Map({"value": Float(), "unit": Str()}),
        Optional("outer_emissivity"): Map({"value": Float(), "unit": Str()}),
        Optional("expansion"): Map({"value": Float(), "unit": Str()}),
        Optional("viscosity"): Map({"value": Float(), "unit": Str()}),
    }
)
numerical_options_description_schema = Map(
    {
        Optional("nonlinear_solver_type"): Enum(['nonlinear_solver_newton_basic', 'nonlinear_solver_newton_backtracking', 'nonlinear_solver_alfasim_quasi_newton']),
        Optional("tolerance"): Float(),
        Optional("maximum_iterations"): Int(),
        Optional("maximum_timestep_change_factor"): Float(),
        Optional("maximum_cfl_value"): Float(),
        Optional("relaxed_tolerance"): Float(),
        Optional("divergence_tolerance"): Float(),
        Optional("friction_factor_evaluation_strategy"): Enum(['time_explicit', 'newton_explicit', 'implicit']),
        Optional("simulation_mode"): Enum(['default', 'robust']),
        Optional("enable_solver_caching"): Bool(),
        Optional("caching_rtol"): Float(),
        Optional("caching_atol"): Float(),
        Optional("always_repeat_timestep"): Bool(),
    }
)
open_hole_description_schema = Map(
    {
        "name": Str(),
        "length": Map({"value": Float(), "unit": Str()}),
        "diameter": Map({"value": Float(), "unit": Str()}),
        "inner_roughness": Map({"value": Float(), "unit": Str()}),
    }
)
overall_pipe_trend_description_schema = Map(
    {
        Optional("name"): Str(),
        "curve_names": Seq(Str()),
        "location": Enum(['main', 'annulus', 'not_defined']),
        "element_name": Str(),
    }
)
packer_description_schema = Map(
    {
        "name": Str(),
        "position": Map({"value": Float(), "unit": Str()}),
        Optional("material_above"): Str(),
    }
)
physics_description_schema = Map(
    {
        Optional("hydrodynamic_model"): Enum(['hydrodynamic_model_2_fields', 'hydrodynamic_model_4_fields', 'hydrodynamic_model_3_layers_gas_oil_water', 'hydrodynamic_model_5_fields_solid', 'hydrodynamic_model_5_fields_water', 'hydrodynamic_model_5_fields_co2', 'hydrodynamic_model_3_layers_no_bubble_gas_oil_water', 'hydrodynamic_model_3_layers_water_with_co2', 'hydrodynamic_model_3_layers_7_fields_gas_oil_water', 'hydrodynamic_model_3_layers_9_fields_gas_oil_water']),
        Optional("simulation_regime"): Enum(['simulation_regime_transient', 'simulation_regime_steady_state']),
        Optional("energy_model"): Enum(['no_model', 'global_model', 'layers_model']),
        Optional("solids_model"): Enum(['no_model', 'thomas1965_equilibrium', 'mills1985_equilibrium', 'santamaria2010_equilibrium', 'from_plugin']),
        Optional("solids_model_plugin_id"): Str(),
        Optional("initial_condition_strategy"): Enum(['constant', 'steady_state', 'restart']),
        Optional("restart_filepath"): Str(),
        Optional("keep_former_results"): Bool(),
        Optional("emulsion_model"): Enum(['no_model', 'model_default', 'taylor1932', 'brinkman1952', 'mooney1951a', 'mooney1951b', 'hinze1955', 'sleicher1962', 'brauner2001', 'boxall2012', 'brinkman1952_and_yeh1964', 'from_plugin']),
        Optional("flash_model"): Enum(['hydrocarbon_only', 'hydrocarbon_and_water']),
        Optional("correlations_package"): Enum(['correlation_package_classical', 'correlation_package_alfasim', 'correlation_package_isdb_tests']),
    }
)
pig_equipment_description_schema = Map(
    {
        "diameter": Map({"value": Float(), "unit": Str()}),
        "position": Map({"value": Float(), "unit": Str()}),
        Optional("launch_times"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("mass_input_type"): Enum(['constant', 'curve']),
        Optional("mass"): Map({"value": Float(), "unit": Str()}),
        Optional("mass_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        Optional("static_force_input_type"): Enum(['constant', 'curve']),
        Optional("static_force"): Map({"value": Float(), "unit": Str()}),
        Optional("static_force_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        Optional("wall_friction_input_type"): Enum(['constant', 'curve']),
        Optional("wall_friction"): Map({"value": Float(), "unit": Str()}),
        Optional("wall_friction_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        Optional("linear_friction_input_type"): Enum(['constant', 'curve']),
        Optional("linear_friction"): Map({"value": Float(), "unit": Str()}),
        Optional("linear_friction_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        Optional("quadratic_friction_input_type"): Enum(['constant', 'curve']),
        Optional("quadratic_friction"): Map({"value": Float(), "unit": Str()}),
        Optional("quadratic_friction_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        Optional("trap_mode"): Enum(['automatic', 'user_defined']),
        Optional("trap_position"): Map({"value": Float(), "unit": Str()}),
        Optional("trap_pipe_name"): Str(),
        Optional("route_mode"): Enum(['automatic', 'user_defined']),
        Optional("pipe_route_names"): Seq(Str()),
    }
)
pipe_segments_description_schema = Map(
    {
        "start_positions": Map({"values": Seq(Float()), "unit": Str()}),
        "diameters": Map({"values": Seq(Float()), "unit": Str()}),
        "roughnesses": Map({"values": Seq(Float()), "unit": Str()}),
        Optional("wall_names"): Seq(Str()),
    }
)
pressure_container_description_schema = Map(
    {
        Optional("positions"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("pressures"): Map({"values": Seq(Float()), "unit": Str()}),
    }
)
pressure_node_properties_description_schema = Map(
    {
        Optional("pressure_input_type"): Enum(['constant', 'curve']),
        Optional("pressure"): Map({"value": Float(), "unit": Str()}),
        Optional("pressure_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        Optional("temperature_input_type"): Enum(['constant', 'curve']),
        Optional("temperature"): Map({"value": Float(), "unit": Str()}),
        Optional("temperature_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        Optional("fluid"): Str(),
        Optional("tracer_mass_fraction"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("split_type"): Enum(['mass_inflow_split_type_constant_volume_fraction', 'mass_inflow_split_type_constant_mass_fraction', 'mass_inflow_split_type_pvt', 'mass_inflow_split_type_pvt_user_gor_wc', 'mass_inflow_split_type_pvt_user_glr_wc']),
        Optional("mass_fractions_input_type"): Enum(['constant', 'curve']),
        Optional("mass_fractions"): MapPattern(Str(), Map({"value": Float(), "unit": Str()})),
        Optional("mass_fractions_curve"): MapPattern(
            Str(),
            Map(
                {
                    "image": Map({"values": Seq(Float()), "unit": Str()}),
                    "domain": Map({"values": Seq(Float()), "unit": Str()}),
                }
            ),
        ),
        Optional("volume_fractions_input_type"): Enum(['constant', 'curve']),
        Optional("volume_fractions"): MapPattern(Str(), Map({"value": Float(), "unit": Str()})),
        Optional("volume_fractions_curve"): MapPattern(
            Str(),
            Map(
                {
                    "image": Map({"values": Seq(Float()), "unit": Str()}),
                    "domain": Map({"values": Seq(Float()), "unit": Str()}),
                }
            ),
        ),
        Optional("gas_liquid_ratio_input_type"): Enum(['constant', 'curve']),
        Optional("gas_liquid_ratio"): Map({"value": Float(), "unit": Str()}),
        Optional("gas_liquid_ratio_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        Optional("gas_oil_ratio_input_type"): Enum(['constant', 'curve']),
        Optional("gas_oil_ratio"): Map({"value": Float(), "unit": Str()}),
        Optional("gas_oil_ratio_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        Optional("water_cut_input_type"): Enum(['constant', 'curve']),
        Optional("water_cut"): Map({"value": Float(), "unit": Str()}),
        Optional("water_cut_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
    }
)
profile_output_description_schema = Map(
    {
        "curve_names": Seq(Str()),
        "location": Enum(['main', 'annulus', 'not_defined']),
        "element_name": Str(),
    }
)
pvt_model_correlation_description_schema = Map(
    {
        Optional("oil_density_std"): Map({"value": Float(), "unit": Str()}),
        Optional("gas_density_std"): Map({"value": Float(), "unit": Str()}),
        Optional("rs_sat"): Map({"value": Float(), "unit": Str()}),
        Optional("pvt_correlation_package"): Enum(['pvt_correlation_package_lasater', 'pvt_correlation_package_standing', 'pvt_correlation_package_vazquez_beggs', 'pvt_correlation_package_glaso']),
    }
)
referenced_pressure_container_description_schema = Map(
    {
        Optional("reference_coordinate"): Map({"value": Float(), "unit": Str()}),
        Optional("positions"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("pressures"): Map({"values": Seq(Float()), "unit": Str()}),
    }
)
referenced_temperatures_container_description_schema = Map(
    {
        Optional("reference_coordinate"): Map({"value": Float(), "unit": Str()}),
        Optional("positions"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("temperatures"): Map({"values": Seq(Float()), "unit": Str()}),
    }
)
referenced_tracers_mass_fractions_container_description_schema = Map(
    {
        Optional("reference_coordinate"): Map({"value": Float(), "unit": Str()}),
        Optional("positions"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("tracers_mass_fractions"): Seq(Map({"values": Seq(Float()), "unit": Str()})),
    }
)
referenced_velocities_container_description_schema = Map(
    {
        Optional("reference_coordinate"): Map({"value": Float(), "unit": Str()}),
        Optional("positions"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("velocities"): MapPattern(Str(), Map({"values": Seq(Float()), "unit": Str()})),
    }
)
referenced_volume_fractions_container_description_schema = Map(
    {
        Optional("reference_coordinate"): Map({"value": Float(), "unit": Str()}),
        Optional("positions"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("fractions"): MapPattern(Str(), Map({"values": Seq(Float()), "unit": Str()})),
    }
)
reservoir_inflow_equipment_description_schema = Map(
    {
        Optional("pressure_input_type"): Enum(['constant', 'curve']),
        Optional("pressure"): Map({"value": Float(), "unit": Str()}),
        Optional("pressure_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        Optional("temperature_input_type"): Enum(['constant', 'curve']),
        Optional("temperature"): Map({"value": Float(), "unit": Str()}),
        Optional("temperature_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        Optional("fluid"): Str(),
        Optional("tracer_mass_fraction"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("split_type"): Enum(['mass_inflow_split_type_constant_volume_fraction', 'mass_inflow_split_type_constant_mass_fraction', 'mass_inflow_split_type_pvt', 'mass_inflow_split_type_pvt_user_gor_wc', 'mass_inflow_split_type_pvt_user_glr_wc']),
        Optional("mass_fractions_input_type"): Enum(['constant', 'curve']),
        Optional("mass_fractions"): MapPattern(Str(), Map({"value": Float(), "unit": Str()})),
        Optional("mass_fractions_curve"): MapPattern(
            Str(),
            Map(
                {
                    "image": Map({"values": Seq(Float()), "unit": Str()}),
                    "domain": Map({"values": Seq(Float()), "unit": Str()}),
                }
            ),
        ),
        Optional("volume_fractions_input_type"): Enum(['constant', 'curve']),
        Optional("volume_fractions"): MapPattern(Str(), Map({"value": Float(), "unit": Str()})),
        Optional("volume_fractions_curve"): MapPattern(
            Str(),
            Map(
                {
                    "image": Map({"values": Seq(Float()), "unit": Str()}),
                    "domain": Map({"values": Seq(Float()), "unit": Str()}),
                }
            ),
        ),
        Optional("gas_liquid_ratio_input_type"): Enum(['constant', 'curve']),
        Optional("gas_liquid_ratio"): Map({"value": Float(), "unit": Str()}),
        Optional("gas_liquid_ratio_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        Optional("gas_oil_ratio_input_type"): Enum(['constant', 'curve']),
        Optional("gas_oil_ratio"): Map({"value": Float(), "unit": Str()}),
        Optional("gas_oil_ratio_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        Optional("water_cut_input_type"): Enum(['constant', 'curve']),
        Optional("water_cut"): Map({"value": Float(), "unit": Str()}),
        Optional("water_cut_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        "start": Map({"value": Float(), "unit": Str()}),
        "length": Map({"value": Float(), "unit": Str()}),
        Optional("productivity_ipr"): Str(),
        Optional("injectivity_ipr"): Str(),
    }
)
separator_node_properties_description_schema = Map(
    {
        Optional("environment_temperature"): Map({"value": Float(), "unit": Str()}),
        Optional("geometry"): Enum(['vertical_cylinder', 'horizontal_cylinder', 'sphere']),
        Optional("length"): Map({"value": Float(), "unit": Str()}),
        Optional("overall_heat_transfer_coefficient"): Map({"value": Float(), "unit": Str()}),
        Optional("diameter"): Map({"value": Float(), "unit": Str()}),
        Optional("nozzles"): MapPattern(Str(), Map({"value": Float(), "unit": Str()})),
        Optional("initial_phase_volume_fractions"): MapPattern(Str(), Map({"value": Float(), "unit": Str()})),
        Optional("gas_separation_efficiency"): Map({"value": Float(), "unit": Str()}),
        Optional("liquid_separation_efficiency"): Map({"value": Float(), "unit": Str()}),
    }
)
separator_trend_description_schema = Map(
    {
        Optional("name"): Str(),
        "curve_names": Seq(Str()),
        "element_name": Str(),
    }
)
speed_curve_description_schema = Map(
    {
        Optional("time"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("speed"): Map({"values": Seq(Float()), "unit": Str()}),
    }
)
surge_volume_options_description_schema = Map(
    {
        Optional("time_mode"): Enum(['all_simulation', 'user_defined']),
        Optional("drainage_mode"): Enum(['automatic', 'user_defined']),
        Optional("start_time"): Map({"value": Float(), "unit": Str()}),
        Optional("end_time"): Map({"value": Float(), "unit": Str()}),
        Optional("maximum_drainage_rate"): Map({"value": Float(), "unit": Str()}),
    }
)
table_pump_description_schema = Map(
    {
        Optional("speeds"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("void_fractions"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("flow_rates"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("pressure_boosts"): Map({"values": Seq(Float()), "unit": Str()}),
    }
)
temperatures_container_description_schema = Map(
    {
        Optional("positions"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("temperatures"): Map({"values": Seq(Float()), "unit": Str()}),
    }
)
time_options_description_schema = Map(
    {
        Optional("stop_on_steady_state"): Bool(),
        Optional("automatic_restart_autosave_frequency"): Bool(),
        Optional("initial_time"): Map({"value": Float(), "unit": Str()}),
        Optional("final_time"): Map({"value": Float(), "unit": Str()}),
        Optional("initial_timestep"): Map({"value": Float(), "unit": Str()}),
        Optional("minimum_timestep"): Map({"value": Float(), "unit": Str()}),
        Optional("maximum_timestep"): Map({"value": Float(), "unit": Str()}),
        Optional("restart_autosave_frequency"): Map({"value": Float(), "unit": Str()}),
        Optional("minimum_time_for_steady_state_stop"): Map({"value": Float(), "unit": Str()}),
    }
)
tracer_model_constant_coefficients_description_schema = Map(
    {
        Optional("partition_coefficients"): MapPattern(Str(), Map({"value": Float(), "unit": Str()})),
    }
)
tracers_mass_fractions_container_description_schema = Map(
    {
        Optional("positions"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("tracers_mass_fractions"): Seq(Map({"values": Seq(Float()), "unit": Str()})),
    }
)
tubing_description_schema = Map(
    {
        "name": Str(),
        "length": Map({"value": Float(), "unit": Str()}),
        "outer_diameter": Map({"value": Float(), "unit": Str()}),
        "inner_diameter": Map({"value": Float(), "unit": Str()}),
        "inner_roughness": Map({"value": Float(), "unit": Str()}),
        Optional("material"): Str(),
    }
)
velocities_container_description_schema = Map(
    {
        Optional("positions"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("velocities"): MapPattern(Str(), Map({"values": Seq(Float()), "unit": Str()})),
    }
)
volume_fractions_container_description_schema = Map(
    {
        Optional("positions"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("fractions"): MapPattern(Str(), Map({"values": Seq(Float()), "unit": Str()})),
    }
)
wall_layer_description_schema = Map(
    {
        "thickness": Map({"value": Float(), "unit": Str()}),
        "material_name": Str(),
        Optional("has_annulus_flow"): Bool(),
    }
)
x_and_y_description_schema = Map(
    {
        Optional("x"): Map({"values": Seq(Float()), "unit": Str()}),
        Optional("y"): Map({"values": Seq(Float()), "unit": Str()}),
    }
)
casing_description_schema = Map(
    {
        Optional("casing_sections"): Seq(casing_section_description_schema),
        Optional("tubings"): Seq(tubing_description_schema),
        Optional("packers"): Seq(packer_description_schema),
        Optional("open_holes"): Seq(open_hole_description_schema),
    }
)
compressor_equipment_description_schema = Map(
    {
        "position": Map({"value": Float(), "unit": Str()}),
        Optional("speed_curve"): speed_curve_description_schema,
        Optional("reference_pressure"): Map({"value": Float(), "unit": Str()}),
        Optional("reference_temperature"): Map({"value": Float(), "unit": Str()}),
        Optional("constant_speed"): Map({"value": Float(), "unit": Str()}),
        Optional("compressor_type"): Enum(['speed_curve', 'constant_speed']),
        Optional("speed_curve_interpolation_type"): Enum(['constant', 'linear', 'quadratic']),
        Optional("flow_direction"): Enum(['forward', 'backward']),
        Optional("table"): compressor_pressure_table_description_schema,
    }
)
controller_node_properties_description_schema = Map(
    {
        Optional("type"): Enum(['pid']),
        Optional("gain"): Float(),
        Optional("setpoint"): Float(),
        Optional("integral_time"): Map({"value": Float(), "unit": Str()}),
        Optional("derivative_time"): Map({"value": Float(), "unit": Str()}),
        Optional("input_signal_properties"): controller_input_signal_properties_description_schema,
        Optional("output_signal_properties"): controller_output_signal_properties_description_schema,
    }
)
environment_description_schema = Map(
    {
        Optional("thermal_model"): Enum(['adiabatic_walls', 'steady_state_heat_transfer', 'transient_heat_transfer']),
        Optional("position_input_mode"): Enum(['position_by_tvd', 'position_by_md']),
        Optional("reference_y_coordinate"): Map({"value": Float(), "unit": Str()}),
        Optional("md_properties_table"): Seq(environment_property_description_schema),
        Optional("tvd_properties_table"): Seq(environment_property_description_schema),
    }
)
fluid_description_schema = Map(
    {
        Optional("composition"): Seq(composition_description_schema),
        Optional("fraction_pairs"): Seq(bip_description_schema),
    }
)
formation_description_schema = Map(
    {
        "reference_y_coordinate": Map({"value": Float(), "unit": Str()}),
        Optional("layers"): Seq(formation_layer_description_schema),
    }
)
initial_pressures_description_schema = Map(
    {
        Optional("position_input_type"): Enum(['vertical_position', 'horizontal_position', 'length']),
        Optional("table_x"): referenced_pressure_container_description_schema,
        Optional("table_y"): referenced_pressure_container_description_schema,
        Optional("table_length"): pressure_container_description_schema,
    }
)
initial_temperatures_description_schema = Map(
    {
        Optional("position_input_type"): Enum(['vertical_position', 'horizontal_position', 'length']),
        Optional("table_x"): referenced_temperatures_container_description_schema,
        Optional("table_y"): referenced_temperatures_container_description_schema,
        Optional("table_length"): temperatures_container_description_schema,
    }
)
initial_tracers_mass_fractions_description_schema = Map(
    {
        Optional("position_input_type"): Enum(['vertical_position', 'horizontal_position', 'length']),
        Optional("table_x"): referenced_tracers_mass_fractions_container_description_schema,
        Optional("table_y"): referenced_tracers_mass_fractions_container_description_schema,
        Optional("table_length"): tracers_mass_fractions_container_description_schema,
    }
)
initial_velocities_description_schema = Map(
    {
        Optional("position_input_type"): Enum(['vertical_position', 'horizontal_position', 'length']),
        Optional("table_x"): referenced_velocities_container_description_schema,
        Optional("table_y"): referenced_velocities_container_description_schema,
        Optional("table_length"): velocities_container_description_schema,
    }
)
initial_volume_fractions_description_schema = Map(
    {
        Optional("position_input_type"): Enum(['vertical_position', 'horizontal_position', 'length']),
        Optional("table_x"): referenced_volume_fractions_container_description_schema,
        Optional("table_y"): referenced_volume_fractions_container_description_schema,
        Optional("table_length"): volume_fractions_container_description_schema,
    }
)
leak_equipment_description_schema = Map(
    {
        "position": Map({"value": Float(), "unit": Str()}),
        Optional("location"): Enum(['main', 'annulus', 'not_defined']),
        Optional("model"): Enum(['orifice', 'flow_coefficient', 'gas_lift_valve']),
        Optional("type"): Enum(['internal', 'external']),
        Optional("diameter"): Map({"value": Float(), "unit": Str()}),
        Optional("discharge_coefficient"): Map({"value": Float(), "unit": Str()}),
        Optional("cv_table"): cv_table_description_schema,
        Optional("gas_lift_valve_opening_type"): Enum(['minimum_pressure_difference', 'pressure_operated']),
        Optional("minimum_pressure_difference"): Map({"value": Float(), "unit": Str()}),
        Optional("bellows_reference_pressure"): Map({"value": Float(), "unit": Str()}),
        Optional("bellows_reference_temperature"): Map({"value": Float(), "unit": Str()}),
        Optional("port_to_bellows_area_ratio"): Map({"value": Float(), "unit": Str()}),
        Optional("opening_input_type"): Enum(['constant', 'curve']),
        Optional("opening"): Map({"value": Float(), "unit": Str()}),
        Optional("opening_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        Optional("target_pipe_name"): Str(),
        Optional("target_position"): Map({"value": Float(), "unit": Str()}),
        Optional("target_location"): Enum(['main', 'annulus', 'not_defined']),
        Optional("backflow"): Bool(),
        Optional("backpressure"): Map({"value": Float(), "unit": Str()}),
    }
)
positional_pipe_trend_description_schema = Map(
    {
        Optional("name"): Str(),
        "curve_names": Seq(Str()),
        "location": Enum(['main', 'annulus', 'not_defined']),
        "position": Map({"value": Float(), "unit": Str()}),
        "element_name": Str(),
        Optional("surge_volume_options"): surge_volume_options_description_schema,
    }
)
profile_description_schema = Map(
    {
        Optional("x_and_y"): x_and_y_description_schema,
        Optional("length_and_elevation"): length_and_elevation_description_schema,
    }
)
pump_equipment_description_schema = Map(
    {
        "position": Map({"value": Float(), "unit": Str()}),
        Optional("type"): Enum(['constant_pressure', 'table_interpolation']),
        Optional("pressure_boost"): Map({"value": Float(), "unit": Str()}),
        Optional("thermal_efficiency"): Map({"value": Float(), "unit": Str()}),
        Optional("table"): table_pump_description_schema,
        Optional("speed_curve"): speed_curve_description_schema,
        Optional("speed_curve_interpolation_type"): Enum(['constant', 'linear', 'quadratic']),
        Optional("flow_direction"): Enum(['forward', 'backward']),
    }
)
table_ipr_description_schema = Map(
    {
        Optional("well_index_phase"): Enum(['well_index_phase_gas', 'well_index_phase_oil', 'well_index_phase_water', 'well_index_phase_liquid']),
        Optional("table"): ipr_curve_description_schema,
    }
)
tracers_description_schema = Map(
    {
        Optional("constant_coefficients"): MapPattern(Str(), tracer_model_constant_coefficients_description_schema),
    }
)
valve_equipment_description_schema = Map(
    {
        "position": Map({"value": Float(), "unit": Str()}),
        Optional("type"): Enum(['perkins_valve', 'choke_valve_with_flow_coefficient', 'check_valve']),
        Optional("diameter"): Map({"value": Float(), "unit": Str()}),
        Optional("flow_direction"): Enum(['forward', 'backward']),
        Optional("opening_type"): Enum(['constant_opening', 'table_interpolation']),
        Optional("opening"): Map({"value": Float(), "unit": Str()}),
        Optional("opening_curve_interpolation_type"): Enum(['constant', 'linear', 'quadratic']),
        Optional("opening_curve"): Map(
            {
                "image": Map({"values": Seq(Float()), "unit": Str()}),
                "domain": Map({"values": Seq(Float()), "unit": Str()}),
            }
        ),
        Optional("cv_table"): cv_table_description_schema,
    }
)
wall_description_schema = Map(
    {
        "name": Str(),
        Optional("inner_roughness"): Map({"value": Float(), "unit": Str()}),
        Optional("wall_layer_container"): Seq(wall_layer_description_schema),
    }
)
annulus_equipment_description_schema = Map(
    {
        Optional("leaks"): MapPattern(Str(), leak_equipment_description_schema),
        Optional("gas_lift_valves"): MapPattern(Str(), gas_lift_valve_equipment_description_schema),
    }
)
equipment_description_schema = Map(
    {
        Optional("mass_sources"): MapPattern(Str(), mass_source_equipment_description_schema),
        Optional("pumps"): MapPattern(Str(), pump_equipment_description_schema),
        Optional("valves"): MapPattern(Str(), valve_equipment_description_schema),
        Optional("reservoir_inflows"): MapPattern(Str(), reservoir_inflow_equipment_description_schema),
        Optional("heat_sources"): MapPattern(Str(), heat_source_equipment_description_schema),
        Optional("compressors"): MapPattern(Str(), compressor_equipment_description_schema),
        Optional("leaks"): MapPattern(Str(), leak_equipment_description_schema),
        Optional("pigs"): MapPattern(Str(), pig_equipment_description_schema),
    }
)
ipr_models_description_schema = Map(
    {
        Optional("linear_models"): MapPattern(Str(), linear_ipr_description_schema),
        Optional("table_models"): MapPattern(Str(), table_ipr_description_schema),
    }
)
initial_conditions_description_schema = Map(
    {
        Optional("pressures"): initial_pressures_description_schema,
        Optional("volume_fractions"): initial_volume_fractions_description_schema,
        Optional("tracers_mass_fractions"): initial_tracers_mass_fractions_description_schema,
        Optional("velocities"): initial_velocities_description_schema,
        Optional("temperatures"): initial_temperatures_description_schema,
        Optional("fluid"): Str(),
    }
)
node_description_schema = Map(
    {
        "name": Str(),
        "node_type": Enum(['internal_node', 'mass_source_boundary', 'pressure_boundary', 'separator_node', 'controller_node']),
        Optional("pvt_model"): Str(),
        Optional("pressure_properties"): pressure_node_properties_description_schema,
        Optional("mass_source_properties"): mass_source_node_properties_description_schema,
        Optional("internal_properties"): internal_node_properties_description_schema,
        Optional("separator_properties"): separator_node_properties_description_schema,
        Optional("controller_properties"): controller_node_properties_description_schema,
    }
)
pvt_model_compositional_description_schema = Map(
    {
        Optional("equation_of_state_type"): Enum(['pvt_compositional_peng_robinson', 'pvt_compositional_soave_redlich_kwong']),
        Optional("surface_tension_model_type"): Enum(['WeinaugKatz', 'LeeChien', 'SchechterGuo']),
        Optional("viscosity_model"): Enum(['corresponding_states_principle', 'lohrenz_bray_clark']),
        Optional("heavy_components"): Seq(heavy_component_description_schema),
        Optional("light_components"): Seq(light_component_description_schema),
        Optional("fluids"): MapPattern(Str(), fluid_description_schema),
    }
)
trends_output_description_schema = Map(
    {
        Optional("positional_pipe_trends"): Seq(positional_pipe_trend_description_schema),
        Optional("overall_pipe_trends"): Seq(overall_pipe_trend_description_schema),
        Optional("global_trends"): Seq(global_trend_description_schema),
        Optional("equipment_trends"): Seq(equipment_trend_description_schema),
        Optional("separator_trends"): Seq(separator_trend_description_schema),
    }
)
annulus_description_schema = Map(
    {
        "has_annulus_flow": Bool(),
        Optional("pvt_model"): Str(),
        Optional("initial_conditions"): initial_conditions_description_schema,
        Optional("equipment"): annulus_equipment_description_schema,
        "top_node": Str(),
    }
)
case_output_description_schema = Map(
    {
        Optional("automatic_trend_frequency"): Bool(),
        Optional("trends"): trends_output_description_schema,
        Optional("trend_frequency"): Map({"value": Float(), "unit": Str()}),
        Optional("automatic_profile_frequency"): Bool(),
        Optional("profiles"): Seq(profile_output_description_schema),
        Optional("profile_frequency"): Map({"value": Float(), "unit": Str()}),
    }
)
pipe_description_schema = Map(
    {
        "name": Str(),
        "source": Str(),
        "target": Str(),
        Optional("source_port"): Enum(['port', 'left_annulus_port', 'right_annulus_port']),
        Optional("target_port"): Enum(['port', 'left_annulus_port', 'right_annulus_port']),
        Optional("pvt_model"): Str(),
        Optional("profile"): profile_description_schema,
        Optional("equipment"): equipment_description_schema,
        Optional("environment"): environment_description_schema,
        Optional("segments"): pipe_segments_description_schema,
        Optional("initial_conditions"): initial_conditions_description_schema,
    }
)
pvt_models_description_schema = Map(
    {
        Optional("default_model"): Str(),
        Optional("tables"): MapPattern(Str(), Str()),
        Optional("correlations"): MapPattern(Str(), pvt_model_correlation_description_schema),
        Optional("compositions"): MapPattern(Str(), pvt_model_compositional_description_schema),
    }
)
well_description_schema = Map(
    {
        "name": Str(),
        Optional("pvt_model"): Str(),
        Optional("stagnant_fluid"): Str(),
        Optional("profile"): profile_description_schema,
        Optional("casing"): casing_description_schema,
        Optional("annulus"): annulus_description_schema,
        Optional("formation"): formation_description_schema,
        "top_node": Str(),
        "bottom_node": Str(),
        Optional("environment"): environment_description_schema,
        Optional("initial_conditions"): initial_conditions_description_schema,
        Optional("equipment"): equipment_description_schema,
    }
)
case_description_schema = Map(
    {
        Optional("name"): Str(),
        Optional("physics"): physics_description_schema,
        Optional("time_options"): time_options_description_schema,
        Optional("numerical_options"): numerical_options_description_schema,
        Optional("ipr_models"): ipr_models_description_schema,
        Optional("pvt_models"): pvt_models_description_schema,
        Optional("tracers"): tracers_description_schema,
        Optional("outputs"): case_output_description_schema,
        Optional("pipes"): Seq(pipe_description_schema),
        Optional("nodes"): Seq(node_description_schema),
        Optional("wells"): Seq(well_description_schema),
        Optional("materials"): Seq(material_description_schema),
        Optional("walls"): Seq(wall_description_schema),
    }
)
# [[[end]]] (checksum: b15791693ba5dce623dd301a851d625e)
# fmt: on
