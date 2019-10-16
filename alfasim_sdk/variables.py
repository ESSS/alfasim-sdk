import numbers
from enum import Enum
from typing import Optional

import attr
from attr import attrib
from attr.validators import instance_of
from attr.validators import optional
from barril.units import UnitDatabase

from alfasim_sdk._validators import non_empty_str
from alfasim_sdk._validators import valid_unit


class Visibility(Enum):
    """
    Controls the visibility of the variable.
        - Internal: The variable should only be used by the plugin, but not available to the end-user.
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
    """
    Secondary variables are those variables that are not unknowns from the nonlinear system.
    That is, they are not directly solved in the nonlinear system, but they are calculated based on the nonlinear system results.

    :param str name:
    :param str caption:
    :param alfasim_sdk.variables.Type type:
    :param str unit:
    :param alfasim_sdk.variables.Visibility visibility:
    :param alfasim_sdk.variables.Location location:
    :param alfasim_sdk.variables.Scope multifield_scope:
    :param number.Real default_value:
    :param bool checked_on_gui_default:
    """

    name: str = attrib(validator=non_empty_str)
    caption: str = attrib(validator=non_empty_str)
    type = attrib(validator=instance_of(Type), default=Type.Double)
    unit = attrib(validator=[non_empty_str, valid_unit])
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
