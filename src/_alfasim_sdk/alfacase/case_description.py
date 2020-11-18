from enum import EnumMeta
from functools import partial
from numbers import Number
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import NewType
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union

import attr
import numpy as np
from attr.validators import deep_iterable
from attr.validators import deep_mapping
from attr.validators import in_
from attr.validators import instance_of
from attr.validators import optional
from barril.units import Array
from barril.units import Scalar

from _alfasim_sdk import constants

Numpy1DArray = NewType("Numpy1DArray", np.ndarray)
PhaseName = str


list_of_strings = deep_iterable(
    member_validator=optional(instance_of(str)), iterable_validator=instance_of(list)
)


def collapse_array_repr(value):
    """
    The full repr representation of PVT model takes too much space to print all values inside a array.
    Making annoying to debug Subjects that has a PVT model on it, due to seventy-four lines with only numbers.
    """
    import re

    return re.sub(r"array\(\[.*?\]\)", "array([...])", repr(value), flags=re.DOTALL)


def to_scalar(
    value: Union[Tuple[Number, str], Scalar], is_optional: bool = False
) -> Scalar:
    """
    Converter to be used with attr.ib, accepts tuples and Scalar as input
    If `is_optional` is defined, the converter will also accept None.

    Ex.:
    @attr.s
    class TrendOutputDescription:
        pos = attrib_scalar()
        temperature = attrib_scalar(converter=partial(ToScalar, is_optional=True))

    TrendOutputDescription(position=Scalar(1,"m")
    TrendOutputDescription(position=(1,"m")
    TrendOutputDescription(temperature=None)
    """
    if is_optional and value is None:
        return value
    if isinstance(value, tuple) and (len(value) == 2):
        return Scalar(value)
    elif isinstance(value, Scalar):
        return value

    raise TypeError(
        f"Expected pair (value, unit) or Scalar, got {value!r} (type: {type(value)})"
    )


attr_nothing_type = object


def attrib_scalar(
    default: Optional[
        Union[Tuple[Number, str], Scalar, attr_nothing_type]
    ] = attr.NOTHING,
    is_optional: bool = False,
) -> attr._make._CountingAttr:
    """
    Create a new attr attribute with a converter to Scalar accepting also tuple(value, unit).

    :param default:
        Value to be used as default when instantiating a class with this attr.ib

        If a default is not set (``attr.NOTHING``), a value must be supplied when instantiating;
        otherwise, a `TypeError` will be raised.
    """
    return attr.ib(
        default=default,
        converter=partial(to_scalar, is_optional=is_optional or not default),
        type=Optional[Scalar] if is_optional or not default else Scalar,
    )


def attrib_instance(type_) -> attr._make._CountingAttr:
    """
    Create a new attr attribute with validator for the given type_
    """
    return attr.ib(
        default=attr.Factory(type_), validator=instance_of(type_), type=type_
    )


def attrib_instance_list(
    type_, *, validator_type: Optional[Tuple[Any, ...]] = None
) -> attr._make._CountingAttr:
    """
    Create a new attr attribute with validator for the given type_
    All attributes created are expected to be List of the given type_

    :param validator_type:
        Inform which type(s) the List should validate.
        When not defined the param type_ will be used the type to be validated.

    """
    # Config validator
    _validator_type = validator_type or type_
    _validator = deep_iterable(
        member_validator=instance_of(_validator_type),
        iterable_validator=instance_of(list),
    )

    return attr.ib(default=attr.Factory(list), validator=_validator, type=List[type_])


def attrib_enum(
    type_: Optional[EnumMeta] = None, default: Any = attr.NOTHING
) -> attr._make._CountingAttr:
    """
    Create a new attr attribute with validator for enums
    When a default value is provided the type_ is automatically computed

    Ex.:
    class Foo(Enum):
        A = 'first'

    Valid calls:
        attrib_enum(type_=Foo)      # Default is attr.NOTHING, a value must be supplied when instantiating;
        attrib_enum(default=Foo.a)  # Default is Foo.a and type_ is Foo
        attrib_enum(type_=Foo, default=Foo.a)
    """
    if default is attr.NOTHING and not type_:
        raise RuntimeError("Default or type_ parameter must be provided")

    if default is not attr.NOTHING:
        type_ = type(default)

    if isinstance(default, EnumMeta):
        raise ValueError(
            f"Default must be a member of Enum and not the Enum class itself, got {default} while expecting"
            f" some of the following members {', '.join([str(i) for i in default])}"
        )
    return attr.ib(default=default, validator=in_(type_), type=type_)


def dict_of(type_):
    """
    An attr validator that performs validation of dictionary values.

    :param type_: The type to check for, can be a type or tuple of types

    :raises TypeError:
        raises a `TypeError` if the initializer is called with a wrong type for this particular attribute

    :return: An attr validator that performs validation of dictionary values.
    """
    return deep_mapping(
        key_validator=instance_of(str),
        value_validator=instance_of(type_),
        mapping_validator=instance_of(dict),
    )


