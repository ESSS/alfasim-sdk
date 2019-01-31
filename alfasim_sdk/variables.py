import numbers
from enum import Enum
from typing import Optional

import attr
from attr import attrib
from attr.validators import instance_of, optional
from barril.units import UnitDatabase

from alfasim_sdk._validators import check_for_valid_unit, check_string_is_not_empty


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
class SecondaryVariable():
    name: str = attrib(validator=[instance_of(str), check_string_is_not_empty])
    caption: str = attrib(validator=[instance_of(str), check_string_is_not_empty])
    unit = attrib(validator=[instance_of(str), check_string_is_not_empty, check_for_valid_unit])
    visibility: Visibility = attrib(validator=instance_of(Visibility), default=Visibility.Output)
    location: Location = attrib(validator=instance_of(Location), default=Location.Center)
    multifield_scope: Scope = attrib(validator=instance_of(Scope), default=Scope.Global)
    default_value: Optional[numbers.Real] = attrib(validator=optional(instance_of(numbers.Real)), default=None)
    checked_on_gui_default: bool = attrib(validator=instance_of(bool), default=True)

    @property
    def category(self):
        return UnitDatabase.GetSingleton().GetDefaultCategory(self.unit)
