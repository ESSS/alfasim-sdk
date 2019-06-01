import numbers
from enum import Enum
from typing import Optional

import attr
from attr import attrib
from attr.validators import instance_of
from attr.validators import optional
from barril.units import UnitDatabase

from alfasim_sdk._validators import check_string_is_not_empty
from alfasim_sdk._validators import check_unit_is_valid


class Visibility(Enum):
    """
    Controls the visibility of the variable.
        - Internal: The variable should only be used by the plugin, but not available to the end user.
        - Output: The variable should be available to the end user, as a Property on Plot Window
    """

    Internal = "internal"
    Output = "output"


class Type(Enum):
    Double = "Double"
    Int = "Int"


class Location(Enum):
    Center = "center"
    Face = "face"


class Scope(Enum):
    Energy = "energy"
    Field = "field"
    Global = "global"
    Layer = "layer"
    Phase = "phase"
    # TODO ASIM - 2348 Add Scope.ContinuousField and Scope.DispersedField
    # ContinuousField = 'continuous_field'
    # DispersedField = 'dispersed_field'


@attr.s(kw_only=True)
class SecondaryVariable:
    name: str = attrib(validator=[instance_of(str), check_string_is_not_empty])
    caption: str = attrib(validator=[instance_of(str), check_string_is_not_empty])
    type = attrib(validator=instance_of(Type), default=Type.Double)
    unit = attrib(
        validator=[instance_of(str), check_string_is_not_empty, check_unit_is_valid]
    )
    visibility: Visibility = attrib(
        validator=instance_of(Visibility), default=Visibility.Output
    )
    location: Location = attrib(
        validator=instance_of(Location), default=Location.Center
    )
    multifield_scope: Scope = attrib(validator=instance_of(Scope), default=Scope.Global)
    default_value: Optional[numbers.Real] = attrib(
        validator=optional(instance_of(numbers.Real)), default=None
    )
    checked_on_gui_default: bool = attrib(validator=instance_of(bool), default=True)

    @property
    def category(self):
        return UnitDatabase.GetSingleton().GetDefaultCategory(self.unit)