def attrib_dict_of(type_) -> attr._make._CountingAttr:
    """
    Create a new attr attribute with validator for an atribute that is a dictionary with keys as str (to represent
    the name) and the content of an instance of type_
    """
    return attr.ib(
        default=attr.Factory(dict), validator=dict_of(type_), type=Dict[str, type_]
    )


dict_of_array = deep_mapping(
    key_validator=instance_of(str),
    value_validator=instance_of(Array),
    mapping_validator=instance_of(dict),
)


list_of_tracer_models = deep_iterable(
    member_validator=in_(constants.TracerModelType),
    iterable_validator=instance_of(list),
)


@attr.s(frozen=True, slots=True)
class PluginDescription:
    name: Optional[str] = attr.ib(default=None, validator=optional(instance_of(str)))
    gui_models = attr.ib(default=attr.Factory(list))
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
class TrendOutputDescription:
    curve_names: List[str] = attr.ib(validator=list_of_strings)
    element_name: str = attr.ib(validator=instance_of(str))
    position = attrib_scalar()
    location = attrib_enum(type_=constants.OutputAttachmentLocation)


@attr.s(frozen=True, slots=True)
class ProfileOutputDescription:
    curve_names: List[str] = attr.ib(validator=list_of_strings)
    element_name: str = attr.ib(validator=instance_of(str))
    location = attrib_enum(type_=constants.OutputAttachmentLocation)


