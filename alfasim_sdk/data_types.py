import numbers
from typing import List

import attr
from attr import attrib
from attr.validators import instance_of, optional


@attr.s
class BaseField:
    """
    Base class for all widget fields available at alfasim.
    """
    caption: str = attrib(validator=instance_of(str))


@attr.s
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
    value: str = attrib(validator=instance_of(str))


@attr.s
class Enum(BaseField):
    value: List[str] = attrib()
    initial: str = attrib(validator=optional(instance_of(str)), default=None)

    @value.validator
    def check(self, attr, values):
        if not isinstance(values, list):
            raise TypeError(f"{attr.name} must be a list, got a {type(values)}.")

        if not all(isinstance(value, str) for value in values):
            raise TypeError(f"{attr.name} must be a list of string.")

        if self.initial is not None:
            if self.initial not in values:
                raise TypeError(f"The initial condition must be within the declared values")


@attr.s
class DataReference(BaseField):
    value = attrib()

    @value.validator
    def check(self, attr, value):
        if not issubclass(value, AlfaSimType):
            raise TypeError(f"{attr.name} must be a valid ALFASim type")


@attr.s
class Quantity(BaseField):
    value: numbers.Real = attrib(validator=instance_of(numbers.Real))
    unit: str = attrib(validator=instance_of(str))


@attr.s
class TableColumn(BaseField):
    id: str = attrib(validator=instance_of(str))
    value: Quantity = attrib()
    caption = attrib(init=False, default='')

    def __attrs_post_init__(self):
        self.caption = self.value.caption

    @value.validator
    def check(self, attr, values):
        if not isinstance(values, Quantity):
            raise TypeError(f"{attr.name} must be a Quantity, got a {type(values)}.")


@attr.s
class Table(BaseField):
    rows: List[TableColumn] = attrib()

    @rows.validator
    def check(self, attr, values):
        if not isinstance(values, list):
            raise TypeError(f"{attr.name} must be a list, got a {type(values)}.")

        if not values:
            raise TypeError(f"{attr.name} must be a list with TableColumn.")

        if not all(isinstance(value, TableColumn) for value in values):
            raise TypeError(f"{attr.name} must be a list of TableColumn.")


@attr.s
class Boolean(BaseField):
    value: bool = attrib(validator=instance_of(bool))


@attr.s
class AlfaSimType:
    name = attrib(default='alfasim')


@attr.s
class TracerType(AlfaSimType):
    type = attrib(default='tracer')
