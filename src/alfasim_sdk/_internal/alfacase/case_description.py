from numbers import Number
from pathlib import Path
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union

import attr
import numpy as np
from attr.validators import in_
from attr.validators import instance_of
from attr.validators import optional
from barril.curve.curve import Curve
from barril.units import Array
from barril.units import Scalar

from .case_description_attributes import attrib_array
from .case_description_attributes import attrib_curve
from .case_description_attributes import attrib_dict_of
from .case_description_attributes import attrib_enum
from .case_description_attributes import attrib_instance
from .case_description_attributes import attrib_instance_list
from .case_description_attributes import attrib_scalar
from .case_description_attributes import collapse_array_repr
from .case_description_attributes import dict_of
from .case_description_attributes import dict_of_array
from .case_description_attributes import dict_with_scalar
from .case_description_attributes import InvalidReferenceError
from .case_description_attributes import list_of_strings
from .case_description_attributes import Numpy1DArray
from .case_description_attributes import numpy_array_validator
from .case_description_attributes import PhaseName
from alfasim_sdk._internal import constants

# [[[cog
# # This cog has no output, it just declares and imports symbols used by cogs in this module.
#
# from alfasim_sdk._internal import constants
# from alfasim_sdk._internal.alfacase.case_description_attributes import generate_multi_input
# from alfasim_sdk._internal.alfacase.case_description_attributes import generate_multi_input_dict
#
# def cog_out_multi_input(prop_name, category, default_value, unit):
#   code = generate_multi_input(prop_name, category, default_value, unit)
#   cog.out(code)
#
# def cog_out_multi_input_dict(prop_name, category):
#   code = generate_multi_input_dict(prop_name, category)
#   cog.out(code)
#
# ]]]
# [[[end]]] (checksum: d41d8cd98f00b204e9800998ecf8427e)


@attr.s(frozen=True, slots=True)
class PluginDescription:
    name: Optional[str] = attr.ib(default=None, validator=optional(instance_of(str)))
    gui_models = attr.ib(default=attr.Factory(dict))
    additional_variables = attr.ib(default=None)


@attr.s(frozen=True, slots=True)
class PluginTracerReference:
    tracer_id = attr.ib(default=None)


@attr.s(frozen=True, slots=True)
class PluginInternalReference:
    plugin_item_id = attr.ib(default=None)


@attr.s(frozen=True, slots=True)
class PluginMultipleReference:
    container_key = attr.ib(default=None)
    item_id_list = attr.ib(default=attr.Factory(list))


@attr.s(frozen=True, slots=True)
class PluginTableContainer:
    columns = attr.ib(default=attr.Factory(dict))


@attr.s(frozen=True, slots=True)
class SurgeVolumeOptionsDescription:
    """
    .. include:: /alfacase_definitions/SurgeVolumeOptionsDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_time.txt
    .. include:: /alfacase_definitions/list_of_unit_for_volume_flow_rate.txt
    """

    time_mode = attrib_enum(
        type_=constants.SurgeVolumeTimeMode,
        default=constants.SurgeVolumeTimeMode.AllSimulation,
    )
    drainage_mode = attrib_enum(
        type_=constants.DrainageRateMode, default=constants.DrainageRateMode.Automatic
    )
    start_time = attrib_scalar(category="time", is_optional=True, default=None)
    end_time = attrib_scalar(category="time", is_optional=True, default=None)
    maximum_drainage_rate = attrib_scalar(
        category="volume flow rate", is_optional=True, default=None
    )


@attr.s(kw_only=True)
class _BaseTrendOutputDescription:
    name: Optional[str] = attr.ib(default=None, validator=optional(instance_of(str)))
    curve_names: List[str] = attr.ib(validator=list_of_strings)


@attr.s()
class PositionalPipeTrendDescription(_BaseTrendOutputDescription):
    """
    .. include:: /alfacase_definitions/PositionalPipeTrendDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    """

    location = attrib_enum(type_=constants.OutputAttachmentLocation)
    position = attrib_scalar(category="length")
    element_name: str = attr.ib(validator=instance_of(str))
    surge_volume_options = attrib_instance(SurgeVolumeOptionsDescription)


@attr.s()
class GlobalTrendDescription(_BaseTrendOutputDescription):
    """
    .. include:: /alfacase_definitions/GlobalTrendDescription.txt
    """


@attr.s()
class OverallPipeTrendDescription(_BaseTrendOutputDescription):
    """
    .. include:: /alfacase_definitions/OverallPipeTrendDescription.txt
    """

    location = attrib_enum(type_=constants.OutputAttachmentLocation)
    element_name: str = attr.ib(validator=instance_of(str))


@attr.s()
class EquipmentTrendDescription(_BaseTrendOutputDescription):
    """
    .. include:: /alfacase_definitions/EquipmentTrendDescription.txt
    """

    element_name: str = attr.ib(validator=instance_of(str))


@attr.s()
class SeparatorTrendDescription(_BaseTrendOutputDescription):
    """
    .. include:: /alfacase_definitions/SeparatorTrendDescription.txt
    """

    element_name: str = attr.ib(validator=instance_of(str))


@attr.s()
class ProfileOutputDescription:
    """
    .. include:: /alfacase_definitions/ProfileOutputDescription.txt
    """

    curve_names: List[str] = attr.ib(validator=list_of_strings)
    location = attrib_enum(type_=constants.OutputAttachmentLocation)
    element_name: str = attr.ib(validator=optional(instance_of(str)))


@attr.s()
class TrendsOutputDescription:
    """
    .. include:: /alfacase_definitions/TrendsOutputDescription.txt
    """

    positional_pipe_trends = attrib_instance_list(PositionalPipeTrendDescription)
    overall_pipe_trends = attrib_instance_list(OverallPipeTrendDescription)
    global_trends = attrib_instance_list(GlobalTrendDescription)
    equipment_trends = attrib_instance_list(EquipmentTrendDescription)
    separator_trends = attrib_instance_list(SeparatorTrendDescription)


@attr.s(frozen=True, slots=True)
class CaseOutputDescription:
    """
    .. include:: /alfacase_definitions/CaseOutputDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_time.txt
    """

    automatic_trend_frequency: bool = attr.ib(default=True, validator=instance_of(bool))
    trends = attrib_instance(TrendsOutputDescription)
    trend_frequency = attrib_scalar(default=Scalar(0.1, "s"))
    automatic_profile_frequency: bool = attr.ib(
        default=True, validator=instance_of(bool)
    )
    profiles = attrib_instance_list(ProfileOutputDescription)
    profile_frequency = attrib_scalar(default=Scalar(0.1, "s"))


@attr.s(kw_only=True)
class _MassSourceCommon:
    """
    :ivar total_mass_flow_rate:
        Used when source_type == constants.MassSourceType.TotalMassFlowRatePvtSplit

    :ivar mass_flow_rates:
        Used when source_type == constants.MassSourceType.MassFlowRates

    :ivar gas_oil_ratio:
        Used when source_type is one of:
            - constants.MassSourceType.FlowRateGasGorWc
            - constants.MassSourceType.FlowRateOilGorWc
            - constants.MassSourceType.FlowRateWaterGorWc

    :ivar volumetric_flow_rates_std:
        Used when source_type is one of:
            - AllVolumetricFlowRates                        (All phases are filled)
            - constants.MassSourceType.FlowRateGasGorWc     (Only the Gas phase if filled)
            - constants.MassSourceType.FlowRateOilGorWc     (Only the Oil phase if filled)
            - constants.MassSourceType.FlowRateWaterGorWc   (Only the Water phase if filled)

    :ivar water_cut:
        Used when the Hydrodynamic model has Water phase and source_type is one of:
            - constants.MassSourceType.FlowRateGasGorWc
            - constants.MassSourceType.FlowRateOilGorWc
            - constants.MassSourceType.FlowRateWaterGorWc

    .. include:: /alfacase_definitions/list_of_unit_for_temperature.txt
    .. include:: /alfacase_definitions/list_of_unit_for_volume_flow_rate.txt
    .. include:: /alfacase_definitions/list_of_unit_for_mass_flow_rate.txt
    .. include:: /alfacase_definitions/list_of_unit_for_volume_fraction.txt
    .. include:: /alfacase_definitions/list_of_unit_for_standard_volume_per_standard_volume.txt
    """

    fluid: Optional[str] = attr.ib(default=None, validator=optional(instance_of(str)))
    tracer_mass_fraction: Array = attr.ib(
        default=Array([], "-"),
        validator=instance_of(Array),
        metadata={"type": "array", "category": "mass fraction"},
    )

    # [[[cog
    # cog_out_multi_input("temperature", "temperature", constants.DEFAULT_TEMPERATURE_IN_K, "K")
    # ]]]
    # fmt: off
    temperature_input_type = attrib_enum(default=constants.MultiInputType.Constant)
    temperature = attrib_scalar(
        default=Scalar('temperature', 288.6, 'K')
    )
    temperature_curve = attrib_curve(
        default=Curve(Array('temperature', [], 'K'), Array('time', [], 's'))
    )
    # fmt: on
    # [[[end]]] (checksum: cfa3eacaa542b1544f9501cfc1bbc800)

    source_type = attrib_enum(default=constants.MassSourceType.MassFlowRates)

    # [[[cog
    # cog_out_multi_input_dict("volumetric_flow_rates_std", "standard volume per time")
    # ]]]
    # fmt: off
    volumetric_flow_rates_std_input_type = attrib_enum(default=constants.MultiInputType.Constant)
    volumetric_flow_rates_std: Dict[str, Scalar] = attr.ib(
        default=attr.Factory(dict), validator=dict_of(Scalar),
        metadata={"type": "scalar_dict", "category": 'standard volume per time'},
    )
    volumetric_flow_rates_std_curve: Dict[str, Curve] = attr.ib(
        default=attr.Factory(dict), validator=dict_of(Curve),
        metadata={"type": "curve_dict", "category": 'standard volume per time'},
    )
    # fmt: on
    # [[[end]]] (checksum: 90ffdd6b31ca61d3a254a2a4163470b5)

    # [[[cog
    # cog_out_multi_input_dict("mass_flow_rates", "mass flow rate")
    # ]]]
    # fmt: off
    mass_flow_rates_input_type = attrib_enum(default=constants.MultiInputType.Constant)
    mass_flow_rates: Dict[str, Scalar] = attr.ib(
        default=attr.Factory(dict), validator=dict_of(Scalar),
        metadata={"type": "scalar_dict", "category": 'mass flow rate'},
    )
    mass_flow_rates_curve: Dict[str, Curve] = attr.ib(
        default=attr.Factory(dict), validator=dict_of(Curve),
        metadata={"type": "curve_dict", "category": 'mass flow rate'},
    )
    # fmt: on
    # [[[end]]] (checksum: 14466fad7202e819caa161ebf875697c)

    # [[[cog
    # cog_out_multi_input("total_mass_flow_rate", "mass flow rate", 1.0, "kg/s")
    # ]]]
    # fmt: off
    total_mass_flow_rate_input_type = attrib_enum(default=constants.MultiInputType.Constant)
    total_mass_flow_rate = attrib_scalar(
        default=Scalar('mass flow rate', 1.0, 'kg/s')
    )
    total_mass_flow_rate_curve = attrib_curve(
        default=Curve(Array('mass flow rate', [], 'kg/s'), Array('time', [], 's'))
    )
    # fmt: on
    # [[[end]]] (checksum: 311c423906e498a67edbf00f8ef5779d)

    # [[[cog
    # cog_out_multi_input("water_cut", "volume fraction", 0.0, "-")
    # ]]]
    # fmt: off
    water_cut_input_type = attrib_enum(default=constants.MultiInputType.Constant)
    water_cut = attrib_scalar(
        default=Scalar('volume fraction', 0.0, '-')
    )
    water_cut_curve = attrib_curve(
        default=Curve(Array('volume fraction', [], '-'), Array('time', [], 's'))
    )
    # fmt: on
    # [[[end]]] (checksum: fd5599325fa31c6221db6f11e2fc1123)

    # [[[cog
    # cog_out_multi_input("gas_oil_ratio", "standard volume per standard volume", 0.0, "sm3/sm3")
    # ]]]
    # fmt: off
    gas_oil_ratio_input_type = attrib_enum(default=constants.MultiInputType.Constant)
    gas_oil_ratio = attrib_scalar(
        default=Scalar('standard volume per standard volume', 0.0, 'sm3/sm3')
    )
    gas_oil_ratio_curve = attrib_curve(
        default=Curve(Array('standard volume per standard volume', [], 'sm3/sm3'), Array('time', [], 's'))
    )
    # fmt: on
    # [[[end]]] (checksum: 0cc220bf4175710b45e45e6f4cc58ddd)


