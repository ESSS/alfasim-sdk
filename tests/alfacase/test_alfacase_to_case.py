import shutil
import textwrap
from pathlib import Path

import attr
import numpy
import pytest
import strictyaml
from barril.units import Array, Scalar
from strictyaml import YAML
from strictyaml.ruamel.comments import CommentedMap

from alfasim_sdk import convert_description_to_alfacase
from alfasim_sdk._internal.alfacase import alfacase_to_case, case_description, schema
from alfasim_sdk._internal.alfacase.alfacase_to_case import (
    DescriptionDocument,
    get_array_loader,
    get_scalar_loader,
    load_mass_source_node_properties_description,
    load_physics_description,
    load_pvt_models_description,
)
from alfasim_sdk._internal.alfacase.case_description_attributes import DescriptionError
from alfasim_sdk._internal.alfacase.generate_schema import (
    IGNORED_PROPERTIES,
    convert_to_snake_case,
    get_all_classes_that_needs_schema,
    is_attrs,
)
from alfasim_sdk._internal.alfacase.schema import (
    mass_source_node_properties_description_schema,
)
from alfasim_sdk._internal.constants import MultiInputType

from ..common_testing.alfasim_sdk_common_testing import (
    filled_case_descriptions,
    get_acme_tab_file_path,
)
from ..common_testing.alfasim_sdk_common_testing.filled_case_descriptions import (
    ensure_descriptions_are_equal,
)


@attr.s(frozen=True)
class AlfacaseTestConfig:
    """
    Helper class for test that convert a YAML to CASE

    :ivar description_expected:
        A case description to be used for the test.
    :ivar schema:
        The related schema for the given case description defined on description_expected
        to validate the yaml content.
    :ivar is_sequence:
        Inform the expected case description generated is single instance or a list of instances.
    :ivar is_dict:
        Inform the expected case description generated is instance of a dictionary.
    """

    description_expected = attr.ib()
    schema = attr.ib()
    is_sequence = attr.ib(default=False)
    is_dict = attr.ib(default=False)

    @property
    def load_function_name(self):
        return "load_" + convert_to_snake_case(
            self.description_expected.__class__.__name__
        )


@pytest.fixture
def alfacase_to_case_helper(tmp_path):
    class AlfacaseHelper:
        def __init__(self, tmp_path) -> None:
            self.tmp_path = Path(tmp_path)

        def generate_description(
            self,
            alfacase_config: AlfacaseTestConfig,
            remove_redundant_input_type_data: bool = False,
        ):
            """
            Helper method to generate a "Description" from the given alfacase_config
            """
            alfacase_string = convert_description_to_alfacase(
                alfacase_config.description_expected,
                remove_redundant_input_type_data=remove_redundant_input_type_data,
            )
            alfacase_content = strictyaml.dirty_load(
                yaml_string=alfacase_string,
                schema=alfacase_config.schema,
                allow_flow_style=True,
            )

            # 'LoadPvtModelsDescription' is special case and the DescriptionDocument doesn't need a FakeKey
            skip_dict = (
                alfacase_config.load_function_name == "load_pvt_models_description"
            )

            if alfacase_config.is_sequence:
                alfacase_content = [alfacase_content]
            elif alfacase_config.is_dict and not skip_dict:
                alfacase_content = YAML(
                    CommentedMap({YAML("FakeKey"): alfacase_content})
                )

            description_document = DescriptionDocument(
                content=alfacase_content, file_path=self.tmp_path / "test_case.alfacase"
            )
            if hasattr(alfacase_to_case, alfacase_config.load_function_name):
                loader = getattr(alfacase_to_case, alfacase_config.load_function_name)
            else:
                loader = alfacase_to_case.get_instance_loader(
                    class_=alfacase_config.description_expected.__class__
                )

            return loader(description_document)

        def ensure_description_has_all_properties(
            self, expected_description_class, obtained_description_obj
        ):
            """
            Helper method that check if all attributes from the original class are present on
            the generated case.
            """
            all_keys = attr.fields_dict(expected_description_class).keys()
            obtained_keys = attr.asdict(obtained_description_obj).keys()

            expected_keys = {key for key in all_keys if key not in IGNORED_PROPERTIES}
            obtained_keys = {
                key for key in obtained_keys if key not in IGNORED_PROPERTIES
            }

            assert expected_keys == obtained_keys, (
                f"Error: missing the following key(s): {set(expected_keys).symmetric_difference(set(obtained_keys))}"
            )

    return AlfacaseHelper(tmp_path)


