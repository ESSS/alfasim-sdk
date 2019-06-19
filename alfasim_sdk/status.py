from enum import Enum

import attr
from attr import attrib
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
    edge_name = attr.attrib(validator=non_empty_str)
    inner_diameter = attr.attrib(validator=instance_of(Scalar))
    start_position = attr.attrib(validator=instance_of(Scalar))
    roughness = attr.attrib(validator=instance_of(Scalar))


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


@attr.s(frozen=True)
class PhysicsOptionsInfo:
    emulsion_model = attr.attrib(validator=instance_of(EmulsionModelType))
    solids_model = attr.attrib(validator=instance_of(SolidsModelType))
    hydrodynamic_model = attr.attrib(validator=instance_of(HydrodynamicModelInfo))
