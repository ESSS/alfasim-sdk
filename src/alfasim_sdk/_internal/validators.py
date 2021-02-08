from typing import Any

from attr._make import Attribute
from attr.validators import deep_iterable
from attr.validators import instance_of


def non_empty_str(self: Any, attribute: Attribute, value: str) -> None:
    """
    A validator that raises a ValueError if the initializer is called with a empty string '' or '  '
    """
    if not isinstance(value, str):
        raise TypeError(
            f"'{attribute.name}' must be 'str' (got {value} that is a '{type(value).__name__}')"
        )

    if not value or value.isspace():
        from alfasim_sdk._internal.types import Enum

        if isinstance(self, Enum):
            raise ValueError(
                f'Enum type cannot have an empty string on field "{attribute.name}"'
            )

        raise ValueError(f'The field "{attribute.name}" cannot be empty')


def valid_unit(self: Any, attribute: Attribute, value: str) -> None:
    """
    A validator that raises a ValueError if the initializer is called with a non-valid unit
    """
    from barril.units import UnitDatabase

    if UnitDatabase.GetSingleton().GetDefaultCategory(value) is None:
        raise ValueError(f"{value} is not a valid unit")


list_of_strings = deep_iterable(
    member_validator=instance_of(str), iterable_validator=instance_of(list)
)