ALFACASE_TEST_CONFIG_MAP = {
    "BipDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.BIP_DESCRIPTION,
        schema=schema.bip_description_schema,
        is_sequence=True,
    ),
    "CasingSectionDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.CASING_SECTION_DESCRIPTION,
        schema=schema.casing_section_description_schema,
        is_sequence=True,
    ),
    "CompositionDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.COMPOSITION_DESCRIPTION_C1,
        schema=schema.composition_description_schema,
        is_sequence=True,
    ),
    "CvTableDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.CV_TABLE_DESCRIPTION_SCHEMA,
        schema=schema.cv_table_description_schema,
    ),
    "EnvironmentPropertyDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.ENVIRONMENT_PROPERTY_DESCRIPTION,
        schema=schema.environment_property_description_schema,
        is_sequence=True,
    ),
    "FormationLayerDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.FORMATION_LAYER_DESCRIPTION,
        schema=schema.formation_layer_description_schema,
        is_sequence=True,
    ),
    "GasLiftValveEquipmentDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.GAS_LIST_VALVE_DESCRIPTION,
        schema=schema.gas_lift_valve_equipment_description_schema,
        is_dict=True,
    ),
    "HeatSourceEquipmentDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.HEAT_SOURCE_DESCRIPTION,
        schema=schema.heat_source_equipment_description_schema,
        is_dict=True,
    ),
    "HeavyComponentDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.HEAVY_COMPONENT_DESCRIPTION,
        schema=schema.heavy_component_description_schema,
        is_sequence=True,
    ),
    "InitialConditionsDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.INITIAL_CONDITIONS_DESCRIPTION,
        schema=schema.initial_conditions_description_schema,
    ),
    "LengthAndElevationDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.LENGTH_AND_ELEVATION_DESCRIPTION,
        schema=schema.length_and_elevation_description_schema,
    ),
    "LightComponentDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.LIGH_COMPONENT_DESCRIPTION,
        schema=schema.light_component_description_schema,
        is_sequence=True,
    ),
    "MassSourceEquipmentDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.MASS_SOURCE_DESCRIPTION,
        schema=schema.mass_source_equipment_description_schema,
        is_dict=True,
    ),
    "MaterialDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.MATERIAL_DESCRIPTION,
        schema=schema.material_description_schema,
        is_sequence=True,
    ),
    "PressureNodePropertiesDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.PRESSURE_NODE_PROPERTIES_DESCRIPTION,
        schema=schema.pressure_node_properties_description_schema,
    ),
    "MassSourceNodePropertiesDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.MASS_SOURCE_NODE_PROPERTIES_DESCRIPTION,
        schema=schema.mass_source_node_properties_description_schema,
    ),
    "InternalNodePropertiesDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.INTERNAL_NODE_PROPERTIES_DESCRIPTION,
        schema=schema.internal_node_properties_description_schema,
    ),
    "SeparatorNodePropertiesDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.SEPARATOR_NODE_PROPERTIES_DESCRIPTION,
        schema=schema.separator_node_properties_description_schema,
    ),
    "NodeDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.NODE_MASS_SOURCE_DESCRIPTION,
        schema=schema.node_description_schema,
        is_sequence=True,
    ),
    "NumericalOptionsDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.NUMERICAL_OPTIONS_DESCRIPTION,
        schema=schema.numerical_options_description_schema,
    ),
    "OpenHoleDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.OPEN_HOLE_DESCRIPTION,
        schema=schema.open_hole_description_schema,
        is_sequence=True,
    ),
    "PackerDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.PACKER_DESCRIPTION,
        schema=schema.packer_description_schema,
        is_sequence=True,
    ),
    "PhysicsDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.PHYSICS_DESCRIPTION,
        schema=schema.physics_description_schema,
    ),
    "PipeSegmentsDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.PIPE_WALL_DESCRIPTION,
        schema=schema.pipe_segments_description_schema,
    ),
    "PluginDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.PLUGIN_DESCRIPTION,
        schema=schema.plugin_description_schema,
    ),
    "ProfileOutputDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.PROFILE_OUTPUT_DESCRIPTION,
        schema=schema.profile_output_description_schema,
        is_sequence=True,
    ),
    "PvtModelCorrelationDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.PVT_MODEL_CORRELATION_DEFINITION,
        schema=schema.pvt_model_correlation_description_schema,
        is_dict=True,
    ),
    "PvtModelConstantPropertiesDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.PVT_MODEL_CONST_TABLE_DEFINITION,
        schema=schema.pvt_model_constant_properties_description_schema,
        is_dict=True,
    ),
    "LinearIPRDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.LINEAR_IPR_DESCRIPTION,
        schema=schema.linear_ipr_description_schema,
        is_dict=True,
    ),
    "VogelIPRDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.VOGEL_IPR_DESCRIPTION,
        schema=schema.vogel_ipr_description_schema,
        is_dict=True,
    ),
    "FetkovichIPRDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.FETKOVICH_IPR_DESCRIPTION,
        schema=schema.fetkovich_ipr_description_schema,
        is_dict=True,
    ),
    "ForchheimerIPRDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.FORCHHEIMER_IPR_DESCRIPTION,
        schema=schema.forchheimer_ipr_description_schema,
        is_dict=True,
    ),
    "IPRCurveDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.IPR_CURVE_DESCRIPTION,
        schema=schema.ipr_curve_description_schema,
    ),
    "TableIPRDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.TABLE_IPR_DESCRIPTION,
        schema=schema.table_ipr_description_schema,
        is_dict=True,
    ),
    "IPRModelsDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.IPR_MODELS_DESCRIPTION,
        schema=schema.ipr_models_description_schema,
    ),
    "ReservoirInflowEquipmentDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.RESERVOIR_INFLOW_DESCRIPTION,
        schema=schema.reservoir_inflow_equipment_description_schema,
        is_dict=True,
    ),
    "SpeedCurveDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.SPEED_CURVE_DESCRIPTION,
        schema=schema.speed_curve_description_schema,
    ),
    "SurgeVolumeOptionsDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.SURGE_VOLUME_OPTIONS_DESCRIPTION,
        schema=schema.surge_volume_options_description_schema,
    ),
    "TablePumpDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.TABLE_PUMP_DESCRIPTION,
        schema=schema.table_pump_description_schema,
    ),
    "TimeOptionsDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.TIME_OPTIONS_DESCRIPTION,
        schema=schema.time_options_description_schema,
    ),
    "TracerModelConstantCoefficientsDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.TRACER_MODEL_CONSTANT_COEFFICIENTS_DESCRIPTION,
        schema=schema.tracer_model_constant_coefficients_description_schema,
        is_dict=True,
    ),
    "TrendsOutputDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.TRENDS_OUTPUT_DESCRIPTION,
        schema=schema.trends_output_description_schema,
    ),
    "PositionalPipeTrendDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.POSITIONAL_PIPE_TREND_OUTPUT_DESCRIPTION,
        schema=schema.positional_pipe_trend_description_schema,
        is_sequence=True,
    ),
    "GlobalTrendDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.GLOBAL_TREND_OUTPUT_DESCRIPTION,
        schema=schema.global_trend_description_schema,
        is_sequence=True,
    ),
    "EquipmentTrendDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.EQUIPMENT_TREND_OUTPUT_DESCRIPTION,
        schema=schema.equipment_trend_description_schema,
        is_sequence=True,
    ),
    "OverallPipeTrendDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.OVERALL_PIPE_TREND_OUTPUT_DESCRIPTION,
        schema=schema.overall_pipe_trend_description_schema,
        is_sequence=True,
    ),
    "SeparatorTrendDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.SEPARATOR_TREND_OUTPUT_DESCRIPTION,
        schema=schema.separator_trend_description_schema,
        is_sequence=True,
    ),
    "ControllerTrendDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.CONTROLLER_TREND_OUTPUT_DESCRIPTION,
        schema=schema.controller_trend_description_schema,
        is_sequence=True,
    ),
    "TubingDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.TUBING_DESCRIPTION,
        schema=schema.tubing_description_schema,
        is_sequence=True,
    ),
    "WallLayerDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.WALL_LAYER_DESCRIPTION,
        schema=schema.wall_layer_description_schema,
        is_sequence=True,
    ),
    "XAndYDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.X_AND_Y_DESCRIPTION,
        schema=schema.x_and_y_description_schema,
    ),
    "AnnulusDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.ANNULUS_DESCRIPTION,
        schema=schema.annulus_description_schema,
    ),
    "CaseOutputDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.CASE_OUTPUT_DESCRIPTION,
        schema=schema.case_output_description_schema,
    ),
    "CasingDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.CASING_DESCRIPTION,
        schema=schema.casing_description_schema,
    ),
    "CompressorEquipmentDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.COMPRESSOR_DESCRIPTION,
        schema=schema.compressor_equipment_description_schema,
        is_dict=True,
    ),
    "EnvironmentDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.ENVIRONMENT_DESCRIPTION,
        schema=schema.environment_description_schema,
    ),
    "CompositionalFluidDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.COMPOSITIONAL_FLUID_DESCRIPTION,
        schema=schema.compositional_fluid_description_schema,
        is_dict=True,
    ),
    "CombinedFluidDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.COMBINED_FLUID_DESCRIPTION,
        schema=schema.combined_fluid_description_schema,
        is_dict=True,
    ),
    "FormationDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.FORMATION_DESCRIPTION,
        schema=schema.formation_description_schema,
    ),
    "ProfileDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.PROFILE_DESCRIPTION_WITH_XY,
        schema=schema.profile_description_schema,
    ),
    "PigEquipmentDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.PIG_DESCRIPTION,
        schema=schema.pig_equipment_description_schema,
        is_dict=True,
    ),
    "PumpEquipmentDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.PUMP_DESCRIPTION,
        schema=schema.pump_equipment_description_schema,
    ),
    "TracersDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.TRACERS_DESCRIPTION,
        schema=schema.tracers_description_schema,
    ),
    "ValveEquipmentDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.VALVE_DESCRIPTION,
        schema=schema.valve_equipment_description_schema,
        is_dict=True,
    ),
    "WallDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.WALL_DESCRIPTION,
        schema=schema.wall_description_schema,
        is_sequence=True,
    ),
    "PvtModelCombinedDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.PVT_MODEL_COMBINED_DEFINITION,
        schema=schema.pvt_model_combined_description_schema,
        is_dict=True,
    ),
    "PvtModelCompositionalDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.PVT_MODEL_COMPOSITIONAL_DEFINITION,
        schema=schema.pvt_model_compositional_description_schema,
        is_dict=True,
    ),
    "EquipmentDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.EQUIPMENT_DESCRIPTION,
        schema=schema.equipment_description_schema,
    ),
    "AnnulusEquipmentDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.ANNULUS_EQUIPMENT_DESCRIPTION,
        schema=schema.annulus_equipment_description_schema,
    ),
    "PipeDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.PIPE_DESCRIPTION,
        schema=schema.pipe_description_schema,
        is_sequence=True,
    ),
    "WellDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.WELL_DESCRIPTION,
        schema=schema.well_description_schema,
        is_sequence=True,
    ),
    "PvtModelsDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.PVT_MODELS_DEFINITION,
        schema=schema.pvt_models_description_schema,
        is_dict=True,
    ),
    "AlfasimVersionInfo": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.ALFASIM_VERSION_INFO,
        schema=schema.alfasim_version_info_schema,
    ),
    "CaseDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.CASE,
        schema=schema.case_description_schema,
    ),
    "InitialVolumeFractionsDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.INITIAL_FRACTIONS_DESCRIPTION,
        schema=schema.initial_volume_fractions_description_schema,
    ),
    "InitialPressuresDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.INITIAL_PRESSURES_DESCRIPTION,
        schema=schema.initial_pressures_description_schema,
    ),
    "InitialVelocitiesDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.INITIAL_VELOCITIES_DESCRIPTION,
        schema=schema.initial_velocities_description_schema,
    ),
    "InitialTemperaturesDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.INITIAL_TEMPERATURES_DESCRIPTION,
        schema=schema.initial_temperatures_description_schema,
    ),
    "InitialTracersMassFractionsDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.INITIAL_TRACERS_MASS_FRACTIONS_DESCRIPTION,
        schema=schema.initial_tracers_mass_fractions_description_schema,
    ),
    "ReferencedPressureContainerDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.REFERENCED_PRESSURE_CONTAINER_DESCRIPTION,
        schema=schema.referenced_pressure_container_description_schema,
    ),
    "PressureContainerDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.PRESSURE_CONTAINER_DESCRIPTION,
        schema=schema.pressure_container_description_schema,
    ),
    "ReferencedVelocitiesContainerDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.REFERENCED_VELOCITIES_CONTAINER_DESCRIPTION,
        schema=schema.referenced_velocities_container_description_schema,
    ),
    "VelocitiesContainerDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.VELOCITIES_CONTAINER_DESCRIPTION,
        schema=schema.velocities_container_description_schema,
    ),
    "ReferencedTemperaturesContainerDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.REFERENCED_TEMPERATURES_CONTAINER_DESCRIPTION,
        schema=schema.referenced_temperatures_container_description_schema,
    ),
    "TemperaturesContainerDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.TEMPERATURES_CONTAINER_DESCRIPTION,
        schema=schema.temperatures_container_description_schema,
    ),
    "ReferencedVolumeFractionsContainerDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.REFERENCED_VOLUME_FRACTIONS_CONTAINER_DESCRIPTION,
        schema=schema.referenced_volume_fractions_container_description_schema,
    ),
    "VolumeFractionsContainerDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.VOLUME_FRACTIONS_CONTAINER_DESCRIPTION,
        schema=schema.volume_fractions_container_description_schema,
    ),
    "ReferencedTracersMassFractionsContainerDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.REFERENCED_TRACERS_MASS_FRACTIONS_CONTAINER_DESCRIPTION,
        schema=schema.referenced_tracers_mass_fractions_container_description_schema,
    ),
    "TracersMassFractionsContainerDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.TRACERS_MASS_FRACTIONS_CONTAINER_DESCRIPTION,
        schema=schema.tracers_mass_fractions_container_description_schema,
    ),
    "CompressorPressureTableDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.COMPRESSOR_PRESSURE_TABLE_DESCRIPTION,
        schema=schema.compressor_pressure_table_description_schema,
    ),
    "ControllerInputSignalPropertiesDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.CONTROLLER_INPUT_SIGNAL_PROPERTIES_DESCRIPTION,
        schema=schema.controller_input_signal_properties_description_schema,
    ),
    "ControllerOutputSignalPropertiesDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.CONTROLLER_OUTPUT_SIGNAL_PROPERTIES_DESCRIPTION,
        schema=schema.controller_output_signal_properties_description_schema,
    ),
    "ControllerNodePropertiesDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.CONTROLLER_NODE_PROPERTIES_DESCRIPTION,
        schema=schema.controller_node_properties_description_schema,
    ),
    "LeakEquipmentDescription": AlfacaseTestConfig(
        description_expected=filled_case_descriptions.LEAK_EQUIPMENT_DESCRIPTION,
        schema=schema.leak_equipment_description_schema,
        is_dict=False,
    ),
}