@attr.s(frozen=True, slots=True)
class CaseOutputDescription:
    trends = attrib_instance_list(TrendOutputDescription)
    trend_frequency = attrib_scalar(default=Scalar(0.1, "s"))
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

    """

    fluid: Optional[str] = attr.ib(default=None, validator=optional(instance_of(str)))
    tracer_mass_fraction: Array = attr.ib(
        default=Array([], "-"), validator=instance_of(Array)
    )
    temperature = attrib_scalar(default=Scalar(constants.DEFAULT_TEMPERATURE_IN_K, "K"))

    source_type = attrib_enum(default=constants.MassSourceType.MassFlowRates)
    volumetric_flow_rates_std: Dict[str, Scalar] = attr.ib(
        default=attr.Factory(dict), validator=dict_of(Scalar)
    )
    mass_flow_rates: Dict[str, Scalar] = attr.ib(
        default=attr.Factory(dict), validator=dict_of(Scalar)
    )
    total_mass_flow_rate = attrib_scalar(default=Scalar(1.0, "kg/s", "mass flow rate"))
    water_cut = attrib_scalar(default=Scalar("volume fraction", 0.0, "-"))
    gas_oil_ratio = attrib_scalar(
        default=Scalar("standard volume per standard volume", 0.0, "sm3/sm3")
    )


@attr.s(kw_only=True)
class _PressureSourceCommon:
    pressure = attrib_scalar(default=Scalar(1.0e5, "Pa"))
    temperature = attrib_scalar(default=Scalar(constants.DEFAULT_TEMPERATURE_IN_K, "K"))
    fluid: Optional[str] = attr.ib(default=None, validator=optional(instance_of(str)))

    tracer_mass_fraction: Array = attr.ib(
        default=Array([], "-", "mass fraction"), validator=instance_of(Array)
    )

    split_type = attrib_enum(
        default=constants.MassInflowSplitType.ConstantVolumeFraction
    )
    mass_fractions: Dict[str, Scalar] = attr.ib(
        default=attr.Factory(dict), validator=dict_of(Scalar)
    )
    volume_fractions: Dict[str, Scalar] = attr.ib(
        default=attr.Factory(dict), validator=dict_of(Scalar)
    )
    gas_liquid_ratio = attrib_scalar(
        default=Scalar("standard volume per standard volume", 0.0, "sm3/sm3")
    )
    gas_oil_ratio = attrib_scalar(
        default=Scalar("standard volume per standard volume", 0.0, "sm3/sm3")
    )
    water_cut = attrib_scalar(default=Scalar("volume fraction", 0.0, "-"))


@attr.s(frozen=True, slots=True)
class CompositionDescription:
    """
    :ivar str Component:
        Name of the component available created on:
            * PvtModelCompositionalDescription.light_components
            * PvtModelCompositionalDescription.heavy_components
        Obs.: CompositionDescription can only refer to components created from the same PvtModelCompositionalDescription
    """

    component: str = attr.ib(validator=instance_of(str))
    molar_fraction = attrib_scalar(default=Scalar(0, "mol/mol"))
    reference_enthalpy = attrib_scalar(default=Scalar(0, "J/mol"))


@attr.s(frozen=True, slots=True)
class BipDescription:
    component_1: str = attr.ib(validator=instance_of(str))
    component_2: str = attr.ib(validator=instance_of(str))
    value: float = attr.ib(validator=instance_of(float), converter=float)


@attr.s(frozen=True, slots=True)
class FluidDescription:
    composition = attrib_instance_list(CompositionDescription)
    fraction_pairs = attrib_instance_list(BipDescription)


@attr.s(slots=True, kw_only=True)
class MassSourceEquipmentDescription(_MassSourceCommon):
    position = attrib_scalar()


@attr.s(frozen=True, slots=True, kw_only=True)
class SpeedCurveDescription:
    time: Array = attr.ib(default=Array([0], "s"), validator=instance_of(Array))
    speed: Array = attr.ib(default=Array([500], "rpm"), validator=instance_of(Array))


# fmt: off
@attr.s(frozen=True, slots=True, kw_only=True)
class TablePumpDescription:
    speeds: Array = attr.ib(
        default=Array([0.0] * 12 + [400.0] * 12 + [600.0] * 12, 'rpm'), validator=instance_of(Array)
    )
    void_fractions: Array = attr.ib(
        default=Array(([0.0] * 6 + [0.1] * 6) * 3, '-'), validator=instance_of(Array)
    )
    flow_rates: Array = attr.ib(
        default=Array([0.0, 0.05, 0.1, 0.15, 0.2, 0.3] * 6, 'm3/s'), validator=instance_of(Array)
    )

    pressure_boosts: Array = attr.ib(
        default=Array(
            [0.0] * 12
            + [
                12.0, 10.0, 9.0, 7.5, 5.0, 0.0, 10.0, 9.0, 8.0, 6.0, 3.5, 0.0,
                14.0, 12.0, 10.0, 8.0, 5.5, 0.0, 13.5, 11.2, 9.5, 7.6, 5.2, 0.0,
            ],
            'bar',
        ),
        validator=instance_of(Array),
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
    position = attrib_scalar()
    type = attrib_enum(default=constants.PumpType.ConstantPressure)
    pressure_boost = attrib_scalar(default=Scalar(1.0e5, "Pa"))
    thermal_efficiency = attrib_scalar(default=Scalar(100.0, "%"))
    table = attrib_instance(TablePumpDescription)
    speed_curve = attrib_instance(SpeedCurveDescription)
    speed_curve_interpolation_type = attrib_enum(
        default=constants.InterpolationType.Constant
    )
    flow_direction = attrib_enum(default=constants.FlowDirection.Forward)
    # @TODO: ASIM-3522 - Remove deprecated split equipment code
    nonsplit_equipment: bool = attr.ib(default=True, validator=instance_of(bool))


@attr.s(frozen=True, slots=True)
class CompressorPressureTableDescription:
    """
    :ivar corrected_mass_flow_rate_entries:
        Equivalent to `m * (T/T_ref)**0.5 / (P/P_ref)`
    """

    speed_entries: Array = attr.ib(
        default=Array([0], "rpm"), validator=instance_of(Array)
    )
    corrected_mass_flow_rate_entries: Array = attr.ib(
        default=Array([0], "kg/s"), validator=instance_of(Array)
    )
    pressure_ratio_table: Array = attr.ib(
        default=Array([1.0], "-"), validator=instance_of(Array)
    )
    isentropic_efficiency_table: Array = attr.ib(
        default=Array([1.0], "-"), validator=instance_of(Array)
    )

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
    position = attrib_scalar()
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
    # @TODO: ASIM-3522 - Remove deprecated split equipment code
    nonsplit_equipment: bool = attr.ib(default=True, validator=instance_of(bool))


@attr.s(frozen=True, slots=True)
class OpeningCurveDescription:
    time: Array = attr.ib(validator=instance_of(Array), default=Array([], "s"))
    opening: Array = attr.ib(validator=instance_of(Array), default=Array([], "-"))

    def __attrs_post_init__(self):
        if len(self.time) != len(self.opening):
            msg = (
                f"Time and Opening must have the same size, got {len(self.time)} "
                f"items for time and {len(self.opening)} for opening"
            )
            raise ValueError(msg)


@attr.s(frozen=True, slots=True)
class CvTableDescription:
    opening: Array = attr.ib(validator=instance_of(Array), default=Array([], "-"))
    flow_coefficient: Array = attr.ib(
        validator=instance_of(Array), default=Array([], "(galUS/min)/(psi^0.5)")
    )

    def __attrs_post_init__(self):
        if len(self.flow_coefficient) != len(self.opening):
            msg = (
                f"Opening and Flow Coefficient must have the same size, got {len(self.flow_coefficient)} "
                f"items for flow_coefficient and {len(self.opening)} for opening"
            )
            raise ValueError(msg)


@attr.s(frozen=True, slots=True)
class ValveEquipmentDescription:
    position = attrib_scalar()
    type = attrib_enum(default=constants.ValveType.PerkinsValve)
    diameter = attrib_scalar(default=Scalar(0.01, "m"))
    flow_direction = attrib_enum(default=constants.FlowDirection.Forward)

    # When ValveType is not CheckValve
    opening_type = attrib_enum(default=constants.ValveOpeningType.ConstantOpening)
    # --> When ValveOpeningType.ConstantOpening
    opening = attrib_scalar(default=Scalar("dimensionless", 100, "%"))
    # --> When ValveOpeningType.TableInterpolation
    opening_curve_interpolation_type = attrib_enum(
        default=constants.InterpolationType.Constant
    )
    opening_curve = attrib_instance(OpeningCurveDescription)
    # When ValveType.ChokeValveWithFlowCoefficient
    cv_table = attrib_instance(CvTableDescription)

    # @TODO: ASIM-3522 - Remove deprecated split equipment code
    nonsplit_equipment: bool = attr.ib(default=True, validator=instance_of(bool))


@attr.s(frozen=True, slots=True, kw_only=True)
class IPRCurveDescription:
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
    min_pressure_difference = attrib_scalar(default=Scalar(0.0, "Pa"))
    well_index = attrib_scalar(default=Scalar(24.0, "m3/bar.d"))


@attr.s(frozen=True, slots=True)
class TableIPRDescription(CommonIPR):
    table = attrib_instance(IPRCurveDescription)


@attr.s(frozen=True, slots=True)
class IPRModelsDescription:
    """
    :cvar Dict[str, Union[str, IPRDescription]] tables:
        A dictionary with the name of the IPR and the instance of the IPR Model.
    """

    linear_models: Dict[str, LinearIPRDescription] = attr.ib(
        default=attr.Factory(dict), validator=dict_of(LinearIPRDescription)
    )
    table_models: Dict[str, TableIPRDescription] = attr.ib(
        default=attr.Factory(dict), validator=dict_of(TableIPRDescription)
    )


@attr.s(slots=True)
class ReservoirInflowEquipmentDescription(_PressureSourceCommon):
    start = attrib_scalar()
    length = attrib_scalar()
    productivity_ipr: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )
    injectivity_ipr: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )


@attr.s(frozen=True, slots=True)
class HeatSourceEquipmentDescription:
    start = attrib_scalar()
    length = attrib_scalar()
    power = attrib_scalar()


@attr.s(frozen=True, slots=True)
class PipeSegmentsDescription:
    start_positions: Array = attr.ib(validator=optional(instance_of(Array)))
    diameters: Array = attr.ib(validator=optional(instance_of(Array)))
    roughnesses: Array = attr.ib(validator=optional(instance_of(Array)))
    wall_names: Optional[List[str]] = attr.ib(
        default=None, validator=optional(list_of_strings)
    )


@attr.s(frozen=True, slots=True)
class ReferencedPressureContainerDescription:
    reference_coordinate: Scalar = attr.ib(default=Scalar(0.0, "m"))
    positions: Array = attr.ib(default=Array([0.0], "m"))
    pressures: Array = attr.ib(default=Array([1e5], "Pa"))


@attr.s(frozen=True, slots=True)
class PressureContainerDescription:
    positions: Array = attr.ib(default=Array([0.0], "m"))
    pressures: Array = attr.ib(default=Array([1e5], "Pa"))


@attr.s(frozen=True, slots=True)
class InitialPressuresDescription:
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
    reference_coordinate: Scalar = attr.ib(default=Scalar(0.0, "m"))
    positions: Array = attr.ib(default=Array([], "m"))
    fractions: Dict[PhaseName, Array] = attr.ib(default={})


@attr.s(frozen=True, slots=True)
class VolumeFractionsContainerDescription:
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
    reference_coordinate: Scalar = attr.ib(default=Scalar(0.0, "m"))
    positions: Array = attr.ib(default=Array([], "m"))
    tracers_mass_fractions: List[Array] = attr.ib(default=[])


@attr.s(frozen=True, slots=True)
class TracersMassFractionsContainerDescription:
    positions: Array = attr.ib(default=Array([], "m"))
    tracers_mass_fractions: List[Array] = attr.ib(default=[])


@attr.s(frozen=True, slots=True)
class InitialTracersMassFractionsDescription:
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
    reference_coordinate: Scalar = attr.ib(default=Scalar(0.0, "m"))
    positions: Array = attr.ib(default=Array([], "m"))
    velocities: Dict[PhaseName, Array] = attr.ib(default={})


@attr.s(frozen=True, slots=True)
class VelocitiesContainerDescription:
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
    reference_coordinate: Scalar = attr.ib(default=Scalar(0.0, "m"))
    positions: Array = attr.ib(default=Array([], "m"))
    temperatures: Array = attr.ib(default=Array([], "K"))


@attr.s(frozen=True, slots=True)
class TemperaturesContainerDescription:
    positions: Array = attr.ib(default=Array([0.0], "m"))
    temperatures: Array = attr.ib(
        default=Array([constants.DEFAULT_TEMPERATURE_IN_K], "K")
    )


@attr.s(frozen=True, slots=True)
class InitialTemperaturesDescription:
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


list_of_pipe_environment_heat_transfer_coefficient = deep_iterable(
    member_validator=in_(constants.PipeEnvironmentHeatTransferCoefficientModelType),
    iterable_validator=instance_of(list),
)


@attr.s(frozen=True, slots=True)
class LengthAndElevationDescription:
    """
    Describe a pipe with length and elevation.
    """

    length: Optional[Array] = attr.ib(
        default=None, validator=optional(instance_of(Array))
    )
    elevation: Optional[Array] = attr.ib(
        default=None, validator=optional(instance_of(Array))
    )

    def iter_values_and_unit(
        self,
    ) -> Iterator[Tuple[Tuple[Number, str], Tuple[Number, str]]]:
        """ Returns a pair of values with length and elevation along with their units. """
        length_values = self.length.GetValues(self.length.unit)
        elevation_values = self.elevation.GetValues(self.elevation.unit)
        for length, elevation in zip(length_values, elevation_values):
            yield (length, self.length.unit), (elevation, self.elevation.unit)


@attr.s(frozen=True, slots=True)
class XAndYDescription:
    """
    Describe a pipe with a sequence of coordinates.
    """

    x: Optional[Array] = attr.ib(default=None, validator=optional(instance_of(Array)))
    y: Optional[Array] = attr.ib(default=None, validator=optional(instance_of(Array)))

    def iter_values_and_unit(
        self,
    ) -> Iterator[Tuple[Tuple[Number, str], Tuple[Number, str]]]:
        """ Returns a pair of values with the x and y value along with their units. """
        for x, y in zip(self.x.GetValues(self.x.unit), self.y.GetValues(self.y.unit)):
            yield (x, self.x.unit), (y, self.y.unit)


@attr.s()
class ProfileDescription:
    """
    Describe a pipe by either length and inclination or by X and Y coordinates.

    * LengthAndElevation: a list of points with the length and elevation.
     The first item *MUST* always be (0, 0), otherwise a ValueError is raised.

    * XAndY: a list of points (X, Y), describing the coordinates.

    .. note:: x_and_y and length_and_elevation are mutually exclusive.

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
    mass_sources = attrib_dict_of(MassSourceEquipmentDescription)
    pumps = attrib_dict_of(PumpEquipmentDescription)
    valves = attrib_dict_of(ValveEquipmentDescription)
    reservoir_inflows = attrib_dict_of(ReservoirInflowEquipmentDescription)
    heat_sources = attrib_dict_of(HeatSourceEquipmentDescription)
    compressors = attrib_dict_of(CompressorEquipmentDescription)


