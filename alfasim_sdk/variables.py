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
        - ``Internal``: The variable should only be used by the plugin, but not available to the end-user.
        - ``Output``: The variable should be available to the end user, as a Property on Plot Window
    """

    Internal = "internal"
    Output = "output"


class Type(Enum):
    """
    Indicates the type of the variable.
        - ``Double``: Double precision floating point data type.
        - ``Int``: Integral data type.
    """

    Double = "Double"
    Int = "Int"


class Location(Enum):
    """
    Controls the Location of the variable in the pipe discretization.
        - ``Center``: Center of the control volumes.
        - ``Face``: Faces of control volumes.
    """

    Center = "center"
    Face = "face"


class Scope(Enum):
    """
    Controls the Scope of the variable.
        - ``Energy``: One value for each energy equation (One for `GLOBAL` model and number of layers for `LAYER` model).
        - ``Global``: One global value (or related to the mixture).
        - ``Field``: One value for each field of the hydrodynamic model.
        - ``Layer``: One value for each layer of the hydrodynamic model.
        - ``Phase``: One value for each phase of the hydrodynamic model.
    """

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

    :param name: Plugin secondary variable name. This name will be used to access it in the :ref:`solver_hooks`.
    :param caption: Caption to be shown in the GUI (For output purpose).
    :param type: a :class:`~alfasim_sdk.variables.Type` value.
    :param unit: A string with the unit of the variable.
    :param visibility: a :class:`~alfasim_sdk.variables.Visibility` value.
    :param location: a :class:`~alfasim_sdk.variables.Location` value.
    :param multifield_scope: a :class:`~alfasim_sdk.variables.Scope`.
    :param default_value: Default value to be set.
    :param checked_on_gui_default: If the added variable has :class:`~alfasim_sdk.variables.Visibility` equal to ``Output``,
        it indicates that this variable will be exported as output by default.

    .. note::
        This type is supposed to be used in the :py:func:`~alfasim_sdk.hook_specs_gui.alfasim_get_additional_variables` `hook`.
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