ALL_CLASSES_THAT_NEEDS_SCHEMA = get_all_classes_that_needs_schema(
    case_description.CaseDescription
)

# Useful for debugging
# ALL_CLASSES_THAT_NEEDS_SCHEMA = [case_description.PvtModelCombinedDescription]


@pytest.mark.parametrize("class_", ALL_CLASSES_THAT_NEEDS_SCHEMA)
def test_convert_alfacase_to_description(alfacase_to_case_helper, class_, tmp_path):
    """
    Test to convert Alfacase from all classes of alfasim_core.simulation_models.case_description that needs a Alfacase schema
    """
    alfacase_test_config = ALFACASE_TEST_CONFIG_MAP[class_.__name__]
    file_path = tmp_path / "test_case.alfacase"
    description_obtained = alfacase_to_case_helper.generate_description(
        alfacase_test_config
    )
    description_obtained = (
        description_obtained[0]
        if alfacase_test_config.is_sequence
        else description_obtained
    )

    expected_dict = attr.asdict(alfacase_test_config.description_expected)

    description_obtained = (
        description_obtained
        if is_attrs(description_obtained)
        else description_obtained["FakeKey"]
    )
    obtained_dict = attr.asdict(description_obtained)

    # PvtModels that uses Tables has the full path, while YAML has the partial
    # The following inject the full path on the expected_dict, in order to test the obtained_dict
    def fill_pvt_table_path(values):
        if "pvt_models" in values:
            fill_pvt_table_path(values["pvt_models"])
        elif "tables" in values:
            for pvt_name in values["tables"]:
                values["tables"][pvt_name] = (
                    file_path.parent / values["tables"][pvt_name]
                )

        return values

    expected_dict = fill_pvt_table_path(expected_dict)
    # Check that generated test case is correct
    ensure_descriptions_are_equal(expected_dict, obtained_dict, IGNORED_PROPERTIES)

    # Ensure that all properties from the original Case is present in the generated test case
    alfacase_to_case_helper.ensure_description_has_all_properties(
        expected_description_class=class_, obtained_description_obj=description_obtained
    )