@attr.s(kw_only=True)
class _PressureSourceCommon:
    """

    .. include:: /alfacase_definitions/list_of_unit_for_pressure.txt
    .. include:: /alfacase_definitions/list_of_unit_for_temperature.txt
    .. include:: /alfacase_definitions/list_of_unit_for_mass_fraction.txt
    .. include:: /alfacase_definitions/list_of_unit_for_volume_fraction.txt
    .. include:: /alfacase_definitions/list_of_unit_for_standard_volume_per_standard_volume.txt
    """

    # [[[cog
    # cog_out_multi_input("pressure", "pressure", 1.0e5, "Pa")
    # ]]]
    # fmt: off
    pressure_input_type = attrib_enum(default=constants.MultiInputType.Constant)
    pressure = attrib_scalar(
        default=Scalar('pressure', 100000.0, 'Pa')
    )
    pressure_curve = attrib_curve(
        default=Curve(Array('pressure', [], 'Pa'), Array('time', [], 's'))
    )
    # fmt: on
    # [[[end]]] (checksum: 31e9f12ceb2313cace8f856fc15581a5)

    # [[[cog
    # cog_out_multi_input("temperature", "temperature", constants.DEFAULT_TEMPERATURE_IN_K, "K")
    # ]]]
    # fmt: off
    temperature_input_type = attrib_enum(default=constants.MultiInputType.Constant)
    temperature = attrib_scalar(
        default=Scalar('temperature', 288.6, 'K')
    )
    temperature_curve = attrib_curve(
        default=Curve(Array('temperature', [], 'K'), Array('time', [], 's'))
    )
    # fmt: on
    # [[[end]]] (checksum: cfa3eacaa542b1544f9501cfc1bbc800)

    fluid: Optional[str] = attr.ib(default=None, validator=optional(instance_of(str)))

    tracer_mass_fraction: Array = attr.ib(
        default=Array([], "-", "mass fraction"),
        validator=instance_of(Array),
        metadata={"type": "array", "category": "mass fraction"},
    )

    split_type = attrib_enum(
        default=constants.MassInflowSplitType.ConstantVolumeFraction
    )

    # [[[cog
    # cog_out_multi_input_dict("mass_fractions", "mass fraction")
    # ]]]
    # fmt: off
    mass_fractions_input_type = attrib_enum(default=constants.MultiInputType.Constant)
    mass_fractions: Dict[str, Scalar] = attr.ib(
        default=attr.Factory(dict), validator=dict_of(Scalar),
        metadata={"type": "scalar_dict", "category": 'mass fraction'},
    )
    mass_fractions_curve: Dict[str, Curve] = attr.ib(
        default=attr.Factory(dict), validator=dict_of(Curve),
        metadata={"type": "curve_dict", "category": 'mass fraction'},
    )
    # fmt: on
    # [[[end]]] (checksum: cc96caed7be4897551ce0afd2c3af9f8)

    # [[[cog
    # cog_out_multi_input_dict("volume_fractions", "volume fraction")
    # ]]]
    # fmt: off
    volume_fractions_input_type = attrib_enum(default=constants.MultiInputType.Constant)
    volume_fractions: Dict[str, Scalar] = attr.ib(
        default=attr.Factory(dict), validator=dict_of(Scalar),
        metadata={"type": "scalar_dict", "category": 'volume fraction'},
    )
    volume_fractions_curve: Dict[str, Curve] = attr.ib(
        default=attr.Factory(dict), validator=dict_of(Curve),
        metadata={"type": "curve_dict", "category": 'volume fraction'},
    )
    # fmt: on
    # [[[end]]] (checksum: 73f1389ef2912c079dc3fad3cec8334b)

    # [[[cog
    # cog_out_multi_input("gas_liquid_ratio", "standard volume per standard volume", 0.0, "sm3/sm3")
    # ]]]
    # fmt: off
    gas_liquid_ratio_input_type = attrib_enum(default=constants.MultiInputType.Constant)
    gas_liquid_ratio = attrib_scalar(
        default=Scalar('standard volume per standard volume', 0.0, 'sm3/sm3')
    )
    gas_liquid_ratio_curve = attrib_curve(
        default=Curve(Array('standard volume per standard volume', [], 'sm3/sm3'), Array('time', [], 's'))
    )
    # fmt: on
    # [[[end]]] (checksum: 8799b62448023477ae46a4351289a493)

    # [[[cog
    # cog_out_multi_input("gas_oil_ratio", "standard volume per standard volume", 0.0, "sm3/sm3")
    # ]]]
    # fmt: off
    gas_oil_ratio_input_type = attrib_enum(default=constants.MultiInputType.Constant)
    gas_oil_ratio = attrib_scalar(
        default=Scalar('standard volume per standard volume', 0.0, 'sm3/sm3')
    )
    gas_oil_ratio_curve = attrib_curve(
        default=Curve(Array('standard volume per standard volume', [], 'sm3/sm3'), Array('time', [], 's'))
    )
    # fmt: on
    # [[[end]]] (checksum: 0cc220bf4175710b45e45e6f4cc58ddd)

    # [[[cog
    # cog_out_multi_input("water_cut", "volume fraction", 0.0, "-")
    # ]]]
    # fmt: off
    water_cut_input_type = attrib_enum(default=constants.MultiInputType.Constant)
    water_cut = attrib_scalar(
        default=Scalar('volume fraction', 0.0, '-')
    )
    water_cut_curve = attrib_curve(
        default=Curve(Array('volume fraction', [], '-'), Array('time', [], 's'))
    )
    # fmt: on
    # [[[end]]] (checksum: fd5599325fa31c6221db6f11e2fc1123)


@attr.s(frozen=True, slots=True)
class CompositionDescription:
    """
    :ivar component:
        Name of the component available created on:
            PvtModelCompositionalDescription.light_components
            PvtModelCompositionalDescription.heavy_components

        .. note:: CompositionDescription can only refer to components created from the same PvtModelCompositionalDescription

    .. include:: /alfacase_definitions/CompositionDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_mole_per_mole.txt
    .. include:: /alfacase_definitions/list_of_unit_for_molar_thermodynamic_energy.txt

    """

    component: str = attr.ib(validator=instance_of(str))
    molar_fraction = attrib_scalar(default=Scalar(0, "mol/mol"))
    reference_enthalpy = attrib_scalar(default=Scalar(0, "J/mol"))


@attr.s(frozen=True, slots=True)
class BipDescription:
    """
    .. include:: /alfacase_definitions/BipDescription.txt
    """

    component_1: str = attr.ib(validator=instance_of(str))
    component_2: str = attr.ib(validator=instance_of(str))
    value: float = attr.ib(validator=instance_of(float), converter=float)


@attr.s(frozen=True, slots=True)
class FluidDescription:
    """
    .. include:: /alfacase_definitions/FluidDescription.txt
    """

    composition = attrib_instance_list(CompositionDescription)
    fraction_pairs = attrib_instance_list(BipDescription)


@attr.s(slots=True, kw_only=True)
class MassSourceEquipmentDescription(_MassSourceCommon):
    """
    .. include:: /alfacase_definitions/MassSourceEquipmentDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    """

    position = attrib_scalar(category="length")


@attr.s(frozen=True, slots=True, kw_only=True)
class SpeedCurveDescription:
    """
    .. include:: /alfacase_definitions/SpeedCurveDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    .. include:: /alfacase_definitions/list_of_unit_for_angle_per_time.txt

    """

    time = attrib_array(Array([0], "s"))
    speed = attrib_array(Array([500], "rpm"))


# fmt: off
@attr.s(frozen=True, slots=True, kw_only=True)
class TablePumpDescription:
    """
    .. include:: /alfacase_definitions/TablePumpDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_angle_per_time.txt
    .. include:: /alfacase_definitions/list_of_unit_for_volume_flow_rate.txt
    .. include:: /alfacase_definitions/list_of_unit_for_volume_fraction.txt
    .. include:: /alfacase_definitions/list_of_unit_for_pressure.txt
    """
    speeds = attrib_array(Array([0.0] * 12 + [400.0] * 12 + [600.0] * 12, 'rpm'))
    void_fractions = attrib_array(Array(([0.0] * 6 + [0.1] * 6) * 3, '-'))
    flow_rates = attrib_array(Array([0.0, 0.05, 0.1, 0.15, 0.2, 0.3] * 6, 'm3/s'))

    pressure_boosts = attrib_array(Array(
            [0.0] * 12
            +[
                12.0, 10.0, 9.0, 7.5, 5.0, 0.0, 10.0, 9.0, 8.0, 6.0, 3.5, 0.0,
                14.0, 12.0, 10.0, 8.0, 5.5, 0.0, 13.5, 11.2, 9.5, 7.6, 5.2, 0.0,
            ],
            'bar',
        )
    )

    def __attrs_post_init__(self):
        expected_length = len(self.speeds)
        all_fields = list(attr.fields_dict(self.__class__).keys())
        if any(len(getattr(self, field)) != expected_length for field in all_fields):
            msg = (
                f"speeds, void_fractions, flow_rates and pressure_boosts must have the same size, got:\n"
                f"    - {len(self.speeds)} items for speeds\n"
                f"    - {len(self.void_fractions)} items for void_fractions\n"
                f"    - {len(self.flow_rates)} items for flow_rates\n"
                f"    - {len(self.pressure_boosts)} items for pressure_boosts\n"
            )
            raise ValueError(msg)

# fmt: on


@attr.s(frozen=True, slots=True)
class PumpEquipmentDescription:
    """
    .. include:: /alfacase_definitions/PumpEquipmentDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    .. include:: /alfacase_definitions/list_of_unit_for_pressure.txt
    .. include:: /alfacase_definitions/list_of_unit_for_dimensionless.txt
    """

    position = attrib_scalar(category="length")
    type = attrib_enum(default=constants.PumpType.ConstantPressure)
    pressure_boost = attrib_scalar(default=Scalar(1.0e5, "Pa"))
    thermal_efficiency = attrib_scalar(default=Scalar(100.0, "%"))
    table = attrib_instance(TablePumpDescription)
    speed_curve = attrib_instance(SpeedCurveDescription)
    speed_curve_interpolation_type = attrib_enum(
        default=constants.InterpolationType.Constant
    )
    flow_direction = attrib_enum(default=constants.FlowDirection.Forward)


@attr.s(frozen=True, slots=True)
class CompressorPressureTableDescription:
    """
    :ivar corrected_mass_flow_rate_entries:
        Equivalent to `m * (T/T_ref)**0.5 / (P/P_ref)`

    .. include:: /alfacase_definitions/CompressorPressureTableDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_angle_per_time.txt
    .. include:: /alfacase_definitions/list_of_unit_for_mass_flow_rate.txt
    .. include:: /alfacase_definitions/list_of_unit_for_dimensionless.txt
    """

    speed_entries = attrib_array(Array([0], "rpm"))
    corrected_mass_flow_rate_entries = attrib_array(Array([0], "kg/s"))
    pressure_ratio_table = attrib_array(Array([1.0], "-"))
    isentropic_efficiency_table = attrib_array(Array([1.0], "-"))

    def __attrs_post_init__(self):
        expected_length = len(self.speed_entries)
        all_fields = list(attr.fields_dict(self.__class__).keys())
        if any(len(getattr(self, field)) != expected_length for field in all_fields):
            msg = (
                f"speed_entries, corrected_mass_flow_rate_entries, pressure_ratio_table and isentropic_efficiency_table must have the same size, got:\n"
                f"    - {len(self.speed_entries)} items for speed_entries\n"
                f"    - {len(self.corrected_mass_flow_rate_entries)} items for corrected_mass_flow_rate_entries\n"
                f"    - {len(self.pressure_ratio_table)} items for pressure_ratio_table\n"
                f"    - {len(self.isentropic_efficiency_table)} items for isentropic_efficiency_table\n"
            )
            raise ValueError(msg)

    @pressure_ratio_table.validator
    def _validate_pressure_ratio_table(self, attribute, value):
        pressure_ratio = np.array(value.GetValues("-"))
        assert np.all(pressure_ratio > 0), "Pressure Ratio must be greater than 0"

    @isentropic_efficiency_table.validator
    def _validate_isentropic_efficiency_table(self, attribute, value):
        isen_eff = np.array(value.GetValues("-"))
        assert np.all(
            np.logical_and(isen_eff > 0, isen_eff <= 1.0)
        ), "Isentropic efficiency must be greater than 0 and lower or equal to 1"


@attr.s(frozen=True, slots=True)
class CompressorEquipmentDescription:
    """
    .. include:: /alfacase_definitions/CompressorEquipmentDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    .. include:: /alfacase_definitions/list_of_unit_for_pressure.txt
    .. include:: /alfacase_definitions/list_of_unit_for_temperature.txt
    .. include:: /alfacase_definitions/list_of_unit_for_angle_per_time.txt
    """

    position = attrib_scalar(category="length")
    speed_curve = attrib_instance(SpeedCurveDescription)
    reference_pressure = attrib_scalar(default=Scalar(1.0, "bar"))
    reference_temperature = attrib_scalar(default=Scalar(25, "degC"))
    constant_speed = attrib_scalar(default=Scalar(500, "rpm"))
    compressor_type = attrib_enum(default=constants.CompressorSpeedType.SpeedCurve)
    speed_curve_interpolation_type = attrib_enum(
        default=constants.InterpolationType.Constant
    )
    flow_direction = attrib_enum(default=constants.FlowDirection.Forward)
    table = attrib_instance(CompressorPressureTableDescription)


