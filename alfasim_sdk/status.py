import attr
from attr import attrib

from alfasim_sdk._validators import check_string_is_not_empty


@attr.s(kw_only=True)
class ErrorMessage:
    model_name: str = attrib(validator=check_string_is_not_empty)
    message: str = attrib(validator=check_string_is_not_empty)


@attr.s(kw_only=True)
class WarningMessage:
    model_name: str = attrib(validator=check_string_is_not_empty)
    message: str = attrib(validator=check_string_is_not_empty)