def test_ensure_descriptions_are_equal_compare_ndarray():
    expected_dict = {"foo": numpy.array([[1, 2], [3, 4]])}
    other_1 = {"foo": numpy.array([[0, 0], [0, 0]])}

    ensure_descriptions_are_equal(expected_dict, expected_dict, [])

    with pytest.raises(AssertionError, match="Not equal on foo"):
        ensure_descriptions_are_equal(other_1, expected_dict, [])

    with pytest.raises(AssertionError, match=r"Not equal on bar\.foo"):
        ensure_descriptions_are_equal({"bar": other_1}, {"bar": expected_dict}, [])


def test_update_multi_input_flags_behavior():
    content = strictyaml.dirty_load(
        yaml_string=textwrap.dedent(
            """\
            # Just constant, use "constant" flag.
            volumetric_flow_rates_std:
                gas:
                    value: 0.0
                    unit: sm3/d

            # Constant and curve but no flag, use default flag.
            mass_flow_rates:
                gas:
                    value: 0.0
                    unit: kg/s
            mass_flow_rates_curve:
                gas:
                    image:
                        values: [0.0, 1.0]
                        unit: kg/s
                    domain:
                        values: [0, 10]
                        unit: s

            # Just flag, use value from yaml;
            total_mass_flow_rate_input_type: curve

            # Just curve, use "curve" flag.
            water_cut_curve:
                image:
                    values: [0.2, 0.3]
                    unit: "-"
                domain:
                    values: [0, 20]
                    unit: s
            """
        ),
        schema=mass_source_node_properties_description_schema,
        allow_flow_style=True,
    )
    document = DescriptionDocument(content, Path())
    mass_source_node_properties = load_mass_source_node_properties_description(document)

    assert (
        mass_source_node_properties.volumetric_flow_rates_std_input_type
        == MultiInputType.Constant
    )
    assert (
        mass_source_node_properties.mass_flow_rates_input_type
        == MultiInputType.Constant
    )
    assert (
        mass_source_node_properties.total_mass_flow_rate_input_type
        == MultiInputType.Curve
    )
    assert mass_source_node_properties.water_cut_input_type == MultiInputType.Curve