@attr.s(frozen=True, slots=True)
class CvTableDescription:
    """
    .. include:: /alfacase_definitions/CvTableDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_dimensionless.txt
    .. include:: /alfacase_definitions/list_of_unit_for_flow_coefficient.txt
    """

    opening = attrib_array(default=Array([], "-"))
    flow_coefficient = attrib_array(default=Array([], "(galUS/min)/(psi^0.5)"))

    def __attrs_post_init__(self):
        if len(self.flow_coefficient) != len(self.opening):
            msg = (
                f"Opening and Flow Coefficient must have the same size, got {len(self.flow_coefficient)} "
                f"items for flow_coefficient and {len(self.opening)} for opening"
            )
            raise ValueError(msg)


@attr.s(frozen=True, slots=True)
class PigEquipmentDescription:
    """
    .. include:: /alfacase_definitions/PigEquipmentDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    .. include:: /alfacase_definitions/list_of_unit_for_mass.txt
    .. include:: /alfacase_definitions/list_of_unit_for_force.txt
    .. include:: /alfacase_definitions/list_of_unit_for_force_per_velocity.txt
    .. include:: /alfacase_definitions/list_of_unit_for_force_per_velocity_squared.txt
    """

    diameter = attrib_scalar(category="diameter")
    position = attrib_scalar(category="length")

    launch_times = attrib_array(default=Array([0.0], "s"))

    # [[[cog
    # cog_out_multi_input("mass", "mass", 140.0, "kg")
    # ]]]
    # fmt: off
    mass_input_type = attrib_enum(default=constants.MultiInputType.Constant)
    mass = attrib_scalar(
        default=Scalar('mass', 140.0, 'kg')
    )
    mass_curve = attrib_curve(
        default=Curve(Array('mass', [], 'kg'), Array('time', [], 's'))
    )
    # fmt: on
    # [[[end]]] (checksum: a7bf92b6669c03c650b80056852aa630)

    # [[[cog
    # cog_out_multi_input("static_force", "force", 1000.0, "N")
    # ]]]
    # fmt: off
    static_force_input_type = attrib_enum(default=constants.MultiInputType.Constant)
    static_force = attrib_scalar(
        default=Scalar('force', 1000.0, 'N')
    )
    static_force_curve = attrib_curve(
        default=Curve(Array('force', [], 'N'), Array('time', [], 's'))
    )
    # fmt: on
    # [[[end]]] (checksum: 5a557bb3367d5632e14723da23d9f35a)

    # [[[cog
    # cog_out_multi_input("wall_friction", "force per velocity", 1000.0, "N.s/m")
    # ]]]
    # fmt: off
    wall_friction_input_type = attrib_enum(default=constants.MultiInputType.Constant)
    wall_friction = attrib_scalar(
        default=Scalar('force per velocity', 1000.0, 'N.s/m')
    )
    wall_friction_curve = attrib_curve(
        default=Curve(Array('force per velocity', [], 'N.s/m'), Array('time', [], 's'))
    )
    # fmt: on
    # [[[end]]] (checksum: eac7071ce8c5158f10592694891eef3c)

    # [[[cog
    # cog_out_multi_input("linear_friction", "force per velocity", 10.0, "N.s/m")
    # ]]]
    # fmt: off
    linear_friction_input_type = attrib_enum(default=constants.MultiInputType.Constant)
    linear_friction = attrib_scalar(
        default=Scalar('force per velocity', 10.0, 'N.s/m')
    )
    linear_friction_curve = attrib_curve(
        default=Curve(Array('force per velocity', [], 'N.s/m'), Array('time', [], 's'))
    )
    # fmt: on
    # [[[end]]] (checksum: c1db146868277c945f0290b3de6c1ac1)

    # [[[cog
    # cog_out_multi_input("quadratic_friction", "force per velocity squared", 0.0, "N.s2/m2")
    # ]]]
    # fmt: off
    quadratic_friction_input_type = attrib_enum(default=constants.MultiInputType.Constant)
    quadratic_friction = attrib_scalar(
        default=Scalar('force per velocity squared', 0.0, 'N.s2/m2')
    )
    quadratic_friction_curve = attrib_curve(
        default=Curve(Array('force per velocity squared', [], 'N.s2/m2'), Array('time', [], 's'))
    )
    # fmt: on
    # [[[end]]] (checksum: 57937de27b34d2f159ecce17563ba34d)

    trap_mode = attrib_enum(default=constants.PigTrappingMode.Automatic)
    trap_position = attrib_scalar(default=Scalar(0.0, "m"), category="length")
    trap_pipe_name: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )
    route_mode = attrib_enum(default=constants.PigRoutingMode.Automatic)
    pipe_route_names: Optional[List[str]] = attr.ib(
        default=None, validator=optional(list_of_strings)
    )

    @diameter.validator
    def _validate_diameter(self, attribute, value):
        assert (
            isinstance(value, Scalar) and value.GetCategory() == "diameter"
        ), "Invalid diameter"


@attr.s(frozen=True, slots=True)
class ValveEquipmentDescription:
    """
    .. include:: /alfacase_definitions/ValveEquipmentDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    .. include:: /alfacase_definitions/list_of_unit_for_dimensionless.txt
    """

    position = attrib_scalar(category="length")
    type = attrib_enum(default=constants.ValveType.PerkinsValve)
    diameter = attrib_scalar(default=Scalar("diameter", 0.01, "m"))
    flow_direction = attrib_enum(default=constants.FlowDirection.Forward)

    # When ValveType is not CheckValve
    opening_type = attrib_enum(default=constants.ValveOpeningType.ConstantOpening)
    # --> When ValveOpeningType.ConstantOpening
    opening = attrib_scalar(default=Scalar("dimensionless", 100, "%"))
    # --> When ValveOpeningType.TableInterpolation
    opening_curve_interpolation_type = attrib_enum(
        default=constants.InterpolationType.Constant
    )
    opening_curve = attrib_curve(
        default=Curve(Array("dimensionless", [], "-"), Array("time", [], "s"))
    )
    # When ValveType.ChokeValveWithFlowCoefficient
    cv_table = attrib_instance(CvTableDescription)

    @diameter.validator
    def _validate_diameter(self, attribute, value):
        assert (
            isinstance(value, Scalar) and value.GetCategory() == "diameter"
        ), "Invalid diameter"


@attr.s(frozen=True, slots=True)
class LeakEquipmentDescription:
    """
    .. include:: /alfacase_definitions/LeakEquipmentDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    .. include:: /alfacase_definitions/list_of_unit_for_dimensionless.txt
    """

    position = attrib_scalar(category="length")
    location = attrib_enum(default=constants.LeakLocation.Main)
    model = attrib_enum(default=constants.LeakModel.Orifice)
    type = attrib_enum(default=constants.LeakType.Internal)

    # Perkins model parameters
    diameter = attrib_scalar(default=Scalar("diameter", 0.05, "m"))
    discharge_coefficient = attrib_scalar(default=Scalar("dimensionless", 0.85, "-"))

    # Flow coefficient model parameter
    cv_table = attrib_instance(CvTableDescription)

    # Gas-Lift Valve parameters
    # diameter and discharge_coefficient are also a gas-lift valve parameter, but they are already defined
    gas_lift_valve_opening_type = attrib_enum(
        default=constants.GasLiftValveOpeningType.MinimumPressureDifference
    )

    # Gas-lift parameters of minimum pressure difference opening type
    minimum_pressure_difference = attrib_scalar(default=Scalar("pressure", 0.0, "Pa"))

    # Gas-lift parameters of pressure operated opening type
    bellows_reference_pressure = attrib_scalar(default=Scalar("pressure", 10, "bar"))
    bellows_reference_temperature = attrib_scalar(
        default=Scalar("temperature", 15, "degC")
    )
    port_to_bellows_area_ratio = attrib_scalar(
        default=Scalar("dimensionless", 0.1, "-")
    )

    # Parameters of leak opening
    # [[[cog
    # cog_out_multi_input("opening", "dimensionless", 1.0, "-")
    # ]]]
    # fmt: off
    opening_input_type = attrib_enum(default=constants.MultiInputType.Constant)
    opening = attrib_scalar(
        default=Scalar('dimensionless', 1.0, '-')
    )
    opening_curve = attrib_curve(
        default=Curve(Array('dimensionless', [], '-'), Array('time', [], 's'))
    )
    # fmt: on
    # [[[end]]] (checksum: 28bd1bf52b80d19b34c0fabcd9e93b33)

    target_pipe_name: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )
    target_position = attrib_scalar(default=Scalar(0.0, "m"))
    target_location = attrib_enum(default=constants.LeakLocation.Main)

    backflow: bool = attr.ib(default=False, validator=instance_of(bool))
    backpressure = attrib_scalar(default=Scalar(1.0, "bar"))

    @diameter.validator
    def _validate_diameter(self, attribute, value):
        assert (
            isinstance(value, Scalar) and value.GetCategory() == "diameter"
        ), "Invalid diameter"


@attr.s(frozen=True, slots=True, kw_only=True)
class IPRCurveDescription:
    """
    .. include:: /alfacase_definitions/IPRCurveDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_pressure.txt
    .. include:: /alfacase_definitions/list_of_unit_for_standard_volume_per_time.txt

    """

    pressure_difference: Array = attr.ib(
        default=Array([0.0], "Pa"), validator=instance_of(Array)
    )
    flow_rate: Array = attr.ib(
        default=Array([0.0], "sm3/d"), validator=instance_of(Array)
    )


@attr.s(frozen=True, slots=True)
class CommonIPR:
    well_index_phase = attrib_enum(default=constants.WellIndexPhaseType.Oil)


@attr.s(frozen=True, slots=True)
class LinearIPRDescription(CommonIPR):
    """
    .. include:: /alfacase_definitions/LinearIPRDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_pressure.txt
    .. include:: /alfacase_definitions/list_of_unit_for_productivity_index.txt
    """

    min_pressure_difference = attrib_scalar(default=Scalar(0.0, "Pa"))

    # [[[cog
    # cog_out_multi_input("well_index", "productivity index", 24.0, "m3/bar.d")
    # ]]]
    # fmt: off
    well_index_input_type = attrib_enum(default=constants.MultiInputType.Constant)
    well_index = attrib_scalar(
        default=Scalar('productivity index', 24.0, 'm3/bar.d')
    )
    well_index_curve = attrib_curve(
        default=Curve(Array('productivity index', [], 'm3/bar.d'), Array('time', [], 's'))
    )
    # fmt: on
    # [[[end]]] (checksum: 433953e29d06e22612c935acdbd70db4)


@attr.s(frozen=True, slots=True)
class TableIPRDescription(CommonIPR):
    """
    .. include:: /alfacase_definitions/TableIPRDescription.txt
    """

    table = attrib_instance(IPRCurveDescription)


@attr.s(frozen=True, slots=True)
class IPRModelsDescription:
    """
    :ivar linear_models:
        A dictionary with the name of the IPR and the instance of the IPR Model.

    :ivar table_models:

    .. include:: /alfacase_definitions/IPRModelsDescription.txt
    """

    linear_models: Dict[str, LinearIPRDescription] = attr.ib(
        default=attr.Factory(dict), validator=dict_of(LinearIPRDescription)
    )
    table_models: Dict[str, TableIPRDescription] = attr.ib(
        default=attr.Factory(dict), validator=dict_of(TableIPRDescription)
    )


@attr.s(slots=True)
class ReservoirInflowEquipmentDescription(_PressureSourceCommon):
    """
    .. include:: /alfacase_definitions/ReservoirInflowEquipmentDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    """

    start = attrib_scalar(category="length")
    length = attrib_scalar(category="length")
    productivity_ipr: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )
    injectivity_ipr: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )


@attr.s(frozen=True, slots=True)
class HeatSourceEquipmentDescription:
    """
    .. include:: /alfacase_definitions/HeatSourceEquipmentDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    .. include:: /alfacase_definitions/list_of_unit_for_power.txt
    """

    start = attrib_scalar(category="length")
    length = attrib_scalar(category="length")

    # [[[cog
    # cog_out_multi_input("power", "power", 0, 'W')
    # ]]]
    # fmt: off
    power_input_type = attrib_enum(default=constants.MultiInputType.Constant)
    power = attrib_scalar(
        default=Scalar('power', 0, 'W')
    )
    power_curve = attrib_curve(
        default=Curve(Array('power', [], 'W'), Array('time', [], 's'))
    )
    # fmt: on
    # [[[end]]] (checksum: 5454563efcb0d6262127c023258cceba)


@attr.s(frozen=True, slots=True)
class PipeSegmentsDescription:
    """
    .. include:: /alfacase_definitions/PipeSegmentsDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt

    """

    start_positions: Array = attr.ib(validator=optional(instance_of(Array)))
    diameters: Array = attr.ib(validator=optional(instance_of(Array)))
    roughnesses: Array = attr.ib(validator=optional(instance_of(Array)))
    wall_names: Optional[List[str]] = attr.ib(
        default=None, validator=optional(list_of_strings)
    )