@attr.s(frozen=True, slots=True, kw_only=True)
class EnvironmentPropertyDescription:
    position = attrib_scalar()
    temperature = attrib_scalar()
    type = attrib_enum(type_=constants.PipeEnvironmentHeatTransferCoefficientModelType)
    heat_transfer_coefficient = attrib_scalar(default=Scalar(0.0, "W/m2.K"))
    overall_heat_transfer_coefficient = attrib_scalar(default=Scalar(0.0, "W/m2.K"))
    fluid_velocity = attrib_scalar(default=Scalar(0.0, "m/s"))


@attr.s(frozen=True, slots=True, kw_only=True)
class EnvironmentDescription:
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


dict_with_scalar = deep_mapping(
    key_validator=instance_of(str),
    value_validator=instance_of(Scalar),
    mapping_validator=instance_of(dict),
)


@attr.s(slots=True, kw_only=True)
class PressureNodePropertiesDescription(_PressureSourceCommon):
    """"""


@attr.s(slots=True, kw_only=True)
class MassSourceNodePropertiesDescription(_MassSourceCommon):
    """"""


@attr.s(slots=True, kw_only=True)
class InternalNodePropertiesDescription:
    fluid: Optional[str] = attr.ib(default=None, validator=optional(instance_of(str)))


@attr.s(slots=True, kw_only=True)
class SeparatorNodePropertiesDescription:
    """
    :ivar overall_heat_transfer_coefficient:
        η such that the overall heat transferred to the separator is
            Q = η A (T_amb - T_sep)
    """

    environment_temperature = attrib_scalar(default=Scalar(25.0, "degC"))
    geometry = attrib_enum(default=constants.SeparatorGeometryType.VerticalCylinder)
    length = attrib_scalar(default=Scalar(1.0, "m"))
    overall_heat_transfer_coefficient = attrib_scalar(default=Scalar(0.0, "W/m2.K"))
    radius = attrib_scalar(default=Scalar(1.0, "m"))
    nozzles: Dict[str, Scalar] = attr.ib(
        default=attr.Factory(dict), validator=optional(dict_with_scalar)
    )
    initial_phase_volume_fractions: Dict[str, Scalar] = attr.ib(
        default={
            constants.FLUID_GAS: Scalar("volume fraction", 0.5, "-"),
            constants.FLUID_OIL: Scalar("volume fraction", 0.5, "-"),
        }
    )

    @radius.validator
    def _validate_radius(self, attribute, value):
        assert (
            isinstance(value, Scalar) and value.GetCategory() == "length"
        ), "Invalid radius"

    @length.validator
    def _validate_length(self, attribute, value):
        assert (
            isinstance(value, Scalar) and value.GetCategory() == "length"
        ), "Invalid length"