@pytest.fixture()
def description_document_for_pvt_tables_test(tmp_path):
    case = case_description.PvtModelsDescription(
        tables={"acme": "acme.tab", "acme_2": "acme.tab"}
    )
    alfacase_string = convert_description_to_alfacase(case)
    alfacase_file_path = tmp_path / "test_case.alfacase"
    shutil.copy2(get_acme_tab_file_path(), tmp_path)
    alfacase_content = strictyaml.dirty_load(
        alfacase_string,
        schema=schema.pvt_models_description_schema,
        allow_flow_style=True,
    )
    return DescriptionDocument(content=alfacase_content, file_path=alfacase_file_path)


def test_load_pvt_tables_with_relative_file(
    description_document_for_pvt_tables_test, tmp_path
):
    """
    PvtModelsDescription.tables should accept a path relative to a tab file
    """
    document = description_document_for_pvt_tables_test
    pvt_model_description = load_pvt_models_description(document=document)

    assert pvt_model_description.tables == {
        "acme": document.file_path.parent / "acme.tab",
        "acme_2": document.file_path.parent / "acme.tab",
    }


def test_load_pvt_tables_with_absolute_file(
    description_document_for_pvt_tables_test, tmp_path
):
    """
    PvtModelsDescription.tables should accept absolute path to a tab file
    """
    document = description_document_for_pvt_tables_test

    new_folder = tmp_path / "new_folder"
    new_folder.mkdir()

    shutil.copy2(
        src=tmp_path / "acme.tab",
        dst=tmp_path / "new_folder/acme.tab",
    )

    # YAML is pointing to a valid PVT file, and is an absolute Path.
    document.content["tables"]["acme"] = YAML(
        str(document.file_path.parent / "new_folder/acme.tab")
    )

    pvt_model_description = load_pvt_models_description(document=document)
    assert pvt_model_description.tables == {
        "acme": document.file_path.parent / "new_folder/acme.tab",
        "acme_2": document.file_path.parent / "acme.tab",
    }