@attr.s(frozen=True, slots=True)
class ReferencedPressureContainerDescription:
    """
    .. include:: /alfacase_definitions/ReferencedPressureContainerDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    .. include:: /alfacase_definitions/list_of_unit_for_pressure.txt
    """

    reference_coordinate: Scalar = attr.ib(default=Scalar(0.0, "m"))
    positions: Array = attr.ib(default=Array([0.0], "m"))
    pressures: Array = attr.ib(default=Array([1e5], "Pa"))


@attr.s(frozen=True, slots=True)
class PressureContainerDescription:
    """
    .. include:: /alfacase_definitions/PressureContainerDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    .. include:: /alfacase_definitions/list_of_unit_for_pressure.txt
    """

    positions: Array = attr.ib(default=Array([0.0], "m"))
    pressures: Array = attr.ib(default=Array([1e5], "Pa"))


@attr.s(frozen=True, slots=True)
class InitialPressuresDescription:
    """
    .. include:: /alfacase_definitions/InitialPressuresDescription.txt
    """

    position_input_type = attrib_enum(default=constants.TableInputType.length)
    table_x: ReferencedPressureContainerDescription = attr.ib(
        default=ReferencedPressureContainerDescription()
    )
    table_y: ReferencedPressureContainerDescription = attr.ib(
        default=ReferencedPressureContainerDescription()
    )
    table_length: PressureContainerDescription = attr.ib(
        default=PressureContainerDescription()
    )


@attr.s(frozen=True, slots=True)
class ReferencedVolumeFractionsContainerDescription:
    """
    .. include:: /alfacase_definitions/ReferencedVolumeFractionsContainerDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    .. include:: /alfacase_definitions/list_of_unit_for_pressure.txt
    .. include:: /alfacase_definitions/list_of_unit_for_dimensionless.txt
    """

    reference_coordinate: Scalar = attr.ib(default=Scalar(0.0, "m"))
    positions: Array = attr.ib(default=Array([], "m"))
    fractions: Dict[PhaseName, Array] = attr.ib(default={})


@attr.s(frozen=True, slots=True)
class VolumeFractionsContainerDescription:
    """
    .. include:: /alfacase_definitions/VolumeFractionsContainerDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    .. include:: /alfacase_definitions/list_of_unit_for_dimensionless.txt
    """

    positions: Array = attr.ib(default=Array([0.0], "m"))
    fractions: Dict[PhaseName, Array] = attr.ib(
        default={
            constants.FLUID_GAS: Array([0.1], "-"),
            constants.FLUID_OIL: Array([0.9], "-"),
        },
        validator=dict_of_array,
    )


@attr.s(frozen=True, slots=True)
class InitialVolumeFractionsDescription:
    """
    .. include:: /alfacase_definitions/InitialVolumeFractionsDescription.txt
    """

    position_input_type = attrib_enum(default=constants.TableInputType.length)
    table_x: ReferencedVolumeFractionsContainerDescription = attr.ib(
        default=ReferencedVolumeFractionsContainerDescription()
    )
    table_y: ReferencedVolumeFractionsContainerDescription = attr.ib(
        default=ReferencedVolumeFractionsContainerDescription()
    )
    table_length: VolumeFractionsContainerDescription = attr.ib(
        default=VolumeFractionsContainerDescription()
    )


@attr.s(frozen=True, slots=True)
class ReferencedTracersMassFractionsContainerDescription:
    """
    .. include:: /alfacase_definitions/ReferencedTracersMassFractionsContainerDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    .. include:: /alfacase_definitions/list_of_unit_for_dimensionless.txt
    """

    reference_coordinate: Scalar = attr.ib(default=Scalar(0.0, "m"))
    positions: Array = attr.ib(default=Array([], "m"))
    tracers_mass_fractions: List[Array] = attr.ib(default=[])


@attr.s(frozen=True, slots=True)
class TracersMassFractionsContainerDescription:
    """
    .. include:: /alfacase_definitions/TracersMassFractionsContainerDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    .. include:: /alfacase_definitions/list_of_unit_for_dimensionless.txt
    """

    positions: Array = attr.ib(default=Array([], "m"))
    tracers_mass_fractions: List[Array] = attr.ib(default=[])


@attr.s(frozen=True, slots=True)
class InitialTracersMassFractionsDescription:
    """
    .. include:: /alfacase_definitions/InitialTracersMassFractionsDescription.txt
    """

    position_input_type = attrib_enum(default=constants.TableInputType.length)
    table_x: ReferencedTracersMassFractionsContainerDescription = attr.ib(
        default=ReferencedTracersMassFractionsContainerDescription()
    )
    table_y: ReferencedTracersMassFractionsContainerDescription = attr.ib(
        default=ReferencedTracersMassFractionsContainerDescription()
    )
    table_length: TracersMassFractionsContainerDescription = attr.ib(
        default=TracersMassFractionsContainerDescription()
    )


@attr.s(frozen=True, slots=True)
class ReferencedVelocitiesContainerDescription:
    """
    .. include:: /alfacase_definitions/ReferencedVelocitiesContainerDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    .. include:: /alfacase_definitions/list_of_unit_for_velocity.txt
    """

    reference_coordinate: Scalar = attr.ib(default=Scalar(0.0, "m"))
    positions: Array = attr.ib(default=Array([], "m"))
    velocities: Dict[PhaseName, Array] = attr.ib(default={})


@attr.s(frozen=True, slots=True)
class VelocitiesContainerDescription:
    """
    .. include:: /alfacase_definitions/VelocitiesContainerDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    .. include:: /alfacase_definitions/list_of_unit_for_velocity.txt
    """

    positions: Array = attr.ib(default=Array([0.0], "m"))
    velocities: Dict[PhaseName, Array] = attr.ib(
        default={
            constants.FLUID_GAS: Array([1e-8], "m/s"),
            constants.FLUID_OIL: Array([1e-8], "m/s"),
        },
        validator=dict_of_array,
    )


@attr.s(frozen=True, slots=True)
class InitialVelocitiesDescription:
    """
    .. include:: /alfacase_definitions/InitialVelocitiesDescription.txt
    """

    position_input_type = attrib_enum(default=constants.TableInputType.length)
    table_x: ReferencedVelocitiesContainerDescription = attr.ib(
        default=ReferencedVelocitiesContainerDescription()
    )
    table_y: ReferencedVelocitiesContainerDescription = attr.ib(
        default=ReferencedVelocitiesContainerDescription()
    )
    table_length: VelocitiesContainerDescription = attr.ib(
        default=VelocitiesContainerDescription()
    )


@attr.s(frozen=True, slots=True)
class ReferencedTemperaturesContainerDescription:
    """
    .. include:: /alfacase_definitions/ReferencedTemperaturesContainerDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    .. include:: /alfacase_definitions/list_of_unit_for_temperature.txt
    """

    reference_coordinate: Scalar = attr.ib(default=Scalar(0.0, "m"))
    positions: Array = attr.ib(default=Array([], "m"))
    temperatures: Array = attr.ib(default=Array([], "K"))


@attr.s(frozen=True, slots=True)
class TemperaturesContainerDescription:
    """
    .. include:: /alfacase_definitions/TemperaturesContainerDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    .. include:: /alfacase_definitions/list_of_unit_for_temperature.txt
    """

    positions: Array = attr.ib(default=Array([0.0], "m"))
    temperatures: Array = attr.ib(
        default=Array([constants.DEFAULT_TEMPERATURE_IN_K], "K")
    )


@attr.s(frozen=True, slots=True)
class InitialTemperaturesDescription:
    """
    .. include:: /alfacase_definitions/InitialTemperaturesDescription.txt
    """

    position_input_type = attrib_enum(default=constants.TableInputType.length)
    table_x: ReferencedTemperaturesContainerDescription = attr.ib(
        default=ReferencedTemperaturesContainerDescription()
    )
    table_y: ReferencedTemperaturesContainerDescription = attr.ib(
        default=ReferencedTemperaturesContainerDescription()
    )
    table_length: TemperaturesContainerDescription = attr.ib(
        default=TemperaturesContainerDescription()
    )


@attr.s(slots=True, kw_only=True)
class InitialConditionsDescription:
    """
    .. include:: /alfacase_definitions/InitialConditionsDescription.txt
    """

    pressures: InitialPressuresDescription = attr.ib(
        default=InitialPressuresDescription()
    )
    volume_fractions: InitialVolumeFractionsDescription = attr.ib(
        default=InitialVolumeFractionsDescription()
    )
    tracers_mass_fractions: InitialTracersMassFractionsDescription = attr.ib(
        default=InitialTracersMassFractionsDescription()
    )
    velocities: InitialVelocitiesDescription = attr.ib(
        default=InitialVelocitiesDescription()
    )
    temperatures: InitialTemperaturesDescription = attr.ib(
        default=InitialTemperaturesDescription()
    )
    fluid: Optional[str] = attr.ib(default=None, validator=optional(instance_of(str)))


@attr.s(frozen=True)
class InitialConditionArrays:
    """
    .. include:: /alfacase_definitions/InitialConditionArrays.txt

    .. include:: /alfacase_definitions/list_of_unit_for_pressure.txt
    .. include:: /alfacase_definitions/list_of_unit_for_velocity.txt
    .. include:: /alfacase_definitions/list_of_unit_for_volume_fraction.txt
    .. include:: /alfacase_definitions/list_of_unit_for_temperature.txt
    """

    pressure: Array = attr.ib(validator=instance_of(Array))
    volume_fractions: Dict[PhaseName, Array] = attr.ib(validator=dict_of_array)
    velocity: Dict[PhaseName, Array] = attr.ib(validator=dict_of_array)
    temperature: Dict[str, Array] = attr.ib(validator=dict_of_array)
    x_coord_center: Optional[Array] = attr.ib(
        default=None, validator=optional(instance_of(Array))
    )
    x_coord_face: Optional[Array] = attr.ib(
        default=None, validator=optional(instance_of(Array))
    )


value_and_unit = Tuple[Number, str]


@attr.s(frozen=True, slots=True)
class LengthAndElevationDescription:
    """
    Describe a pipe with length and elevation.

    .. include:: /alfacase_definitions/LengthAndElevationDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    """

    length: Optional[Array] = attr.ib(
        default=None, validator=optional(instance_of(Array))
    )
    elevation: Optional[Array] = attr.ib(
        default=None, validator=optional(instance_of(Array))
    )

    def iter_values_and_unit(
        self,
    ) -> Iterator[Tuple[value_and_unit, value_and_unit]]:
        """Returns an iterator containing a pair of values with length and elevation along with their units."""
        if self.length and self.elevation:
            length_values = self.length.GetValues(self.length.unit)
            elevation_values = self.elevation.GetValues(self.elevation.unit)
            for length, elevation in zip(length_values, elevation_values):
                yield (length, self.length.unit), (elevation, self.elevation.unit)

        return iter(())


@attr.s(frozen=True, slots=True)
class XAndYDescription:
    """
    Describe a pipe with a sequence of coordinates.

    .. include:: /alfacase_definitions/XAndYDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    """

    x: Optional[Array] = attr.ib(default=None, validator=optional(instance_of(Array)))
    y: Optional[Array] = attr.ib(default=None, validator=optional(instance_of(Array)))

    def iter_values_and_unit(
        self,
    ) -> Iterator[Tuple[value_and_unit, value_and_unit]]:
        """Returns a pair of values with the x and y value along with their units."""
        for x, y in zip(self.x.GetValues(self.x.unit), self.y.GetValues(self.y.unit)):
            yield (x, self.x.unit), (y, self.y.unit)


@attr.s()
class ProfileDescription:
    """
    Describe a pipe by either length and inclination or by X and Y coordinates.

    :ivar length_and_elevation:
        A list of points with the length and elevation.
        The first item *MUST* always be (0, 0), otherwise a ValueError is raised.

    :ivar x_and_y:
        A list of points (X, Y), describing the coordinates.

    .. note:: x_and_y and length_and_elevation are mutually exclusive.

    .. include:: /alfacase_definitions/ProfileDescription.txt

    """

    x_and_y: Optional[XAndYDescription] = attr.ib(default=None)
    length_and_elevation: Optional[LengthAndElevationDescription] = attr.ib(
        default=None
    )

    def __attrs_post_init__(self):
        if self.length_and_elevation and self.x_and_y:
            msg = (
                f"length_and_elevation and x_and_y are mutually exclusive and you must configure only one of them, got "
                f"length_and_elevation={self.length_and_elevation} and x_and_y={self.x_and_y}"
            )
            raise ValueError(msg)


@attr.s()
class EquipmentDescription:
    """
    .. include:: /alfacase_definitions/EquipmentDescription.txt
    """

    mass_sources = attrib_dict_of(MassSourceEquipmentDescription)
    pumps = attrib_dict_of(PumpEquipmentDescription)
    valves = attrib_dict_of(ValveEquipmentDescription)
    reservoir_inflows = attrib_dict_of(ReservoirInflowEquipmentDescription)
    heat_sources = attrib_dict_of(HeatSourceEquipmentDescription)
    compressors = attrib_dict_of(CompressorEquipmentDescription)
    leaks = attrib_dict_of(LeakEquipmentDescription)
    pigs = attrib_dict_of(PigEquipmentDescription)