@attr.s(slots=True, kw_only=True)
class NodeDescription:
    name: str = attr.ib()
    node_type = attrib_enum(type_=constants.NodeCellType)
    pvt_model: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )
    pressure_properties = attrib_instance(PressureNodePropertiesDescription)
    mass_source_properties = attrib_instance(MassSourceNodePropertiesDescription)
    internal_properties = attrib_instance(InternalNodePropertiesDescription)
    separator_properties = attrib_instance(SeparatorNodePropertiesDescription)


@attr.s(frozen=True, slots=True, kw_only=True)
class FormationLayerDescription:
    name: str = attr.ib(validator=instance_of(str))
    start = attrib_scalar()
    material: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )


@attr.s(frozen=True, slots=True, kw_only=True)
class FormationDescription:
    reference_y_coordinate = attrib_scalar()
    layers = attrib_instance_list(FormationLayerDescription)


@attr.s(frozen=True, slots=True, kw_only=True)
class CasingSectionDescription:
    name: str = attr.ib(validator=instance_of(str))
    hanger_depth = attrib_scalar()
    settings_depth = attrib_scalar()
    hole_diameter = attrib_scalar()
    outer_diameter = attrib_scalar()
    inner_diameter = attrib_scalar()
    inner_roughness = attrib_scalar()
    material: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )
    top_of_filler = attrib_scalar()
    filler_material: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )
    material_above_filler: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )


@attr.s(frozen=True, slots=True, kw_only=True)
class TubingDescription:
    name: str = attr.ib(validator=instance_of(str))
    length = attrib_scalar()
    outer_diameter = attrib_scalar()
    inner_diameter = attrib_scalar()
    inner_roughness = attrib_scalar()
    material: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )


@attr.s(frozen=True, slots=True, kw_only=True)
class PackerDescription:
    name: str = attr.ib(validator=instance_of(str))
    position = attrib_scalar()
    material_above: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )


@attr.s(frozen=True, slots=True, kw_only=True)
class OpenHoleDescription:
    name: str = attr.ib(validator=instance_of(str))
    length = attrib_scalar()
    diameter = attrib_scalar()
    inner_roughness = attrib_scalar()


@attr.s(frozen=True, slots=True, kw_only=True)
class CasingDescription:
    casing_sections = attrib_instance_list(CasingSectionDescription)
    tubings = attrib_instance_list(TubingDescription)
    packers = attrib_instance_list(PackerDescription)
    open_holes = attrib_instance_list(OpenHoleDescription)


@attr.s(frozen=True, slots=True, kw_only=True)
class GasLiftValveEquipmentDescription:
    position = attrib_scalar()
    diameter = attrib_scalar()
    valve_type = attrib_enum(type_=constants.ValveType)
    delta_p_min = attrib_scalar()
    discharge_coeff = attrib_scalar()


@attr.s(slots=True, kw_only=True)
class AnnulusDescription:
    has_annulus_flow: bool = attr.ib(validator=instance_of(bool))
    pvt_model: Optional[str] = attr.ib(
        default=None, validator=optional(instance_of(str))
    )
    initial_conditions = attrib_instance(InitialConditionsDescription)
    gas_lift_valve_equipment = attrib_dict_of(GasLiftValveEquipmentDescription)
    top_node: str = attr.ib(validator=instance_of(str))