def test_load_pvt_tables_with_invalid_file(
    description_document_for_pvt_tables_test, tmp_path
):
    """
    PvtModelsDescription.tables should raise a RuntimError when tab file is not found.
    """
    document = description_document_for_pvt_tables_test

    # YAML pointing to a invalid PVT model file
    document.content["tables"]["gavea"] = YAML("Foo.tab")

    expected_msg = (
        "The PVT Table Foo.tab must be place within the test_case.alfacase file on *"
    )
    with pytest.raises(RuntimeError, match=expected_msg):
        load_pvt_models_description(document=document)


def test_load_pvt_tables_with_pvt_model_selector(
    description_document_for_pvt_tables_test, tmp_path
):
    """
    PvtModelsDescription.tables should provide a way to the user select one of multiples pvt models that are inside the file
    This syntax can be used either for absolute path or relative path

    # Ex.: " <tab_file> | <pvt_model_name> "
    """
    document = description_document_for_pvt_tables_test

    document.content["tables"]["acme"] = YAML(
        str(document.file_path.parent / "acme.tab|SOMELABEL")
    )
    document.content["tables"]["acme_2"] = YAML("acme.tab|SOMELABEL")

    pvt_model_description = load_pvt_models_description(document=document)
    assert pvt_model_description.tables == {
        "acme": document.file_path.parent / "acme.tab|SOMELABEL",
        "acme_2": document.file_path.parent / "acme.tab|SOMELABEL",
    }

    # Ensure that the pvt file has the pvt_model GaveaDST
    case_description.CaseDescription(
        pvt_models=pvt_model_description
    ).ensure_valid_references()