@attr.s(frozen=True, slots=True, kw_only=True)
class EnvironmentPropertyDescription:
    """
    .. include:: /alfacase_definitions/EnvironmentPropertyDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    .. include:: /alfacase_definitions/list_of_unit_for_temperature.txt
    .. include:: /alfacase_definitions/list_of_unit_for_heat_transfer_coefficient.txt
    .. include:: /alfacase_definitions/list_of_unit_for_velocity.txt
    """

    position = attrib_scalar(category="length")
    temperature = attrib_scalar(category="temperature")
    type = attrib_enum(type_=constants.PipeEnvironmentHeatTransferCoefficientModelType)
    heat_transfer_coefficient = attrib_scalar(default=Scalar(0.0, "W/m2.K"))
    overall_heat_transfer_coefficient = attrib_scalar(default=Scalar(0.0, "W/m2.K"))
    fluid_velocity = attrib_scalar(default=Scalar(0.0, "m/s"))


@attr.s(frozen=True, slots=True, kw_only=True)
class EnvironmentDescription:
    """
    .. include:: /alfacase_definitions/EnvironmentDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    """

    thermal_model = attrib_enum(default=constants.PipeThermalModelType.SteadyState)
    position_input_mode = attrib_enum(default=constants.PipeThermalPositionInput.Md)
    reference_y_coordinate = attrib_scalar(default=Scalar("length", 0.0, "m"))
    md_properties_table = attrib_instance_list(EnvironmentPropertyDescription)
    tvd_properties_table = attrib_instance_list(EnvironmentPropertyDescription)

    @property
    def properties_table(self):  # pragma: no cover
        if self.position_input_mode == constants.PipeThermalPositionInput.Md:
            return self.md_properties_table
        else:
            return self.tvd_properties_table


@attr.s(slots=True)
class PipeDescription:
    """
    .. include:: /alfacase_definitions/PipeDescription.txt
    """

    name: str = attr.ib(validator=instance_of(str))
    source: str = attr.ib(validator=instance_of(str))
    target: str = attr.ib(validator=instance_of(str))
    source_port: Optional[constants.WellConnectionPort] = attr.ib(
        default=None, validator=optional(in_(constants.WellConnectionPort))
    )
    target_port: Optional[constants.WellConnectionPort] = attr.ib(
        default=None, validator=optional(in_(constants.WellConnectionPort))
    )
    pvt_model: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )
    profile = attrib_instance(ProfileDescription)
    equipment = attrib_instance(EquipmentDescription)
    environment = attrib_instance(EnvironmentDescription)
    segments = attrib_instance(PipeSegmentsDescription)

    # Initial Condition Section
    initial_conditions = attrib_instance(InitialConditionsDescription)


@attr.s(slots=True, kw_only=True)
class PressureNodePropertiesDescription(_PressureSourceCommon):
    """
    .. include:: /alfacase_definitions/PressureNodePropertiesDescription.txt
    """


@attr.s(slots=True, kw_only=True)
class MassSourceNodePropertiesDescription(_MassSourceCommon):
    """
    .. include:: /alfacase_definitions/MassSourceNodePropertiesDescription.txt
    """


@attr.s(slots=True, kw_only=True)
class InternalNodePropertiesDescription:
    """
    .. include:: /alfacase_definitions/InternalNodePropertiesDescription.txt
    """

    fluid: Optional[str] = attr.ib(default=None, validator=optional(instance_of(str)))


@attr.s(slots=True, kw_only=True)
class SeparatorNodePropertiesDescription:
    """
    :ivar overall_heat_transfer_coefficient:
        η such that the overall heat transferred to the separator is
            Q = η A (T_amb - T_sep)

    .. include:: /alfacase_definitions/SeparatorNodePropertiesDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    .. include:: /alfacase_definitions/list_of_unit_for_temperature.txt
    .. include:: /alfacase_definitions/list_of_unit_for_heat_transfer_coefficient.txt
    .. include:: /alfacase_definitions/list_of_unit_for_volume_fraction.txt
    """

    environment_temperature = attrib_scalar(default=Scalar(25.0, "degC"))
    geometry = attrib_enum(default=constants.SeparatorGeometryType.VerticalCylinder)
    length = attrib_scalar(default=Scalar(1.0, "m"))
    overall_heat_transfer_coefficient = attrib_scalar(default=Scalar(0.0, "W/m2.K"))
    diameter = attrib_scalar(default=Scalar("diameter", 1.0, "m"))
    nozzles: Dict[str, Scalar] = attr.ib(
        default=attr.Factory(dict), validator=optional(dict_with_scalar)
    )
    initial_phase_volume_fractions: Dict[str, Scalar] = attr.ib(
        default={
            constants.FLUID_GAS: Scalar("volume fraction", 0.5, "-"),
            constants.FLUID_OIL: Scalar("volume fraction", 0.5, "-"),
        }
    )
    gas_separation_efficiency = attrib_scalar(default=Scalar("dimensionless", 1.0, "-"))
    liquid_separation_efficiency = attrib_scalar(
        default=Scalar("dimensionless", 1.0, "-")
    )

    @diameter.validator
    def _validate_diameter(self, attribute, value):
        assert (
            isinstance(value, Scalar) and value.GetCategory() == "diameter"
        ), "Invalid diameter"

    @length.validator
    def _validate_length(self, attribute, value):
        assert (
            isinstance(value, Scalar) and value.GetCategory() == "length"
        ), "Invalid length"

    @gas_separation_efficiency.validator
    def _validate_gas_separation_efficiency(self, attribute, value):
        assert isinstance(value, Scalar) and 0.6 <= value.GetValue("-") <= 1.0

    @liquid_separation_efficiency.validator
    def _validate_liquid_separation_efficiency(self, attribute, value):
        assert isinstance(value, Scalar) and 0.6 <= value.GetValue("-") <= 1.0


@attr.s(slots=True, kw_only=True)
class ControllerInputSignalPropertiesDescription:
    """
    :ivar target_variable:
        Measured variable target of controller setpoint
    :ivar unit:
        Measuring unit of target variable
    :ivar input_trend_name:
        Name of input trend where target variable is measured

    .. include:: /alfacase_definitions/ControllerInputSignalPropertiesDescription.txt
    """

    target_variable: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )
    input_trend_name: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )
    unit: Optional[str] = attr.ib(default=None, validator=optional(instance_of(str)))


@attr.s(slots=True, kw_only=True)
class ControllerOutputSignalPropertiesDescription:
    """
    :ivar controlled_property:
        Property under control to make target variable reach setpoint
    :ivar unit:
        Measuring unit of controlled property
    :ivar network_element_name:
        Name of network element that has controlled property
    :ivar min_value:
        Minimum value of output signal
    :ivar max_value:
        Maximum value of output signal
    :ivar max_rate_of_change:
        Maximum rate of change of output signal

    .. include:: /alfacase_definitions/ControllerOutputSignalPropertiesDescription.txt
    """

    controlled_property: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )
    unit: Optional[str] = attr.ib(default=None, validator=optional(instance_of(str)))
    network_element_name: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )
    min_value: float = attr.ib(default=-1.0e50, converter=float)
    max_value: float = attr.ib(default=1.0e50, converter=float)
    max_rate_of_change: float = attr.ib(default=1.0e50, converter=float)

    @max_rate_of_change.validator
    def _validate_max_rate_of_change(self, attribute, value):
        assert isinstance(value, float) and value >= 0.0


@attr.s(slots=True, kw_only=True)
class ControllerNodePropertiesDescription:
    """
    :ivar type:
        Type of controlling model
    :ivar gain:
        Proportional constant of PID controller
    :ivar setpoint:
        Target value for input signal
    :ivar integral_time:
        Integral constant of PID controller
    :ivar derivative_time:
        Derivative constant of PID controller
    :ivar input_signal_properties:
        Properties of input signal
    :ivar output_signal_properties:
        Properties of output signal

    .. include:: /alfacase_definitions/ControllerNodePropertiesDescription.txt
    """

    type = attrib_enum(default=constants.ControllerType.PID)
    gain: float = attr.ib(default=1e-4, converter=float)
    setpoint: float = attr.ib(default=0.0, converter=float)
    integral_time = attrib_scalar(default=Scalar(10, "s"))
    derivative_time = attrib_scalar(default=Scalar(1, "s"))

    input_signal_properties = attrib_instance(
        ControllerInputSignalPropertiesDescription
    )
    output_signal_properties = attrib_instance(
        ControllerOutputSignalPropertiesDescription
    )

    @integral_time.validator
    def _validate_integral_time(self, attribute, value):
        assert (
            isinstance(value, Scalar)
            and value.GetCategory() == "time"
            and value.GetValue("s") > 0.0
        )

    @derivative_time.validator
    def _validate_derivative_time(self, attribute, value):
        assert (
            isinstance(value, Scalar)
            and value.GetCategory() == "time"
            and value.GetValue("s") >= 0.0
        )


@attr.s(slots=True, kw_only=True)
class NodeDescription:
    """
    .. include:: /alfacase_definitions/NodeDescription.txt
    """

    name: str = attr.ib()
    node_type = attrib_enum(type_=constants.NodeCellType)
    pvt_model: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )
    pressure_properties = attrib_instance(PressureNodePropertiesDescription)
    mass_source_properties = attrib_instance(MassSourceNodePropertiesDescription)
    internal_properties = attrib_instance(InternalNodePropertiesDescription)
    separator_properties = attrib_instance(SeparatorNodePropertiesDescription)
    controller_properties = attrib_instance(ControllerNodePropertiesDescription)


@attr.s(frozen=True, slots=True, kw_only=True)
class FormationLayerDescription:
    """
    .. include:: /alfacase_definitions/FormationLayerDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    """

    name: str = attr.ib(validator=instance_of(str))
    start = attrib_scalar(category="length")
    material: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )


@attr.s(frozen=True, slots=True, kw_only=True)
class FormationDescription:
    """
    .. include:: /alfacase_definitions/FormationDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    """

    reference_y_coordinate = attrib_scalar(category="length")
    layers = attrib_instance_list(FormationLayerDescription)


@attr.s(frozen=True, slots=True, kw_only=True)
class CasingSectionDescription:
    """
    .. include:: /alfacase_definitions/CasingSectionDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    """

    name: str = attr.ib(validator=instance_of(str))
    hanger_depth = attrib_scalar(category="length")
    settings_depth = attrib_scalar(category="length")
    hole_diameter = attrib_scalar(category="diameter")
    outer_diameter = attrib_scalar(category="diameter")
    inner_diameter = attrib_scalar(category="diameter")
    inner_roughness = attrib_scalar(category="length")
    material: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )
    top_of_filler = attrib_scalar(category="length")
    filler_material: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )
    material_above_filler: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )

    @hole_diameter.validator
    @outer_diameter.validator
    @inner_diameter.validator
    def _validate_diameter(self, attribute, value):
        assert (
            isinstance(value, Scalar) and value.GetCategory() == "diameter"
        ), "Invalid diameter"


@attr.s(frozen=True, slots=True, kw_only=True)
class TubingDescription:
    """
    .. include:: /alfacase_definitions/TubingDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    """

    name: str = attr.ib(validator=instance_of(str))
    length = attrib_scalar(category="length")
    outer_diameter = attrib_scalar(category="diameter")
    inner_diameter = attrib_scalar(category="diameter")
    inner_roughness = attrib_scalar(category="length")
    material: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )

    @outer_diameter.validator
    @inner_diameter.validator
    def _validate_diameter(self, attribute, value):
        assert (
            isinstance(value, Scalar) and value.GetCategory() == "diameter"
        ), "Invalid diameter"


@attr.s(frozen=True, slots=True, kw_only=True)
class PackerDescription:
    """
    .. include:: /alfacase_definitions/PackerDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    """

    name: str = attr.ib(validator=instance_of(str))
    position = attrib_scalar(category="length")
    material_above: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )


@attr.s(frozen=True, slots=True, kw_only=True)
class OpenHoleDescription:
    """
    .. include:: /alfacase_definitions/OpenHoleDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    """

    name: str = attr.ib(validator=instance_of(str))
    length = attrib_scalar(category="length")
    diameter = attrib_scalar(category="diameter")
    inner_roughness = attrib_scalar(category="length")

    @diameter.validator
    def _validate_diameter(self, attribute, value):
        assert (
            isinstance(value, Scalar) and value.GetCategory() == "diameter"
        ), "Invalid diameter"


@attr.s(frozen=True, slots=True, kw_only=True)
class CasingDescription:
    """
    .. include:: /alfacase_definitions/CasingDescription.txt
    """

    casing_sections = attrib_instance_list(CasingSectionDescription)
    tubings = attrib_instance_list(TubingDescription)
    packers = attrib_instance_list(PackerDescription)
    open_holes = attrib_instance_list(OpenHoleDescription)


