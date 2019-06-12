import attr
from attr import attrib

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