@attr.s(slots=True, kw_only=True)
class WellDescription:
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
    name: str = attr.ib(validator=instance_of(str))
    material_type = attrib_enum(default=constants.MaterialType.Solid)
    density = attrib_scalar(default=Scalar(1, "kg/m3"))
    thermal_conductivity = attrib_scalar(default=Scalar(0, "W/m.degC"))
    heat_capacity = attrib_scalar(default=Scalar(0, "J/kg.degC"))
    inner_emissivity = attrib_scalar(default=Scalar("emissivity", 0, "-"))
    outer_emissivity = attrib_scalar(default=Scalar("emissivity", 0, "-"))
    expansion = attrib_scalar(default=Scalar(0, "1/K"))
    viscosity = attrib_scalar(default=Scalar(0, "cP"))

    def as_dict(self) -> Dict[str, Union[str, Tuple[Number, str]]]:
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

    :ivar Tuple(float,str) thickness:
    :ivar str material_name:
    """

    thickness: Scalar = attr.ib(validator=instance_of(Scalar))
    material_name: str = attr.ib(validator=instance_of(str))
    has_annulus_flow: bool = attr.ib(default=False, validator=instance_of(bool))


@attr.s
class WallDescription:
    name: str = attr.ib(validator=instance_of(str))
    inner_roughness = attrib_scalar(default=Scalar(0, "m"))
    wall_layer_container = attrib_instance_list(WallLayerDescription)


dict_of_wall_description = deep_mapping(
    key_validator=instance_of(str),
    value_validator=instance_of(WallDescription),
    mapping_validator=instance_of(dict),
)
list_of_numbers = deep_iterable(
    member_validator=instance_of(Number), iterable_validator=instance_of((list, range))
)
dict_with_a_list_of_numbers = deep_mapping(
    key_validator=instance_of(str),
    value_validator=list_of_numbers,
    mapping_validator=instance_of(dict),
)


@attr.s(frozen=True, slots=True)
class PvtModelCorrelationDescription:
    oil_density_std = attrib_scalar(default=Scalar(850.0, "kg/m3"))
    gas_density_std = attrib_scalar(default=Scalar(0.9, "kg/m3"))
    rs_sat = attrib_scalar(default=Scalar(150.0, "sm3/sm3"))
    pvt_correlation_package = attrib_enum(default=constants.CorrelationPackage.Standing)


@attr.s(frozen=True, slots=True)
class HeavyComponentDescription:
    name: str = attr.ib(validator=instance_of(str))
    scn: int = attr.ib(validator=instance_of(int), converter=int)
    MW = attrib_scalar(default=Scalar(0, "kg/mol"))
    rho = attrib_scalar(default=Scalar(0, "kg/m3"))


@attr.s(frozen=True, slots=True)
class LightComponentDescription:
    name: str = attr.ib(validator=instance_of(str))
    Pc = attrib_scalar(default=Scalar("pressure", 0, "Pa"))
    Tc = attrib_scalar(default=Scalar("temperature", 0, "K"))
    Vc = attrib_scalar(default=Scalar("molar volume", 0, "m3/mol"))
    omega = attrib_scalar(default=Scalar("dimensionless", 0, "-"))
    MW = attrib_scalar(default=Scalar("mass per mol", 0, "kg/mol"))
    Tb = attrib_scalar(default=Scalar("temperature", 0, "K"))
    Parachor = attrib_scalar(default=Scalar("dimensionless", 0, "-"))
    B_parameter = attrib_scalar(default=Scalar("dimensionless", 0, "-"))
    Cp_0 = attrib_scalar(default=Scalar("dimensionless", 0, "-"))
    Cp_1 = attrib_scalar(default=Scalar("dimensionless", 0, "-"))
    Cp_2 = attrib_scalar(default=Scalar("dimensionless", 0, "-"))
    Cp_3 = attrib_scalar(default=Scalar("dimensionless", 0, "-"))
    Cp_4 = attrib_scalar(default=Scalar("dimensionless", 0, "-"))


@attr.s(slots=True)
class PvtModelCompositionalDescription:
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


def list_of(type_):
    """
    An attr validator that performs validation of list values.

    :param type_: The type to check for, can be a type or tuple of types

    :raises TypeError:
        raises a `TypeError` if the initializer is called with a wrong type for this particular attribute

    :return: An attr validator that performs validation of values of a list.
    """
    return deep_iterable(
        member_validator=instance_of(type_), iterable_validator=instance_of(list)
    )


def numpy_array_validator(dimension: int, is_list: bool = False):
    """
     An attr validator that performs validation of numpy arrays
    :param dimension:
        The number of array dimensions accepts.
    :param is_list:
        A flag to indicate if the attribute is a container of ndarray

    :return: An attr validator that performs validation of instances of ndarray and their dimensions.
    """

    def _numpy_array_validator(instance, attribute, value):
        def _check_dimension(value, *, position=None):
            """Helper method to check the dimension from ndarray"""
            if value.ndim != dimension:
                raise ValueError(
                    f"attribute '{attribute.name}' from class '{instance.__class__.__name__}' only accepts ndarray "
                    f"with dimension equals to {dimension}, got a ndarray with dimension {value.ndim}"
                    f"{' on position ' + str(position) + '.' if position is not None else '.'}"
                )

        if is_list:
            list_of(np.ndarray)(instance, attribute, value)
            for index, value_from_list in enumerate(value):
                _check_dimension(value=value_from_list, position=index)
        else:
            instance_of(np.ndarray)(instance, attribute, value)
            _check_dimension(value)

    return _numpy_array_validator


@attr.s(slots=True, eq=False)
class PvtModelTableParametersDescription:
    """
    :ivar ndarray(shape=(M,1)) pressure_values:
        Array like of sorted pressure values (m number of entries). [Pa]

    :ivar ndarray(shape=(N,1)) temperature_values:
        Array like of sorted temperature values (n number of entries). [K]

    :ivar List[ndarray(shape=(MxN,1))] table_variables:
        List of array like values for each property such as densities, specific heats,
        enthalpies, etc.

    :ivar List[str] variable_names:
        List of property names
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

    :cvar correlations:
        Standard black-oil correlations found in the literature. The user can tune the parameters used by the correlations.

    :cvar compositions:
        Molar fluid compositions with molecular weights and densities for each component.
        It be light components and/or heavy fractions to be lumped into pseudo-components.

    :cvar tables:
        Load a complete PVT table obtained (usually) from lab results and generated by various software.
        Currently the user can import the table directly from a `.tab` file or a `.alfatable` file.

        The table parameter must be filled with a dictionary where the keys informs the name of the PVT and
        the values informs Path to a file with the Pvt model.

            - The value which holds the Path can be either relative or absolute.
            - The name of the pvt model from the Path can contains a 'pipe' character in order to select one of
              the multiples PVT tables in the same .tab file.

            Ex.:
                For Absolute Path: Path("/home/user/my_file.tab|MyPvtModel")
                For Relative Path: Path("./my_file.tab|MyPvtModel")

    :cvar table_parameters:
        *INTERNAL USE ONLY*

        This attribute is populated when exporting a Study to a CaseDescription, and it holds a model representation
        of a PVT originated from a (.tab / .alfatable) file.

        Their usage is directly related to the export of a CaseDescription to a `.alfacase`/`.alfatable` file,
        where the original PVT file cannot be guaranteed to exist therefore the only reproducible way to recreate
        the PVT is trough the PvtModelTableParametersDescription.

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