@attr.s(frozen=True, slots=True, kw_only=True)
class GasLiftValveEquipmentDescription:
    """
    .. include:: /alfacase_definitions/GasLiftValveEquipmentDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    .. include:: /alfacase_definitions/list_of_unit_for_pressure.txt
    .. include:: /alfacase_definitions/list_of_unit_for_dimensionless.txt
    """

    position = attrib_scalar(category="length")
    diameter = attrib_scalar(category="diameter")
    valve_type = attrib_enum(type_=constants.ValveType)
    delta_p_min = attrib_scalar(category="pressure")
    discharge_coefficient = attrib_scalar(category="dimensionless")

    @diameter.validator
    def _validate_diameter(self, attribute, value):
        assert (
            isinstance(value, Scalar) and value.GetCategory() == "diameter"
        ), "Invalid diameter"


@attr.s()
class AnnulusEquipmentDescription:
    """
    .. include:: /alfacase_definitions/AnnulusEquipmentDescription.txt
    """

    leaks = attrib_dict_of(LeakEquipmentDescription)
    gas_lift_valves = attrib_dict_of(GasLiftValveEquipmentDescription)


@attr.s(slots=True, kw_only=True)
class AnnulusDescription:
    """
    .. include:: /alfacase_definitions/AnnulusDescription.txt
    """

    has_annulus_flow: bool = attr.ib(validator=instance_of(bool))
    pvt_model: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )
    initial_conditions = attrib_instance(InitialConditionsDescription)
    equipment = attrib_instance(AnnulusEquipmentDescription)
    top_node: str = attr.ib(validator=instance_of(str))


@attr.s(slots=True, kw_only=True)
class WellDescription:
    """
    .. include:: /alfacase_definitions/WellDescription.txt
    """

    name: str = attr.ib(validator=instance_of(str))
    pvt_model: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )
    stagnant_fluid: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )
    profile = attrib_instance(ProfileDescription)
    casing = attrib_instance(CasingDescription)
    annulus = attrib_instance(AnnulusDescription)
    formation = attrib_instance(FormationDescription)
    top_node: str = attr.ib(validator=instance_of(str))
    bottom_node: str = attr.ib(validator=instance_of(str))
    environment = attrib_instance(EnvironmentDescription)
    initial_conditions = attrib_instance(InitialConditionsDescription)
    equipment = attrib_instance(EquipmentDescription)


@attr.s(frozen=True, slots=True, kw_only=True)
class MaterialDescription:
    """
    .. include:: /alfacase_definitions/MaterialDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_density.txt
    .. include:: /alfacase_definitions/list_of_unit_for_thermal_conductivity.txt
    .. include:: /alfacase_definitions/list_of_unit_for_specific_heat_capacity.txt
    .. include:: /alfacase_definitions/list_of_unit_for_emissivity.txt
    .. include:: /alfacase_definitions/list_of_unit_for_volumetric_thermal_expansion.txt
    .. include:: /alfacase_definitions/list_of_unit_for_dynamic_viscosity.txt
    """

    name: str = attr.ib(validator=instance_of(str))
    material_type = attrib_enum(default=constants.MaterialType.Solid)
    density = attrib_scalar(default=Scalar(1, "kg/m3"))
    thermal_conductivity = attrib_scalar(default=Scalar(0, "W/m.degC"))
    heat_capacity = attrib_scalar(default=Scalar(0, "J/kg.degC"))
    inner_emissivity = attrib_scalar(default=Scalar("emissivity", 0, "-"))
    outer_emissivity = attrib_scalar(default=Scalar("emissivity", 0, "-"))
    expansion = attrib_scalar(default=Scalar(0, "1/K"))
    viscosity = attrib_scalar(default=Scalar(0, "cP"))

    def as_dict(self) -> Dict[str, Union[str, value_and_unit]]:
        """
        Helper function that returns a dict with all information needed to create a Material.

        This method doesn't return an attr.asdict directly because a SubjectList doesn't accept a
        Scalar object when using the `New()` method, only tuples with value and unit.
        """
        return {
            key: value if not isinstance(value, Scalar) else value.GetValueAndUnit()
            for key, value in attr.asdict(self).items()
        }


@attr.s
class WallLayerDescription:
    """
    Used for defining the default walls.

    :ivar thickness:
    :ivar material_name:
    :ivar has_annulus_flow:

    .. include:: /alfacase_definitions/WallLayerDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    """

    thickness: Scalar = attr.ib(validator=instance_of(Scalar))
    material_name: str = attr.ib(validator=instance_of(str))
    has_annulus_flow: bool = attr.ib(default=False, validator=instance_of(bool))


@attr.s
class WallDescription:
    """
    .. include:: /alfacase_definitions/WallDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_length.txt
    """

    name: str = attr.ib(validator=instance_of(str))
    inner_roughness = attrib_scalar(default=Scalar(0, "m"))
    wall_layer_container = attrib_instance_list(WallLayerDescription)


@attr.s(frozen=True, slots=True)
class PvtModelCorrelationDescription:
    """

    :ivar oil_density_std:
        default: Scalar(850.0, "kg/m3")

    :ivar gas_density_std:
        default: Scalar(0.9, "kg/m3")

    :ivar rs_sat:
        default: Scalar(150.0, "sm3/sm3")

    :ivar pvt_correlation_package:
        default: `CorrelationPackage.Standing`


    .. include:: /alfacase_definitions/PvtModelCorrelationDescription.txt


    .. rubric:: Examples

    .. tab:: CaseDescription

        .. code-block:: python

            PvtModelCorrelationDescription(
                default_model="PVT1",
            )

    .. tab:: Schema

        .. code-block:: yaml

            some_value:
                some_other_value: fooo

    .. include:: /alfacase_definitions/list_of_unit_for_density.txt
    .. include:: /alfacase_definitions/list_of_unit_for_standard_volume_per_standard_volume.txt
    """

    oil_density_std = attrib_scalar(default=Scalar(850.0, "kg/m3"))
    gas_density_std = attrib_scalar(default=Scalar(0.9, "kg/m3"))
    rs_sat = attrib_scalar(default=Scalar(150.0, "sm3/sm3"))
    pvt_correlation_package = attrib_enum(default=constants.CorrelationPackage.Standing)


@attr.s(frozen=True, slots=True)
class HeavyComponentDescription:
    """
    .. include:: /alfacase_definitions/HeavyComponentDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_density.txt
    .. include:: /alfacase_definitions/list_of_unit_for_mass_per_mol.txt
    """

    name: str = attr.ib(validator=instance_of(str))
    scn: int = attr.ib(validator=instance_of(int), converter=int)
    MW = attrib_scalar(default=Scalar(0, "kg/mol"))
    rho = attrib_scalar(default=Scalar(0, "kg/m3"))


@attr.s(frozen=True, slots=True)
class LightComponentDescription:
    """
    .. include:: /alfacase_definitions/LightComponentDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_density.txt
    .. include:: /alfacase_definitions/list_of_unit_for_mass_per_mol.txt
    .. include:: /alfacase_definitions/list_of_unit_for_pressure.txt
    .. include:: /alfacase_definitions/list_of_unit_for_temperature.txt
    .. include:: /alfacase_definitions/list_of_unit_for_molar_volume.txt
    .. include:: /alfacase_definitions/list_of_unit_for_dimensionless.txt
    """

    name: str = attr.ib(validator=instance_of(str))
    Pc = attrib_scalar(default=Scalar("pressure", 0, "Pa"))
    Tc = attrib_scalar(default=Scalar("temperature", 0, "K"))
    Vc = attrib_scalar(default=Scalar("molar volume", 0, "m3/mol"))
    omega = attrib_scalar(default=Scalar("dimensionless", 0, "-"))
    MW = attrib_scalar(default=Scalar("mass per mol", 0, "kg/mol"))
    Tb = attrib_scalar(default=Scalar("temperature", 0, "K"))
    Parachor = attrib_scalar(default=Scalar("dimensionless", 0, "-"))
    Cp_0 = attrib_scalar(default=Scalar("dimensionless", 0, "-"))
    Cp_1 = attrib_scalar(default=Scalar("dimensionless", 0, "-"))
    Cp_2 = attrib_scalar(default=Scalar("dimensionless", 0, "-"))
    Cp_3 = attrib_scalar(default=Scalar("dimensionless", 0, "-"))
    Cp_4 = attrib_scalar(default=Scalar("dimensionless", 0, "-"))


@attr.s(slots=True)
class PvtModelCompositionalDescription:
    """

    :ivar equation_of_state_type:
        default: EquationOfStateType.PengRobinson

    :ivar surface_tension_model_type:
        default: SurfaceTensionType.Weinaugkatz

    :ivar viscosity_model:
        default: PVTCompositionalViscosityModel.CorrespondingStatesPrinciple

    :ivar heavy_components:
        default: []

    :ivar light_components:
        default: []

    :ivar fluids:
        default: {}


    .. include:: /alfacase_definitions/PvtModelCompositionalDescription.txt


    """

    equation_of_state_type = attrib_enum(
        default=constants.EquationOfStateType.PengRobinson
    )
    surface_tension_model_type = attrib_enum(
        default=constants.SurfaceTensionType.Weinaugkatz
    )
    viscosity_model = attrib_enum(
        default=constants.PVTCompositionalViscosityModel.CorrespondingStatesPrinciple
    )
    heavy_components = attrib_instance_list(HeavyComponentDescription)
    light_components = attrib_instance_list(LightComponentDescription)
    fluids = attrib_dict_of(FluidDescription)


