import sys
from typing import Any

import attr

from alfasim_sdk._internal.types import BaseField, Group, Tab, Tabs


def get_attr_class(
    class_: type,
    caption: str,
    icon: str | None,
    model: type | None,
    bases: tuple[type, ...] = (),
):
    attributes = get_all_attributes(class_)

    attr_class = attr.make_class(name=class_.__name__, attrs=attributes, bases=bases)
    attr_class.__qualname__ = class_.__qualname__
    attr_class.__module__ = class_.__module__
    attr_class._alfasim_metadata = {  # type:ignore[attr-defined]
        "caption": caption,
        "icon": icon,
        "model": model,
        "bases": bases,
    }

    return attr_class


def get_metadata(obj: Any) -> dict[str, Any]:
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


def get_all_attributes(class_: type) -> dict[str, Any]:
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


def get_required_sdk_version() -> str:
    """
    Returns a string with default alfasim-sdk version requirement for plugins.
    Default is greater or equal to current alfasim-sdk version.
    """
    return f">={get_current_version()}"


def get_required_python_version() -> str:
    """
    Return the required python version to be included in plugins metadata when using
    the CLI to generate a template.
    """
    # Assume most plugins will use compiled code and include an upper bound.
    major, minor, *_ = sys.version_info
    return f">={major}.{minor},<{major}.{minor + 1}"
