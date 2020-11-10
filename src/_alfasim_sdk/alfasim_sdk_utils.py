from typing import Optional
from typing import Tuple

import attr

from _alfasim_sdk.types import BaseField
from _alfasim_sdk.types import Group
from _alfasim_sdk.types import Tab
from _alfasim_sdk.types import Tabs


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


def is_a_valid_field(value) -> bool:
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


def get_all_attributes(class_: type):
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


def get_current_version():
    """
    Checks current version of alfasim-sdk. Extracted to be easier to mock in tests.
    :return:
    """
    import alfasim_sdk

    return alfasim_sdk.__version__


def get_extras_default_required_version():
    """
    :rtype str:
    :return:
        Returns a string with default alfasim-sdk version requirement for plugins. Default is
        greater or equal current version and lesser than next major release.
    """
    parts = get_current_version().split(".")
    current_major = parts[0]
    current_minor = ".".join(parts[:2])
    next_major = int(current_major) + 1
    return f">={current_minor}, <{next_major}"