@attr.s(slots=True, eq=False)
class PvtModelTableParametersDescription:
    """
    :ivar pressure_values:
        Array like of sorted pressure values (m number of entries). [Pa]

    :ivar temperature_values:
        Array like of sorted temperature values (n number of entries). [K]

    :ivar table_variables:
        List of array like values for each property such as densities, specific heats,
        enthalpies, etc.

    :ivar variable_names:
        List of property names

    .. include:: /alfacase_definitions/list_of_unit_for_temperature.txt
    .. include:: /alfacase_definitions/list_of_unit_for_density.txt
    .. include:: /alfacase_definitions/list_of_unit_for_pressure.txt
    .. include:: /alfacase_definitions/list_of_unit_for_standard_volume_per_standard_volume.txt
    .. include:: /alfacase_definitions/list_of_unit_for_dimensionless.txt
    """

    pressure_values: Numpy1DArray = attr.ib(
        validator=numpy_array_validator(dimension=1), repr=collapse_array_repr
    )
    temperature_values: Numpy1DArray = attr.ib(
        validator=numpy_array_validator(dimension=1), repr=collapse_array_repr
    )
    table_variables: List[Numpy1DArray] = attr.ib(
        validator=numpy_array_validator(dimension=1, is_list=True),
        repr=collapse_array_repr,
    )
    variable_names: List[str] = attr.ib(validator=list_of_strings)

    pressure_std = attrib_scalar(default=Scalar(1, "bar"), is_optional=True)
    temperature_std = attrib_scalar(default=Scalar(15, "degC"), is_optional=True)

    gas_density_std = attrib_scalar(default=Scalar(1, "kg/m3"), is_optional=True)
    oil_density_std = attrib_scalar(default=Scalar(800, "kg/m3"), is_optional=True)
    water_density_std = attrib_scalar(default=Scalar(1000, "kg/m3"), is_optional=True)

    gas_oil_ratio = attrib_scalar(default=Scalar(0, "sm3/sm3"), is_optional=True)  # GOR
    gas_liquid_ratio = attrib_scalar(
        default=Scalar(0, "sm3/sm3"), is_optional=True
    )  # GLR
    water_cut = attrib_scalar(default=Scalar(0, "-"), is_optional=True)  # WC
    total_water_fraction = attrib_scalar(default=Scalar(0, "-"), is_optional=True)

    label: Optional[str] = attr.ib(default=None, validator=optional(instance_of(str)))
    number_of_phases: int = attr.ib(default=2, validator=instance_of(int))
    warn_when_outside: bool = attr.ib(default=True, validator=instance_of(bool))

    def __attrs_post_init__(self):
        """
        Fix standard properties that have not been set in .TAB files.

        Some pvt tables do not set water related properties if it is a two-phase
        table.

        PVT Sim always set water related properties to np.nan.
        Multiflash sometimes does not write the water related keyword.

        """
        if self.pressure_std is None:
            self.pressure_std = Scalar(np.nan, "bar")
        if self.temperature_std is None:
            self.temperature_std = Scalar(np.nan, "degC")
        if self.gas_density_std is None:
            self.gas_density_std = Scalar(np.nan, "kg/m3")
        if self.oil_density_std is None:
            self.oil_density_std = Scalar(np.nan, "kg/m3")
        if self.water_density_std is None:
            self.water_density_std = Scalar(np.nan, "kg/m3")
        if self.gas_oil_ratio is None:
            self.gas_oil_ratio = Scalar(np.nan, "sm3/sm3")
        if self.gas_liquid_ratio is None:
            self.gas_liquid_ratio = Scalar(np.nan, "sm3/sm3")
        if self.water_cut is None:
            self.water_cut = Scalar(np.nan, "-")
        if self.total_water_fraction is None:
            self.total_water_fraction = Scalar(np.nan, "-")

    @property
    def pressure_unit(self):
        return "Pa"

    @property
    def temperature_unit(self):
        return "K"

    @staticmethod
    def create_constant(
        rho_g_ref=1.0,
        rho_l_ref=1000.0,
        rho_w_ref=1000.0,
        rho_s_ref=2500.0,
        mu_g_ref=5e-6,
        mu_l_ref=5e-2,
        mu_w_ref=5e-2,
        s_ref=7.197e-2,
        ideal_gas=True,
        cp_g_ref=1010.0,
        cp_l_ref=4181.3,
        cp_w_ref=4181.3,
        h_l_ref=104.86e3,
        k_g_ref=2.4e-2,
        k_l_ref=5.91e-1,
        k_w_ref=5.91e-1,
        s_gw_ref=7.197e-2,
        s_lw_ref=7.197e-2,
        has_water=False,
    ):
        """
        Returns parameters that can be used to create a very simple constant and isothermal PVT
        table.
        Used by PvtTable to build it's default table if no parameter is passed.
        """
        r = 286.9  # Air individual gas constant [J/kg K]

        def ideal_gas_density_model(p, t):
            """
            :param p: pressure in Pa
            :param t: temperature in K
            """
            return p / (r * t)

        def constant_gas_density_model(p, t):
            return rho_g_ref + 0 * p

        def gas_density_derivative_respect_pressure(p, t):
            return 1 / (r * t)

        def gas_density_derivative_respect_temperature(p, t):
            return -p / (r * t ** 2)

        def constant_density_model(p, t):
            return rho_l_ref + 0 * p

        def oil_density_derivative_respect_pressure(p, t):
            return 0 * p

        def oil_density_derivative_respect_temperature(p, t):
            return 0 * p

        def oil_viscosity_model(p, t):
            return mu_l_ref + p * 0

        def water_constant_density_model(p, t):
            return rho_w_ref + 0 * p

        def water_density_derivative_respect_pressure(p, t):
            return 0 * p

        def water_density_derivative_respect_temperature(p, t):
            return 0 * p

        def water_viscosity_model(p, t):
            return mu_w_ref + p * 0

        def gas_viscosity_model(p, t):
            return mu_g_ref + p * 0

        def surface_tension_model(p, t):
            return s_ref + p * 0

        def gas_mass_fraction_model(p, t):
            return 0 * p

        def water_mass_fraction_model(p, t):
            return 0 * p

        def oil_specific_heat_model(p, t):
            return cp_l_ref + p * 0

        def water_specific_heat_model(p, t):
            return cp_w_ref + p * 0

        def gas_specific_heat_model(p, t):
            return cp_g_ref + p * 0

        def oil_specific_enthalpy_model(p, t):
            return cp_l_ref * t + p / rho_l_ref

        def water_specific_enthalpy_model(p, t):
            return cp_w_ref * t + p / rho_w_ref

        def gas_specific_enthalpy_model(p, t):
            h_lg = 2.260e6
            return cp_g_ref * t + h_lg + h_l_ref

        def oil_thermal_conductivity_model(p, t):
            return k_l_ref + p * 0

        def water_thermal_conductivity_model(p, t):
            return k_w_ref + p * 0

        def gas_thermal_conductivity_model(p, t):
            return k_g_ref + p * 0

        def gas_water_surface_tension_model(p, t):
            return s_gw_ref + p * 0

        def oil_water_surface_tension_model(p, t):
            return s_lw_ref + p * 0

        pressure_values = np.linspace(0.5, 1e10, 4)  # Pa (1e-5 to 1e5 in bar)
        temperature_values = np.linspace(250, 500, 30)  # K

        gas_density_model = (
            ideal_gas_density_model if ideal_gas else constant_gas_density_model
        )

        t, p = np.meshgrid(temperature_values, pressure_values)

        data = [
            gas_density_model(p, t).flatten(),
            gas_density_derivative_respect_pressure(p, t).flatten(),
            gas_density_derivative_respect_temperature(p, t).flatten(),
            constant_density_model(p, t).flatten(),
            oil_density_derivative_respect_pressure(p, t).flatten(),
            oil_density_derivative_respect_temperature(p, t).flatten(),
            gas_viscosity_model(p, t).flatten(),
            oil_viscosity_model(p, t).flatten(),
            surface_tension_model(p, t).flatten(),
            gas_mass_fraction_model(p, t).flatten(),
            gas_specific_heat_model(p, t).flatten(),
            oil_specific_heat_model(p, t).flatten(),
            gas_specific_enthalpy_model(p, t).flatten(),
            oil_specific_enthalpy_model(p, t).flatten(),
            gas_thermal_conductivity_model(p, t).flatten(),
            oil_thermal_conductivity_model(p, t).flatten(),
        ]

        names = [
            "gas density",
            "gas density derivative pressure",
            "gas density derivative temperature",
            "oil density",
            "oil density derivative pressure",
            "oil density derivative temperature",
            "gas viscosity",
            "oil viscosity",
            "gas-oil surface tension",
            "gas mass fraction",
            "gas specific heat",
            "oil specific heat",
            "gas specific enthalpy",
            "oil specific enthalpy",
            "gas thermal conductivity",
            "oil thermal conductivity",
        ]

        if has_water:
            data += [
                water_constant_density_model(p, t).flatten(),
                water_density_derivative_respect_pressure(p, t).flatten(),
                water_density_derivative_respect_temperature(p, t).flatten(),
                water_viscosity_model(p, t).flatten(),
                water_mass_fraction_model(p, t).flatten(),
                water_specific_heat_model(p, t).flatten(),
                water_specific_enthalpy_model(p, t).flatten(),
                water_thermal_conductivity_model(p, t).flatten(),
                gas_water_surface_tension_model(p, t).flatten(),
                oil_water_surface_tension_model(p, t).flatten(),
            ]

            names += [
                "water density",
                "water density derivative pressure",
                "water density derivative temperature",
                "water viscosity",
                "water mass fraction",
                "water specific heat",
                "water specific enthalpy",
                "water thermal conductivity",
                "gas_water_surface_tension",
                "oil_water_surface_tension",
            ]

        return PvtModelTableParametersDescription(
            pressure_values=pressure_values,
            temperature_values=temperature_values,
            table_variables=data,
            variable_names=names,
            pressure_std=Scalar(1e5, "Pa"),
            temperature_std=Scalar(15, "degC"),
            gas_density_std=Scalar(rho_g_ref, "kg/m3"),
            oil_density_std=Scalar(rho_l_ref, "kg/m3"),
            water_density_std=Scalar(rho_w_ref, "kg/m3"),
            gas_oil_ratio=Scalar(0, "sm3/sm3"),
            gas_liquid_ratio=Scalar(0, "sm3/sm3"),
            water_cut=Scalar(0, "-"),
            total_water_fraction=Scalar(0, "-"),
            number_of_phases=3 if has_water else 2,
        )

    @staticmethod
    def create_empty():
        """
        Creates a dummy (empty) PVT Table parameters with no valid data.
        """
        return PvtModelTableParametersDescription(
            pressure_values=np.array([0.0]),
            temperature_values=np.array([0.0]),
            table_variables=[],
            variable_names=[],
            number_of_phases=-1,
        )

    def __eq__(self, other):
        """
        Need to re-implement the equality operator because ndarrays don't support equality, so the attr's generated
        __eq__ function does not work.
        """
        if type(self) is not type(other):
            return False

        if len(self.table_variables) != len(other.table_variables):
            return False

        for array1, array2 in zip(self.table_variables, other.table_variables):
            if not np.array_equal(array1, array2):
                return False

        return (
            (self.pressure_values == other.pressure_values).all()
            and (self.temperature_values == other.temperature_values).all()
            and self.variable_names == other.variable_names
            and self.pressure_std == other.pressure_std
            and self.temperature_std == other.temperature_std
            and self.number_of_phases == other.number_of_phases
        )


@attr.s(slots=True)
class PvtModelsDescription:
    """
    Holds a PVT which is used by the simulator to obtain fluid characteristics, such as density and viscosity,
    given a certain pressure and temperature.

    This class is a holder for the different ways the user can enter PVT information in the application.

    :ivar correlations:
        Standard black-oil correlations found in the literature. The user can tune the parameters used by the correlations.

    :ivar compositions:
        Molar fluid compositions with molecular weights and densities for each component.
        It be light components and/or heavy fractions to be lumped into pseudo-components.

    :ivar tables:
        Load a complete PVT table obtained (usually) from lab results and generated by various software.
        Currently the user can import the table directly from a `.tab` file or a `.alfatable` file.

        The table parameter must be filled with a dictionary where the keys informs the name of the PVT and
        the values informs Path to a file with the Pvt model.

            - The value which holds the Path can be either relative or absolute.
            - The name of the pvt model from the Path can contains a 'pipe' character in order to select one of
              the multiples PVT tables in the same .tab file.

            .. rubric:: Example

            Absolute Path, using MyPvtModel

            >>> Path("/home/user/my_file.tab|MyPvtModel")

            Relative Path, using MyPvtModel

            >>> Path("./my_file.tab|MyPvtModel")

    :ivar table_parameters:
        *INTERNAL USE ONLY*

        This attribute is populated when exporting a Study to a CaseDescription, and it holds a model representation
        of a PVT originated from a (.tab / .alfatable) file.

        Their usage is directly related to the export of a CaseDescription to a `.alfacase`/`.alfatable` file,
        where the original PVT file cannot be guaranteed to exist therefore the only reproducible way to recreate
        the PVT is trough the PvtModelTableParametersDescription.


    .. include:: /alfacase_definitions/PvtModelsDescription.txt

    .. rubric:: Examples

    .. tab:: CaseDescription

        .. code-block:: python

            PvtModelsDescription(
                default_model="PVT1",
                tables={
                    'PVT1': Path('./my_tab_file.tab')
                },
            )

    .. tab:: Schema

        .. code-block:: yaml

            pvt_models:
                default_model: PVT1
                tables:
                    PVT1: ./my_tab_file.tab

    """

    default_model: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )

    tables: Dict[str, Union[str, Path]] = attr.ib(
        default=attr.Factory(dict), validator=dict_of((str, Path))
    )
    correlations: Dict[str, PvtModelCorrelationDescription] = attr.ib(
        default=attr.Factory(dict), validator=dict_of(PvtModelCorrelationDescription)
    )
    compositions: Dict[str, PvtModelCompositionalDescription] = attr.ib(
        default=attr.Factory(dict), validator=dict_of(PvtModelCompositionalDescription)
    )
    table_parameters: Dict[str, PvtModelTableParametersDescription] = attr.ib(
        default=attr.Factory(dict),
        validator=dict_of(PvtModelTableParametersDescription),
    )

    @staticmethod
    def get_pvt_file_and_model_name(
        value: Union[str, Path]
    ) -> Tuple[Path, Optional[str]]:
        """
        Parse the value provided from the user to get the path for the pvt file and if defined, the pvt model.
        """
        parts = str(value).split("|")
        model_name = None if len(parts) == 1 else parts[1].strip()
        return Path(parts[0].strip()), model_name


@attr.s()
class TracerModelConstantCoefficientsDescription:
    """
    .. include:: /alfacase_definitions/TracerModelConstantCoefficientsDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_mass_fraction.txt
    """

    partition_coefficients: Dict[str, Scalar] = attr.ib(
        default=attr.Factory(dict), validator=dict_of(Scalar)
    )


@attr.s()
class TracersDescription:
    """
    .. include:: /alfacase_definitions/TracersDescription.txt
    """

    constant_coefficients: Dict[
        str, TracerModelConstantCoefficientsDescription
    ] = attr.ib(
        default=attr.Factory(dict),
        validator=dict_of(TracerModelConstantCoefficientsDescription),
    )


@attr.s()
class PhysicsDescription:
    """
    .. include:: /alfacase_definitions/PhysicsDescription.txt
    """

    hydrodynamic_model = attrib_enum(default=constants.HydrodynamicModelType.FourFields)
    simulation_regime = attrib_enum(default=constants.SimulationRegimeType.Transient)
    energy_model = attrib_enum(default=constants.EnergyModel.NoModel)
    solids_model = attrib_enum(default=constants.SolidsModelType.NoModel)
    solids_model_plugin_id: str = attr.ib(default="", validator=instance_of(str))
    initial_condition_strategy = attrib_enum(
        default=constants.InitialConditionStrategyType.Constant
    )
    restart_filepath: Optional[Path] = attr.ib(
        default=None, validator=optional(instance_of(Path))
    )
    keep_former_results: bool = attr.ib(default=False, validator=instance_of(bool))
    emulsion_model = attrib_enum(default=constants.EmulsionModelType.NoModel)
    emulsion_model_plugin_id: str = attr.ib(default="", validator=instance_of(str))
    flash_model = attrib_enum(default=constants.FlashModel.HydrocarbonAndWater)
    correlations_package = attrib_enum(
        default=constants.CorrelationPackageType.Classical
    )