def test_get_array_loader():
    alfacase_content = YAML(
        value={"foo": {"values": YAML(value=[1, 2]), "unit": YAML(value="m")}}
    )
    description_document = DescriptionDocument(
        content=alfacase_content, file_path=Path()
    )
    # Loading Scalar passing ``category``
    array_loader = get_array_loader(category="length")
    assert array_loader(key="foo", alfacase_content=description_document) == Array(
        "length", [1.0, 2.0], "m"
    )

    # Load Scalar passing ``from_unit``
    array_loader = get_array_loader(from_unit="m")
    assert array_loader(key="foo", alfacase_content=description_document) == Array(
        "length", [1.0, 2.0], "m"
    )

    expected_msg = "Either 'category' or 'from_unit' parameter must be defined"
    with pytest.raises(ValueError, match=expected_msg):
        get_array_loader()


def test_get_scalar_loader():
    alfacase_content = YAML(
        value={"foo": {"value": YAML(value=1), "unit": YAML(value="m")}}
    )
    description_document = DescriptionDocument(
        content=alfacase_content, file_path=Path()
    )

    # Loading Scalar passing ``category``
    scalar_loader = get_scalar_loader(category="length")
    assert scalar_loader(key="foo", alfacase_content=description_document) == Scalar(
        1.0, "m", "length"
    )

    # Load Scalar passing ``from_unit``
    scalar_loader = get_scalar_loader(from_unit="m")
    assert scalar_loader(key="foo", alfacase_content=description_document) == Scalar(
        1.0, "m", "length"
    )

    # Passing None
    expected_msg = "Either 'category' or 'from_unit' parameter must be defined"
    with pytest.raises(ValueError, match=expected_msg):
        get_scalar_loader()

    # Informing both parameter
    expected_msg = "Both parameters 'category' and 'from_unit' were provided, only one must be informed"
    with pytest.raises(ValueError, match=expected_msg):
        get_scalar_loader(category="length", from_unit="m")


