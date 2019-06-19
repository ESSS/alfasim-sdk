from enum import Enum
from typing import List

import attr
from attr import attrib
from attr.validators import deep_iterable
from attr.validators import instance_of
from attr.validators import optional
from barril.units import Scalar

from alfasim_sdk._validators import list_of_strings
from alfasim_sdk._validators import non_empty_str


@attr.s(kw_only=True)
class ErrorMessage:
    """
    The model_name and the message informed is displayed on the status monitor of ALFAsim.
    The execution of a new simulation will not be allowed until the error is solved.
    """

    model_name: str = attrib(validator=non_empty_str)
    message: str = attrib(validator=non_empty_str)


@attr.s(kw_only=True)
class WarningMessage:
    """
    The model_name and the message informed is displayed on the status monitor of ALFAsim.
    The execution of a new simulation will be kept normal.
    """

    model_name: str = attrib(validator=non_empty_str)
    message: str = attrib(validator=non_empty_str)


@attr.s(frozen=True)
class PluginInfo:
    name = attr.attrib(validator=non_empty_str)
    enabled = attr.attrib(validator=instance_of(bool))
    models = attr.attrib(validator=list_of_strings)


@attr.s(frozen=True)
class PipelineSegmentInfo:
    inner_diameter = attr.attrib(validator=instance_of(Scalar))
    start_position = attr.attrib(validator=instance_of(Scalar))
    is_custom = attr.attrib(validator=instance_of(bool))
    roughness = attr.attrib(validator=instance_of(Scalar))


list_of_segments = deep_iterable(
    member_validator=instance_of(PipelineSegmentInfo),
    iterable_validator=instance_of(list),
)


@attr.s(frozen=True)
class PipelineInfo:
    name = attr.attrib(type=str, validator=non_empty_str)
    edge_name = attr.attrib(type=str, validator=non_empty_str)
    segments = attr.attrib(type=List[PipelineSegmentInfo], validator=list_of_segments)
    total_length = attr.attrib(type=Scalar, validator=instance_of(Scalar))


@attr.s(frozen=True)
class NodeInfo:
    name = attr.attrib(validator=non_empty_str)
    number_of_phases_from_associated_pvt = attr.attrib(
        validator=optional(instance_of(int))
    )


@attr.s(frozen=True)
class EdgeInfo:
    name = attr.attrib(validator=non_empty_str)
    number_of_phases_from_associated_pvt = attr.attrib(
        validator=optional(instance_of(int))
    )


class EmulsionModelType(Enum):
    no_model = "EmulsionModelType.no_model"
    boxall2012 = "EmulsionModelType.boxall2012"
    brauner2001 = "EmulsionModelType.brauner2001"
    brinkman1952 = "EmulsionModelType.brinkman1952"
    brinkman1952_and_yeh1964 = "EmulsionModelType.brinkman1952_and_yeh1964"
    hinze1955 = "EmulsionModelType.hinze1955"
    model_default = "EmulsionModelType.model_default"
    mooney1951a = "EmulsionModelType.mooney1951a"
    mooney1951b = "EmulsionModelType.mooney1951b"
    sleicher1962 = "EmulsionModelType.sleicher1962"
    taylor1932 = "EmulsionModelType.taylor1932"


class SolidsModelType(Enum):
    no_model = "SolidsModelType.no_model"
    mills1985_equilibrium = "SolidsModelType.mills1985_equilibrium"
    santamaria2010_equilibrium = "SolidsModelType.santamaria2010_equilibrium"
    thomas1965_equilibrium = "SolidsModelType.thomas1965_equilibrium"


@attr.s(frozen=True)
class HydrodynamicModelInfo:
    phases = attr.attrib(validator=list_of_strings)
    fields = attr.attrib(validator=list_of_strings)
    layers = attr.attrib(validator=list_of_strings)
    has_water_phase = attr.attrib(type=bool, validator=instance_of(bool))


@attr.s(frozen=True)
class PhysicsOptionsInfo:
    emulsion_model = attr.attrib(validator=instance_of(EmulsionModelType))
    solids_model = attr.attrib(validator=instance_of(SolidsModelType))
    hydrodynamic_model = attr.attrib(validator=instance_of(HydrodynamicModelInfo))
