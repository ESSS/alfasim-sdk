from enum import Enum
from typing import List

import attr
from attr import attrib
from attr.validators import deep_iterable
from attr.validators import instance_of
from barril.units import Scalar

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
    models = attr.attrib(
        validator=deep_iterable(
            member_validator=instance_of(str), iterable_validator=instance_of(list)
        )
    )


@attr.s(frozen=True)
class PipelineSegmentInfo:
    edge_name = attr.attrib(validator=non_empty_str)
    inner_diameter = attr.attrib(validator=instance_of(Scalar))
    start_position = attr.attrib(validator=instance_of(Scalar))


@attr.s(frozen=True)
class NodesInfo:
    name = attr.attrib(validator=non_empty_str)
    number_of_phases = attr.attrib(validator=instance_of(int))


@attr.s(frozen=True)
class EdgesInfo:
    name = attr.attrib(validator=non_empty_str)
    number_of_phases = attr.attrib(validator=instance_of(int))


class EmulsionModelType(Enum):
    boxall2012 = "EmulsionModelType.boxall2012"
    brauner2001 = "EmulsionModelType.brauner2001"
    brinkman1952 = "EmulsionModelType.brinkman1952"
    brinkman1952_and_yeh1964 = "EmulsionModelType.brinkman1952_and_yeh1964"
    hinze1955 = "EmulsionModelType.hinze1955"
    model_default = "EmulsionModelType.model_default"
    mooney1951a = "EmulsionModelType.mooney1951a"
    mooney1951b = "EmulsionModelType.mooney1951b"
    no_model = "EmulsionModelType.no_model"
    sleicher1962 = "EmulsionModelType.sleicher1962"
    taylor1932 = "EmulsionModelType.taylor1932"


class SolidsModelType(Enum):
    mills1985_equilibrium = "SolidsModelType.mills1985_equilibrium"
    no_model = "SolidsModelType.no_model"
    santamaria2010_equilibrium = "SolidsModelType.santamaria2010_equilibrium"
    thomas1965_equilibrium = "SolidsModelType.thomas1965_equilibrium"


@attr.s(frozen=True)
class HydrodynamicModelInfo:
    phases: List[str] = attr.attrib()
    fields: List[str] = attr.attrib()
    layers: List[str] = attr.attrib()


@attr.s(frozen=True)
class PhysicsOptionsInfo:
    emulsion_model = attr.attrib(validator=instance_of(EmulsionModelType))
    solids_model = attr.attrib(validator=instance_of(SolidsModelType))
    hydrodynamic_model = attr.attrib(validator=instance_of(HydrodynamicModelInfo))
