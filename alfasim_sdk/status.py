import attr
from attr import attrib

from alfasim_sdk._validators import non_empty_str


@attr.s(kw_only=True)
class ErrorMessage:
    model_name: str = attrib(validator=non_empty_str)
    message: str = attrib(validator=non_empty_str)


@attr.s(kw_only=True)
class WarningMessage:
    model_name: str = attrib(validator=non_empty_str)
    message: str = attrib(validator=non_empty_str)