class DescriptionError(Exception):
    """
    Base exception for exceptions in case description.
    """


class InvalidReferenceError(DescriptionError):
    """
    Error raised when an attribute has a reference for an element that doesn't exist.
    """


class InvalidYamlData(DescriptionError):
    """
    Error raised when some data in the YAML file is not properly configured.
    """


@attr.s()
class TracerModelConstantCoefficientsDescription:
    partition_coefficients: Dict[str, Scalar] = attr.ib(
        default=attr.Factory(dict), validator=dict_of(Scalar)
    )


@attr.s()
class TracersDescription:
    constant_coefficients: Dict[
        str, TracerModelConstantCoefficientsDescription
    ] = attr.ib(
        default=attr.Factory(dict),
        validator=dict_of(TracerModelConstantCoefficientsDescription),
    )


@attr.s()
class PhysicsDescription:
    hydrodynamic_model = attrib_enum(default=constants.HydrodynamicModelType.FourFields)
    simulation_regime = attrib_enum(default=constants.SimulationRegimeType.Transient)
    energy_model = attrib_enum(default=constants.EnergyModel.NoModel)
    solids_model = attrib_enum(default=constants.SolidsModelType.NoModel)
    initial_condition_strategy = attrib_enum(
        default=constants.InitialConditionStrategyType.Constant
    )
    restart_filepath: Optional[Path] = attr.ib(
        default=None, validator=optional(instance_of(Path))
    )
    keep_former_results: bool = attr.ib(default=False, validator=instance_of(bool))
    emulsion_model = attrib_enum(default=constants.EmulsionModelType.NoModel)
    flash_model = attrib_enum(default=constants.FlashModel.HydrocarbonAndWater)
    correlations_package = attrib_enum(
        default=constants.CorrelationPackageType.Classical
    )


@attr.s()
class TimeOptionsDescription:
    stop_on_steady_state: bool = attr.ib(default=False, validator=instance_of(bool))
    initial_time = attrib_scalar(default=Scalar("time", 0.0, "s"))
    final_time = attrib_scalar(default=Scalar("time", 10.0, "s"))
    initial_timestep = attrib_scalar(default=Scalar("time", 1e-4, "s"))
    minimum_timestep = attrib_scalar(default=Scalar("time", 1e-12, "s"))
    maximum_timestep = attrib_scalar(default=Scalar("time", 0.1, "s"))
    restart_autosave_frequency = attrib_scalar(default=Scalar("time", 1, "h"))
    minimum_time_for_steady_state_stop = attrib_scalar(default=Scalar("time", 0.0, "s"))


@attr.s()
class NumericalOptionsDescription:
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

        :param bool reset_invalid_reference:
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
