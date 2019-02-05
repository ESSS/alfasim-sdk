import numbers
from typing import Callable, List, Optional, Type, Union

import attr
from attr import attrib
from attr._make import Attribute
from attr.validators import instance_of, optional

from alfasim_sdk._validators import check_string_is_not_empty, check_unit_is_valid


@attr.s(kw_only=True)
class ALFAsimType:
    name = attrib(default="ALFAsim")


@attr.s(kw_only=True)
class TracerType(ALFAsimType):
    type = attrib(default="tracer")


@attr.s(kw_only=True)
class BaseField:
    """
    Base class for all widget fields available at ALFAsim.

    The BaseField class and all others classes that inheritance from BaseField must use kw_only=True
    for all attributes.
    This is due to the necessity to make enable_expr is an optional value and the
    only way to have properties with default values mixed with required properties is with
    key-word only arguments.
    """

    caption: str = attrib(validator=[instance_of(str), check_string_is_not_empty])
    enable_expr: Optional[Callable] = attrib(default=None)

    @enable_expr.validator
    def check(self, attr: Attribute, value: Optional[Callable]) -> None:
        if value is None:
            return

        if not callable(value):
            raise TypeError(f"enable_expr must be a function, got a {type(value)}.")


@attr.s(kw_only=True)
class String(BaseField):
    """
    The String represents an input that the user can provide a string text for the application.

    GUI Representation:
    On the GUI interface, the String represent an text input with a one-line text editor.

    Properties:
    caption - property used as a label for the text input.
    value   - property that holds the value informed from the user, or the default value that
              should be displayed for the user.


    """

    value: str = attrib(validator=[instance_of(str), check_string_is_not_empty])


@attr.s(kw_only=True)
class Enum(BaseField):
    values: List[str] = attrib()
    initial: str = attrib(validator=optional(instance_of(str)), default=None)

    @values.validator
    def check(self, attr: Attribute, values: List[str]) -> None:
        if not isinstance(values, list):
            raise TypeError(
                f"{attr.name} must be a list, got a '{type(values).__name__}'."
            )

        for value in values:
            if not isinstance(value, str):
                raise TypeError(
                    f"{attr.name} must be a list of strings, the item '{value}' is a '{type(value).__name__}'"
                )
            check_string_is_not_empty(self, attr, value)

        if self.initial is not None:
            if self.initial not in values:
                raise TypeError(
                    f"The initial condition must be within the declared values"
                )


@attr.s(kw_only=True)
class DataReference(BaseField):
    value = attrib()

    @value.validator
    def check(self, attr: Attribute, value: Type[ALFAsimType]) -> None:
        if not issubclass(value, ALFAsimType):
            raise TypeError(f"{attr.name} must be a valid ALFAsim type")


@attr.s(kw_only=True)
class Quantity(BaseField):
    value: numbers.Real = attrib(validator=instance_of(numbers.Real))
    unit: str = attrib(
        validator=[instance_of(str), check_string_is_not_empty, check_unit_is_valid]
    )


@attr.s(kw_only=True)
class TableColumn(BaseField):
    id: str = attrib(validator=[instance_of(str), check_string_is_not_empty])
    value: Quantity = attrib()
    caption = attrib(init=False, default="")

    def __attrs_post_init__(self) -> None:
        self.caption = self.value.caption

    @value.validator
    def check(self, attr: Attribute, values: Quantity) -> None:
        if not isinstance(values, Quantity):
            raise TypeError(f"{attr.name} must be a Quantity, got a {type(values)}.")


@attr.s(kw_only=True)
class Table(BaseField):
    rows: List[TableColumn] = attrib()

    @rows.validator
    def check(self, attr: Attribute, values: Union[List[str], str]):
        if not isinstance(values, list):
            raise TypeError(f"{attr.name} must be a list, got a {type(values)}.")

        if not values:
            raise TypeError(f"{attr.name} must be a list with TableColumn.")

        if not all(isinstance(value, TableColumn) for value in values):
            raise TypeError(f"{attr.name} must be a list of TableColumn.")


@attr.s(kw_only=True)
class Boolean(BaseField):
    value: bool = attrib(validator=instance_of(bool))
