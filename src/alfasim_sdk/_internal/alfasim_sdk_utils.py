from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple

import attr

from alfasim_sdk._internal.types import BaseField
from alfasim_sdk._internal.types import Group
from alfasim_sdk._internal.types import Tab
from alfasim_sdk._internal.types import Tabs


def get_attr_class(
    class_: type,
    caption: str,
    icon: Optional[str],
    model: Optional[type],
    bases: Optional[Tuple] = (),
):
    attributes = get_all_attributes(class_)

    attr_class = attr.make_class(name=class_.__name__, attrs=attributes, bases=bases)
    attr_class.__qualname__ = class_.__qualname__
    attr_class.__module__ = class_.__module__
    attr_class._alfasim_metadata = {
        "caption": caption,
        "icon": icon,
        "model": model,
        "bases": bases,
    }

    return attr_class


def get_metadata(obj: Any) -> Dict[str, Any]:
    """
    Return the metadata associated with a class created by the SDK.
    """
    return obj._alfasim_metadata


def is_a_valid_field(value: type) -> bool:
    """
    A utility method to indicate if the given value is BaseField or a Tab layout
    """
    valid_field = False

    if isinstance(value, BaseField):
        valid_field = True

    if isinstance(value, type) and (issubclass(value, Tab) or issubclass(value, Tabs)):
        valid_field = True

    if isinstance(value, type) and issubclass(value, Group):
        valid_field = True

    return valid_field


def get_all_attributes(class_: type) -> Dict[str, Any]:
    """
    Return a dictionary with all attributes from the given class_ converted to an attr.Attribute, ignoring all "dunders"
    method and raising a TypeError to avoid attributes with a "_" at the beginning of the name
    """
    attributes = {}
    for key, value in vars(class_).items():
        if key.startswith("__"):
            continue

        if key.startswith("_"):
            raise TypeError(
                f"Error defining {key}, attributes starting with '_' are not allowed"
            )

        if not is_a_valid_field(value):
            raise TypeError(
                f"Error defining {key}, attributes must be a valid type defined by alfasim_sdk"
            )

        attributes[key] = attr.ib(default=value)

    return attributes


def get_current_version() -> str:
    """
    Checks current version of alfasim-sdk. Extracted to be easier to mock in tests.
    """
    import alfasim_sdk

    return alfasim_sdk.__version__


def get_extras_default_required_version() -> str:
    """
    :return:
        Returns a string with default alfasim-sdk version requirement for plugins. Default is
        greater or equal current version and lesser than next major release.
    """
    parts = get_current_version().split(".")
    current_major = parts[0]
    current_minor = ".".join(parts[:2])
    next_major = int(current_major) + 1
    return f">={current_minor}, <{next_major}"
