from typing import Any

from attr._make import Attribute


def check_string_is_not_empty(self: Any, attribute: Attribute, value: str) -> None:
    """
    A validator that raises a ValueError if the initializer is called with a empty string '' or '  '
    """
    if not value or value.isspace():
        from alfasim_sdk.types import Enum
        if type(self) is Enum:
            raise ValueError(f'Enum type cannot have an empty string on field "{attribute.name}"')

        raise ValueError(f'The field "{attribute.name}" cannot be empty')


def check_unit_is_valid(self: Any, attribute: Attribute, value: str) -> None:
    """
    A validator that raises a ValueError if the initializer is called with a non-valid unit
    """
    from barril.units import UnitDatabase
    if UnitDatabase.GetSingleton().GetDefaultCategory(value) is None:
        raise ValueError(f"{value} is not a valid unit")
