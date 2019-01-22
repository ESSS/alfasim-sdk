from enum import Enum

import attr
from attr import attrib
from attr.validators import instance_of


class Visibility(Enum):
    Internal = 'internal'
    Output = 'output'


class Location(Enum):
    Center = 'center'
    Face = 'face'


class Scope(Enum):
    Energy = 'energy'
    Field = 'field'
    Global = 'global'
    Layer = 'layer'
    Phase = 'phase'
    # TODO ASIM - 2348 Add Scope.ContinuousField and Scope.DispersedField
    # ContinuousField = 'continuous_field'
    # DispersedField = 'dispersed_field'


@attr.s(kw_only=True)
class Variable():
    name: str = attrib(validator=instance_of(str))
    caption: str = attrib(validator=instance_of(str))
    unit = attrib(validator=instance_of(str))
    visibility: Visibility = attrib(validator=instance_of(Visibility), default=Visibility.Output)
    location: Location = attrib(validator=instance_of(Location), default=Location.Center)
    multifield_scope: Scope = attrib(validator=instance_of(Scope), default=Scope.Global)
    checked_on_gui_default: bool = attrib(validator=instance_of(bool), default=True)