@attr.s()
class TimeOptionsDescription:
    """
    .. include:: /alfacase_definitions/TimeOptionsDescription.txt

    .. include:: /alfacase_definitions/list_of_unit_for_time.txt
    """

    stop_on_steady_state: bool = attr.ib(default=False, validator=instance_of(bool))
    automatic_restart_autosave_frequency: bool = attr.ib(
        default=True, validator=instance_of(bool)
    )
    initial_time = attrib_scalar(default=Scalar("time", 0.0, "s"))
    final_time = attrib_scalar(default=Scalar("time", 10.0, "s"))
    initial_timestep = attrib_scalar(default=Scalar("time", 1e-4, "s"))
    minimum_timestep = attrib_scalar(default=Scalar("time", 1e-12, "s"))
    maximum_timestep = attrib_scalar(default=Scalar("time", 0.1, "s"))
    restart_autosave_frequency = attrib_scalar(default=Scalar("time", 1, "h"))
    minimum_time_for_steady_state_stop = attrib_scalar(default=Scalar("time", 0.0, "s"))


@attr.s()
class NumericalOptionsDescription:
    """
    .. include:: /alfacase_definitions/NumericalOptionsDescription.txt
    """

    nonlinear_solver_type = attrib_enum(
        default=constants.NonlinearSolverType.AlfasimQuasiNewton
    )
    tolerance: float = attr.ib(default=1e-4, converter=float)
    maximum_iterations: int = attr.ib(default=5, converter=int)
    maximum_timestep_change_factor: float = attr.ib(default=2, converter=float)
    maximum_cfl_value: float = attr.ib(default=1.0, converter=float)
    relaxed_tolerance: float = attr.ib(default=0.0, converter=float)
    divergence_tolerance: float = attr.ib(default=-1.0, converter=float)
    friction_factor_evaluation_strategy = attrib_enum(
        default=constants.EvaluationStrategyType.TimeExplicit
    )
    simulation_mode = attrib_enum(default=constants.SimulationModeType.Default)
    enable_solver_caching: bool = attr.ib(default=True)
    caching_rtol: float = attr.ib(default=1e-2)
    caching_atol: float = attr.ib(default=1e-4)
    always_repeat_timestep: bool = attr.ib(default=False, validator=instance_of(bool))


@attr.s()
class CaseDescription:
    """
    .. include:: /alfacase_definitions/CaseDescription.txt
    """

    name: Optional[str] = attr.ib(default=None, validator=optional(instance_of(str)))
    physics = attrib_instance(PhysicsDescription)
    time_options = attrib_instance(TimeOptionsDescription)
    numerical_options = attrib_instance(NumericalOptionsDescription)
    plugins = attrib_instance_list(PluginDescription)
    ipr_models = attrib_instance(IPRModelsDescription)
    pvt_models = attrib_instance(PvtModelsDescription)
    tracers = attrib_instance(TracersDescription)
    outputs = attrib_instance(CaseOutputDescription)
    pipes = attrib_instance_list(PipeDescription)
    nodes = attrib_instance_list(NodeDescription)
    wells = attrib_instance_list(WellDescription)
    materials = attrib_instance_list(MaterialDescription)
    walls = attrib_instance_list(WallDescription)

    def _check_pvt_model_references(self, reset_invalid_reference: bool = False):
        """
        Check the consistence of the pvt_models, the following check are made:
        - The pvt files configured on case.pvt_models.tables must exist.
        - The property "default_model" must be a valid pvt_model defined on pvt_models
        - The property "pvt_model" that are defined can be None, if "default_model" is defined.
        - The property "pvt_model" from all elements that are defined must be a valid pvt_model
        - If default_model is None, all components that uses pvt_model must be defined.

        :param reset_invalid_reference:
            Set the element to None if a insistence is found instead of raising an exception.

        """
        from itertools import chain

        pvt_models_available = list(
            chain(
                self.pvt_models.tables.keys(),
                self.pvt_models.correlations.keys(),
                self.pvt_models.compositions.keys(),
                self.pvt_models.table_parameters.keys(),
            )
        )
        if (
            self.pvt_models.default_model
            and self.pvt_models.default_model not in pvt_models_available
        ):
            if not reset_invalid_reference:
                raise InvalidReferenceError(
                    f"PVT model '{self.pvt_models.default_model}' select on 'default_model' is not declared on 'pvt_models', "
                    f"available pvt_models are: {', '.join(pvt_models_available)}"
                )
            self.pvt_models.default_model = None

        elements_without_pvt_model = []

        def _handle_invalid_reference(element, element_name, pvt_model_name):
            """
            Set the pvt_model from the element to None if reset_invalid_reference is activate, otherwise raise
            an exception informing the valid pvt_models.
            """
            invalid_pvt_model = (
                pvt_model_name and pvt_model_name not in pvt_models_available
            )
            pvt_model_needs_to_be_defined = not (
                self.pvt_models.default_model
                or pvt_model_name
                or reset_invalid_reference
            )
            # If model_default is not defined, and element doesnt have a pvt_model
            if pvt_model_needs_to_be_defined:
                elements_without_pvt_model.append(
                    element_name
                )  # Collect to raise at the end

            # If element has pvt_model assigned and it's not available
            elif invalid_pvt_model:
                if reset_invalid_reference:
                    element.pvt_model = None
                else:
                    raise InvalidReferenceError(
                        f"PVT model '{pvt_model_name}' selected on '{element_name}' is not declared on 'pvt_models', "
                        f"available pvt_models are: {', '.join(pvt_models_available)}"
                    )

        for element in chain(self.nodes, self.pipes, self.wells):
            _handle_invalid_reference(element, element.name, element.pvt_model)

            # Well has an annulus that also has a pvt_model but, doesn't have a name
            if isinstance(element, WellDescription):
                _handle_invalid_reference(
                    element.annulus,
                    f"Annulus from {element.name}",
                    element.annulus.pvt_model,
                )

        if elements_without_pvt_model:
            raise InvalidReferenceError(
                f"The following elements doesnt have a pvt_model assigned: {', '.join(elements_without_pvt_model)}.\n"
                f"Either assign a valid pvt_model on the element, or fill the default_model parameter."
            )

    def _check_pvt_model_files(self, reset_invalid_reference: bool = False):
        """
        Check the consistence of case.pvt_models.tables, the following check are made:
        - Ensure PVT files exist
        - Ensure that the PVT Model referred from inside the file exist

        :param bool reset_invalid_reference:
            Set the element to None if a insistence is found instead of raising an exception.
        """

        def _get_all_pvt_models_declared_on_file(file_path: Path) -> Set[str]:
            """
            Read the pvt model file and return a tuple with all PVT Models declared on it
            """
            import csv
            import re

            all_pvt_models_declared = set()
            reader = csv.reader(file_path.read_text().splitlines(), delimiter=",")
            for line in reader:
                all_line_content = ",".join(line)
                if "PVTTABLE LABEL" in all_line_content:
                    matches = re.findall(r"LABEL\s+=\s+([^,]+)", all_line_content)
                    all_pvt_models_declared.add(
                        matches[0].replace('"', "").replace("'", "")
                    )

            return all_pvt_models_declared

        keys_from_pvt_tables_to_remove = []
        for key, value in self.pvt_models.tables.items():
            pvt_file, model_name = PvtModelsDescription.get_pvt_file_and_model_name(
                value
            )

            # Check if PVT files from case.pvt_models.tables exist
            if not Path(pvt_file).is_file():
                if not reset_invalid_reference:
                    raise InvalidReferenceError(
                        f"Error on '{key}', '{pvt_file}' is not a valid file"
                    )

                keys_from_pvt_tables_to_remove.append(key)
                continue

            # Check if user select PVT model is inside the file.
            if model_name:
                pvt_models_available_on_file = _get_all_pvt_models_declared_on_file(
                    pvt_file
                )
                if model_name not in pvt_models_available_on_file:
                    if not reset_invalid_reference:
                        raise InvalidReferenceError(
                            f"'{model_name}' could not be found on '{pvt_file.name}', available models are: '{', '.join(sorted(pvt_models_available_on_file))}'"
                        )
                    keys_from_pvt_tables_to_remove.append(key)

        for key in keys_from_pvt_tables_to_remove:
            del self.pvt_models.tables[key]

    def _check_restart_file(self):
        restart_file = self.physics.restart_filepath
        if restart_file and not Path(restart_file).is_file():
            raise InvalidReferenceError(
                f"Restart file '{restart_file}' is not a valid file"
            )

    def _check_fluid_references(self, *, reset_invalid_reference: bool = False):
        """
        Checks if all referenced fluids have a definition in at least one of the PVTs

        :param bool reset_invalid_reference:
            If True, sets the element to None if an inconsistency is found instead of raising an exception.
        """
        from itertools import chain

        elements_with_invalid_fluid = []
        fluids_available = set(
            fluid
            for composition in self.pvt_models.compositions.values()
            for fluid in composition.fluids.keys()
        )

        def _handle_invalid_fluid(element, element_name):
            if element.fluid and element.fluid not in fluids_available:
                if reset_invalid_reference:
                    element.fluid = None
                else:
                    elements_with_invalid_fluid.append(f"'{element_name}'")

        for node in self.nodes:
            _handle_invalid_fluid(node.pressure_properties, node.name)
            _handle_invalid_fluid(node.mass_source_properties, node.name)
            _handle_invalid_fluid(node.internal_properties, node.name)

        for pipe in self.pipes:
            _handle_invalid_fluid(pipe.initial_conditions, pipe.name)
            for name, equip in chain(
                pipe.equipment.mass_sources.items(),
                pipe.equipment.reservoir_inflows.items(),
            ):
                _handle_invalid_fluid(equip, f"{name} from {pipe.name}")

        for well in self.wells:
            _handle_invalid_fluid(well.initial_conditions, well.name)
            _handle_invalid_fluid(
                well.annulus.initial_conditions,
                f"Annulus from {well.name}",
            )

        if elements_with_invalid_fluid:
            raise InvalidReferenceError(
                f"The following elements have an invalid fluid assigned: {', '.join(sorted(elements_with_invalid_fluid))}.\n"
            )

    def ensure_valid_references(self):
        """
        Ensure that all attributes that uses references has consistent values, otherwise an exception is raised.
        # TODO: ASIM-3635: Add Check for source and target parameters of PipeDescription
        # TODO: ASIM-3635: Add Check for stagnant_fluid parameters of WellDescription
        # TODO: ASIM-3635: Add Check for top_node parameter of AnnulusDescription
        """
        self._check_pvt_model_files()
        self._check_pvt_model_references()
        self._check_restart_file()
        self._check_fluid_references()
        self.ensure_unique_names()

    def reset_invalid_references(self):
        """
        Reset all attributes that uses references to None if the reference is invalid.
        """
        self._check_pvt_model_files(reset_invalid_reference=True)
        self._check_pvt_model_references(reset_invalid_reference=True)
        self._check_fluid_references(reset_invalid_reference=True)

    def ensure_unique_names(self):
        """
        Ensure that elements that can be referenced by name have a unique name,
        raising `InvalidReferenceError` if some elements have the same name .
        """
        import collections
        from collections import Counter

        duplicate_names = collections.defaultdict(list)

        def get_duplicate_keys(counter):
            return [key for key, value in counter.items() if value > 1]

        all_node_names = [i.name for i in self.nodes]
        all_pipes_names = [i.name for i in self.pipes]
        all_wells_names = [i.name for i in self.wells]
        all_walls_names = [i.name for i in self.walls]
        all_material_names = [i.name for i in self.materials]
        all_pvt_names = list(self.pvt_models.tables.keys())
        all_pvt_names += list(self.pvt_models.correlations.keys())
        all_pvt_names += list(self.pvt_models.compositions.keys())

        all_fluids = [
            fluid
            for pvt_model in self.pvt_models.compositions.values()
            for fluid in pvt_model.fluids.keys()
        ]

        duplicate_names["Nodes"] = get_duplicate_keys(Counter(all_node_names))
        duplicate_names["Pipes"] = get_duplicate_keys(Counter(all_pipes_names))
        duplicate_names["Wells"] = get_duplicate_keys(Counter(all_wells_names))
        duplicate_names["Walls"] = get_duplicate_keys(Counter(all_walls_names))
        duplicate_names["Materials"] = get_duplicate_keys(Counter(all_material_names))
        duplicate_names["PVT"] = get_duplicate_keys(Counter(all_pvt_names))
        duplicate_names["Fluids"] = get_duplicate_keys(Counter(all_fluids))

        def get_error_msg():
            output = []
            for key, value in sorted(duplicate_names.items()):
                if value:
                    output.append(f"{key}:")
                    formatted_names = "\n    - ".join(name for name in value)
                    output.append(f"    - {formatted_names}")
            return "\n".join(output)

        if any(value for key, value in duplicate_names.items()):
            raise InvalidReferenceError(
                f"Elements that can be referenced must have a unique name, found multiples definitions of the following items:\n"
                f"{get_error_msg()}"
            )

        # Check unique name between elements
        duplicate_names["Nodes and Wells"] = get_duplicate_keys(
            Counter(all_wells_names + all_node_names)
        )
        duplicate_names["Pipes and Wells"] = get_duplicate_keys(
            Counter(all_wells_names + all_pipes_names)
        )

        if any(value for key, value in duplicate_names.items()):
            raise InvalidReferenceError(
                f"Some different type of elements needs to have unique name between them, found duplicated names for the following items:\n"
                f"{get_error_msg()}"
            )