def test_convert_alfacase_to_description_restart_file_path(tmp_path):
    """
    Round-trip test with a description that has a Path as type.
        - YAML representation should be a Str()
        - CaseDescription should be a pathlib.Path
    """

    alfacase_file = tmp_path / "test_case.yaml"
    some_folder = tmp_path / "some_folder"
    some_folder.mkdir()
    restart_file = some_folder / "restart.state"
    restart_file.touch()

    physics_with_restart_file = attr.evolve(
        filled_case_descriptions.PHYSICS_DESCRIPTION, restart_filepath=restart_file
    )

    alfacase_string = convert_description_to_alfacase(physics_with_restart_file)
    restart_file_relative_path = restart_file.relative_to(alfacase_file.parent)
    assert f"restart_filepath: {restart_file.absolute()}" in alfacase_string
    alfacase_string = alfacase_string.replace(
        f"restart_filepath: {restart_file.absolute()}",
        f"restart_filepath: {restart_file_relative_path}",
    )

    alfacase_content = strictyaml.dirty_load(
        yaml_string=alfacase_string,
        schema=schema.physics_description_schema,
        allow_flow_style=True,
    )

    assert isinstance(alfacase_content["restart_filepath"].value, str)
    assert alfacase_content["restart_filepath"].value == str(
        Path("some_folder/restart.state")
    )

    description_document = DescriptionDocument(
        content=alfacase_content, file_path=alfacase_file
    )
    physics_description = load_physics_description(description_document)
    assert physics_description.restart_filepath == restart_file


def test_invalid_yaml_contents_parsing(tmp_path):
    """
    Errors while parsing YAML should be detected and raised as our custom exception.
    """
    import re

    alfacase_content = "Invalid YAML contents"
    alfacase_file = tmp_path / "invalid-yaml.alfacase"
    alfacase_file.write_text(data=alfacase_content, encoding="UTF-8")

    expected_msg = (
        "when expecting a mapping\n"
        '  in "<unicode string>", line 1, column 1:\n'
        "    Invalid YAML contents\n"
        "     ^ (line: 1)\n"
        "found arbitrary text\n"
        '  in "<unicode string>", line 2, column 1:\n'
        "    ...\n"
        "    ^ (line: 2)"
    )

    with pytest.raises(DescriptionError, match=re.escape(expected_msg)):
        DescriptionDocument.from_file(alfacase_file)


def test_get_case_description_attribute_loader_dict_explicit_loaders() -> None:
    def fake_explict_loader(*args, **kwargs):
        """No-op"""

    loaders_with_explicit_loaders = (
        alfacase_to_case.get_case_description_attribute_loader_dict(
            case_description.BipDescription,
            explicit_loaders={"component_1": fake_explict_loader},
        )
    )
    component_1_explicit_loader = loaders_with_explicit_loaders.pop("component_1")

    loaders = alfacase_to_case.get_case_description_attribute_loader_dict(
        case_description.BipDescription
    )
    component_1_automatic_loader = loaders.pop("component_1")

    assert loaders_with_explicit_loaders == loaders
    assert component_1_explicit_loader is fake_explict_loader
    assert component_1_automatic_loader is alfacase_to_case.load_value
