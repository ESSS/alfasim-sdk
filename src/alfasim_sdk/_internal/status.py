import attr
from attr import attrib

from alfasim_sdk._internal.validators import non_empty_str


@attr.s(kw_only=True)
class ErrorMessage:
    """
    ErrorMessage allows the plugin to display a message over the status monitor, and signalize to the application to block
    the simulation until the issue is fixed.

    :ivar model_name: Name of the model that issues the error.
    :ivar message: Message that will be displayed over the status monitor.

    Checkout the :func:`~alfasim_sdk._internal.hook_specs_gui.alfasim_get_status` for some examples of ```ErrorMessage``` in action.
    """

    model_name: str = attrib(validator=non_empty_str)
    message: str = attrib(validator=non_empty_str)


@attr.s(kw_only=True)
class WarningMessage:
    """
    WarningMessage allows the plugin to display a message to the user over the status monitor, and signalizes a minor
    issue that needs to be fixed but doesn't block the simulation.

    :ivar model_name: Name of the model that issues the warning.
    :ivar message: Message that will be displayed over the status monitor.

    Checkout the :func:`~alfasim_sdk._internal.hook_specs_gui.alfasim_get_status` for some examples of ```WarningMessage``` in action.
    """

    model_name: str = attrib(validator=non_empty_str)
    message: str = attrib(validator=non_empty_str)
